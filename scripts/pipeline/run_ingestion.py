"""
Data Ingestion Pipeline Runner

Main orchestration script for the complete data ingestion pipeline.

Runs three main phases:
1. DOWNLOAD - Fetch data from external sources
2. EXTRACT - Uncompress and extract archives
3. PARSE - Convert to structured formats (CSV/Parquet)

Usage:
    # Run all phases for all datasets
    python scripts/pipeline/run_ingestion.py --all

    # Run specific phases
    python scripts/pipeline/run_ingestion.py --download --extract --parse

    # Run for specific datasets
    python scripts/pipeline/run_ingestion.py --datasets rrc_production fracfocus

    # Force re-download
    python scripts/pipeline/run_ingestion.py --download --force

    # Generate context for UI tools
    python scripts/pipeline/run_ingestion.py --generate-context

    # Dry run (show what would be done)
    python scripts/pipeline/run_ingestion.py --all --dry-run
"""

import argparse
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Dict, Optional

# Load environment variables FIRST before any other imports
load_dotenv()

# Add parent directory to path
SCRIPTS_DIR = Path(__file__).parent.parent
PROJECT_ROOT = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

from downloaders.rrc_downloader import RRCDownloader
from downloaders.fracfocus_downloader import FracFocusDownloader
from pipeline.extract import ExtractionOrchestrator
from pipeline.parse import ParsingOrchestrator
from shared_state import PipelineState


class IngestionPipeline:
    """Main data ingestion pipeline orchestrator"""

    # Data layer directories to scan (extendable to interim, processed, external)
    DATA_LAYERS = ['raw']  # TODO: Add 'interim', 'processed', 'external' in future

    def __init__(self, base_data_dir: str = 'data/raw', dry_run: bool = False):
        """
        Initialize ingestion pipeline

        Args:
            base_data_dir: Base directory for raw data
            dry_run: If True, only show what would be done
        """
        self.base_data_dir = Path(base_data_dir)
        self.dry_run = dry_run

        # Initialize components
        self.rrc_downloader = RRCDownloader(str(self.base_data_dir / 'rrc'))
        self.fracfocus_downloader = FracFocusDownloader(str(self.base_data_dir / 'fracfocus'))
        self.extractor = ExtractionOrchestrator(str(self.base_data_dir))
        self.parser = ParsingOrchestrator(str(self.base_data_dir))

        self.results = {
            'download': {},
            'extract': {},
            'parse': {}
        }

    def discover_datasets(self, include_unprocessed: bool = True) -> List[Dict[str, str]]:
        """
        Dynamically discover all datasets by scanning directories

        Args:
            include_unprocessed: If True, include directories without metadata.json

        Returns:
            List of dicts with 'name', 'path', and 'has_metadata' for each dataset
        """
        discovered = []
        seen_paths = set()

        if not self.base_data_dir.exists():
            return discovered

        # First, find all directories with metadata.json files
        for metadata_file in self.base_data_dir.rglob('metadata.json'):
            dataset_dir = metadata_file.parent
            relative_path = dataset_dir.relative_to(self.base_data_dir)

            # Create logical name from path
            # e.g., "rrc/production" -> "rrc_production"
            # e.g., "NETL EDX" -> "netl_edx"
            name_parts = list(relative_path.parts)
            logical_name = '_'.join(name_parts).lower().replace(' ', '_')

            discovered.append({
                'name': logical_name,
                'display_name': ' / '.join(name_parts),
                'path': str(dataset_dir),
                'metadata_path': str(metadata_file),
                'has_metadata': True,
                'status': 'processed'
            })
            seen_paths.add(str(dataset_dir))

        # If requested, also include top-level directories without metadata
        if include_unprocessed:
            for item in self.base_data_dir.iterdir():
                if item.is_dir() and str(item) not in seen_paths:
                    # Check if it's not a hidden/system directory
                    if not item.name.startswith('.') and not item.name.startswith('__'):
                        logical_name = item.name.lower().replace(' ', '_')

                        discovered.append({
                            'name': logical_name,
                            'display_name': item.name,
                            'path': str(item),
                            'metadata_path': None,
                            'has_metadata': False,
                            'status': 'not_processed'
                        })

        return discovered

    def scan_directory_structure(self, dataset_path: Path, max_depth: int = 4, max_files_per_dir: int = 50) -> Dict:
        """
        Dynamically scan directory structure for a dataset

        Args:
            dataset_path: Path to dataset directory
            max_depth: Maximum depth to scan (prevent huge trees)
            max_files_per_dir: Maximum files to list per directory

        Returns:
            Dictionary representing directory tree with files
        """
        def scan_dir(path: Path, current_depth: int = 0) -> Dict:
            if current_depth >= max_depth:
                return {'_truncated': True}

            result = {
                'type': 'directory',
                'name': path.name,
                'path': str(path.relative_to(dataset_path)),
                'subdirs': {},
                'files': []
            }

            try:
                items = list(path.iterdir())

                # Separate dirs and files
                dirs = [item for item in items if item.is_dir() and not item.name.startswith('.')]
                files = [item for item in items if item.is_file() and not item.name.startswith('.')]

                # Scan subdirectories
                for subdir in sorted(dirs):
                    result['subdirs'][subdir.name] = scan_dir(subdir, current_depth + 1)

                # List files (with size info)
                file_list = []
                for i, file in enumerate(sorted(files)):
                    if i >= max_files_per_dir:
                        file_list.append({
                            '_truncated': True,
                            '_message': f'... and {len(files) - max_files_per_dir} more files'
                        })
                        break

                    try:
                        file_size = file.stat().st_size
                        file_list.append({
                            'name': file.name,
                            'size_bytes': file_size,
                            'size_human': self._format_bytes(file_size),
                            'extension': file.suffix
                        })
                    except:
                        file_list.append({'name': file.name, 'error': 'could not stat'})

                result['files'] = file_list
                result['file_count'] = len(files)
                result['dir_count'] = len(dirs)

            except PermissionError:
                result['error'] = 'Permission denied'
            except Exception as e:
                result['error'] = str(e)

            return result

        if not dataset_path.exists():
            return {'error': 'Path does not exist'}

        return scan_dir(dataset_path)

    def run_download(self, datasets: Optional[List[str]] = None, force: bool = False) -> Dict[str, bool]:
        """
        Run download phase

        Args:
            datasets: List of datasets to download (None = all)
            force: Force re-download even if files exist

        Returns:
            Dictionary with download results
        """
        print("\n" + "="*70)
        print("PHASE 1: DOWNLOAD")
        print("="*70)

        if self.dry_run:
            print("[DRY RUN] Would download the following datasets:")
            discovered = [d['name'] for d in self.discover_datasets()]
            for dataset in (datasets or discovered):
                print(f"  - {dataset}")
            return {}

        results = {}

        # Determine which datasets to download
        download_all = datasets is None or len(datasets) == 0

        # RRC Production
        if download_all or 'rrc_production' in datasets:
            print("\n--- Downloading RRC Production ---")
            results['rrc_production'] = self.rrc_downloader.download_production(force)

        # RRC Permits
        if download_all or 'rrc_permits' in datasets:
            print("\n--- Downloading RRC Permits ---")
            results['rrc_permits'] = self.rrc_downloader.download_permits(force)

        # RRC Completions
        if download_all or 'rrc_completions' in datasets:
            print("\n--- Downloading RRC Completions ---")
            results['rrc_completions'] = self.rrc_downloader.download_completions(force)

        # FracFocus
        if download_all or 'fracfocus' in datasets:
            print("\n--- Downloading FracFocus ---")
            results['fracfocus'] = self.fracfocus_downloader.download_csv_bulk(force)

        self.results['download'] = results
        return results

    def run_extract(self, datasets: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Run extraction phase

        Args:
            datasets: List of datasets to extract (None = all)

        Returns:
            Dictionary with extraction results
        """
        print("\n" + "="*70)
        print("PHASE 2: EXTRACT")
        print("="*70)

        if self.dry_run:
            print("[DRY RUN] Would extract the following datasets:")
            discovered = [d['name'] for d in self.discover_datasets()]
            for dataset in (datasets or discovered):
                print(f"  - {dataset}")
            return {}

        results = {}

        # Determine which datasets to extract
        extract_all = datasets is None or len(datasets) == 0

        # RRC Production
        if extract_all or 'rrc_production' in datasets:
            print("\n--- Extracting RRC Production ---")
            results['rrc_production'] = self.extractor.extract_rrc_production()

        # RRC Permits
        if extract_all or 'rrc_permits' in datasets:
            print("\n--- Extracting RRC Permits ---")
            results['rrc_permits'] = self.extractor.extract_rrc_permits()

        # RRC Completions
        if extract_all or 'rrc_completions' in datasets:
            print("\n--- Extracting RRC Completions ---")
            results['rrc_completions'] = self.extractor.extract_rrc_completions()

        # FracFocus
        if extract_all or 'fracfocus' in datasets:
            print("\n--- Extracting FracFocus ---")
            results['fracfocus'] = self.extractor.extract_fracfocus()

        self.results['extract'] = results
        return results

    def run_parse(self, datasets: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Run parsing phase

        Args:
            datasets: List of datasets to parse (None = all)

        Returns:
            Dictionary with parsing results
        """
        print("\n" + "="*70)
        print("PHASE 3: PARSE")
        print("="*70)

        if self.dry_run:
            print("[DRY RUN] Would parse the following datasets:")
            discovered = [d['name'] for d in self.discover_datasets()]
            for dataset in (datasets or discovered):
                print(f"  - {dataset}")
            return {}

        results = {}

        # Determine which datasets to parse
        parse_all = datasets is None or len(datasets) == 0

        # RRC Production
        if parse_all or 'rrc_production' in datasets:
            print("\n--- Parsing RRC Production ---")
            results['rrc_production'] = self.parser.parse_rrc_production()

        # RRC Permits
        if parse_all or 'rrc_permits' in datasets:
            print("\n--- Parsing RRC Permits ---")
            results['rrc_permits'] = self.parser.parse_rrc_permits()

        # RRC Completions
        if parse_all or 'rrc_completions' in datasets:
            print("\n--- Parsing RRC Completions ---")
            results['rrc_completions'] = self.parser.parse_rrc_completions()

        # FracFocus
        if parse_all or 'fracfocus' in datasets:
            print("\n--- Parsing FracFocus ---")
            results['fracfocus'] = self.parser.parse_fracfocus()

        self.results['parse'] = results
        return results

    def run_all(self, datasets: Optional[List[str]] = None, force: bool = False,
                launch_ui: Optional[str] = None) -> Dict[str, Dict[str, bool]]:
        """
        Run all pipeline phases

        Args:
            datasets: List of datasets to process (None = all)
            force: Force re-download even if files exist
            launch_ui: UI tool to launch after completion ('studio', 'runner', 'interface', or None)

        Returns:
            Dictionary with all results
        """
        print("\n" + "="*70)
        print("COMPLETE DATA INGESTION PIPELINE")
        print("="*70)
        print(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Phases: Download -> Extract -> Parse")
        if datasets:
            print(f"Datasets: {', '.join(datasets)}")
        else:
            print("Datasets: ALL")
        if launch_ui:
            print(f"UI Launch: {launch_ui} (after completion)")
        print("="*70)

        # Run all phases
        download_results = self.run_download(datasets, force)
        extract_results = self.run_extract(datasets)
        parse_results = self.run_parse(datasets)

        # Print summary
        print("\n" + "="*70)
        print("PIPELINE COMPLETE")
        print("="*70)

        total_success = 0
        total_failed = 0

        for phase, results in [('Download', download_results),
                               ('Extract', extract_results),
                               ('Parse', parse_results)]:
            success = sum(1 for v in results.values() if v)
            failed = len(results) - success
            total_success += success
            total_failed += failed
            print(f"{phase}: {success} succeeded, {failed} failed")

        print("-"*70)
        print(f"Total: {total_success} succeeded, {total_failed} failed")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)

        # Generate and save context after successful pipeline run
        if total_success > 0:
            self.generate_and_save_context()

            # Auto-launch UI if requested
            if launch_ui:
                self.launch_ui_tool(launch_ui)

        return {
            'download': download_results,
            'extract': extract_results,
            'parse': parse_results
        }

    def generate_context(self) -> Dict:
        """
        Generate rich context from pipeline state

        Returns:
            Context dictionary with all pipeline information
        """
        # Dynamically discover all datasets
        discovered_datasets = self.discover_datasets()

        context = {
            'timestamp': datetime.now().isoformat(),
            'pipeline_version': '2.0',
            'base_data_dir': str(self.base_data_dir),
            'data_sources': {},
            'pipeline_status': {
                'download': self.results.get('download', {}),
                'extract': self.results.get('extract', {}),
                'parse': self.results.get('parse', {})
            },
            'statistics': {
                'total_datasets': len(discovered_datasets),
                'processed_datasets': 0,
                'total_records': 0,
                'total_size_bytes': 0
            }
        }

        # Add metadata from each discovered dataset
        for dataset_info in discovered_datasets:
            dataset_name = dataset_info['name']
            dataset_path = Path(dataset_info['path'])

            # Scan directory structure for this dataset
            print(f"Scanning directory structure for {dataset_name}...")
            directory_structure = self.scan_directory_structure(dataset_path)

            # Check if dataset has been processed
            if not dataset_info['has_metadata']:
                # Dataset exists but has no metadata - not yet processed
                context['data_sources'][dataset_name] = {
                    'status': 'not_processed',
                    'display_name': dataset_info['display_name'],
                    'path': dataset_info['path'],
                    'processing_state': {
                        'download': 'not_started',
                        'extract': 'not_started',
                        'parsing': 'not_started'
                    },
                    'directory_structure': directory_structure
                }
                continue

            # Dataset has metadata - load it
            metadata_path = Path(dataset_info['metadata_path'])
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)

                    # Add display name, status, and directory structure to metadata
                    metadata['display_name'] = dataset_info['display_name']
                    metadata['path'] = dataset_info['path']
                    metadata['status'] = dataset_info['status']
                    metadata['directory_structure'] = directory_structure

                    context['data_sources'][dataset_name] = metadata

                    # Update statistics
                    context['statistics']['processed_datasets'] += 1
                    if 'parsed' in metadata:
                        context['statistics']['total_records'] += metadata['parsed'].get('total_rows', 0)
                        context['statistics']['total_size_bytes'] += metadata['parsed'].get('total_size_bytes', 0)
            except Exception as e:
                print(f"Warning: Could not load metadata for {dataset_name}: {e}")
                context['data_sources'][dataset_name] = {
                    'error': str(e),
                    'status': 'error',
                    'display_name': dataset_info['display_name'],
                    'path': dataset_info['path']
                }

        # Add helpful summary
        context['summary'] = {
            'datasets_available': len([d for d, m in context['data_sources'].items() if 'error' not in m]),
            'datasets_with_errors': len([d for d, m in context['data_sources'].items() if 'error' in m]),
            'human_readable_size': self._format_bytes(context['statistics']['total_size_bytes']),
            'human_readable_records': f"{context['statistics']['total_records']:,}"
        }

        # Generate initial UI prompt from pipeline status
        status_lines = []
        for ds_name, ds_info in context['data_sources'].items():
            if 'error' in ds_info:
                continue

            # Check if dataset has been processed
            if ds_info.get('status') == 'not_processed':
                status_lines.append(
                    f"  - {ds_info['display_name']}: NOT PROCESSED YET (no data ingested)"
                )
                continue

            # Dataset has been processed - show details
            proc_state = ds_info.get('processing_state', {})
            parsed_info = ds_info.get('parsed', {}) or ds_info.get('parsing_results', {})
            file_count = parsed_info.get('total_files', 0)
            record_count = parsed_info.get('total_records', parsed_info.get('total_rows', 0))

            status_lines.append(
                f"  - {ds_info.get('display_name', ds_name)}: {proc_state.get('download', 'unknown')} download, "
                f"{proc_state.get('parsing', 'unknown')} parsing → "
                f"{file_count} files, {record_count:,} records"
            )

        context['initial_prompt'] = f"""Design a pipeline monitoring dashboard that shows:

**Pipeline Status Overview:**
{chr(10).join(status_lines)}

**Data Requirements:**
- Show processing stage status for each dataset (download → extract → parse → validate → load)
- Display file counts, record counts, and data sizes
- Highlight any errors or warnings in the pipeline
- Show last update timestamps
- Make it easy to see what's complete vs in-progress vs failed
- Include data quality metrics where available
- Professional, clean layout - this is for monitoring ETL pipeline health

**UX/Interaction Requirements - CRITICAL:**
Each dataset has a hierarchical directory structure (e.g., rrc/production/downloads, rrc/production/extracted, rrc/production/parsed).
Users need to EXPLORE this structure interactively:

1. **Expandable/Collapsible Datasets**: Make each dataset name clickable/expandable to reveal its subdirectories
2. **Drill-Down Navigation**: When user clicks on a dataset (e.g., "rrc / production"), show its folders (downloads/, extracted/, parsed/)
3. **File Browser**: When user expands "parsed/" folder, show the actual CSV files with names and sizes
4. **File Preview**: When user clicks on a CSV file, show:
   - File metadata (size, row count, columns)
   - Column names and data types
   - Sample of first few rows
5. **Breadcrumb Navigation**: Show current location (e.g., rrc / production / parsed / 260663.csv) with back navigation
6. **Search/Filter**: Allow users to search across all datasets and files
7. **Tree View**: Use a collapsible tree structure (like file explorer) for intuitive navigation

The full directory structure and file listings are available in context['data_sources'][dataset_name]['directory_structure'].
Use this data to create an interactive, explorable UI - NOT just a static list!

Total: {len(context['data_sources'])} datasets, {context['summary']['human_readable_records']} records processed"""

        return context

    def generate_and_save_context(self):
        """Generate context and save using shared state manager"""
        print("\n--- Generating Pipeline Context ---")
        context = self.generate_context()

        # Save using shared state manager
        PipelineState.save_context(context)

        # Print summary
        print(f"[OK] Context saved with {context['summary']['datasets_available']} datasets")
        print(f"   Total records: {context['summary']['human_readable_records']}")
        print(f"   Total size: {context['summary']['human_readable_size']}")
        print("\nTo launch UI with this context, run:")
        print("  python launch.py ui studio")
        print("  python launch.py ui runner")
        print("  python launch.py ui interface")

    def launch_ui_tool(self, tool: str):
        """
        Launch UI tool after pipeline completion

        Args:
            tool: UI tool to launch ('studio', 'runner', 'interface')
        """
        import subprocess
        import time

        print("\n" + "="*70)
        print("LAUNCHING UI DASHBOARD GENERATOR")
        print("="*70)

        scripts = {
            'studio': 'agent_studio.py',  # Real agents with Pinecone, CoT, planning + nice UI
            'runner': 'agent_chat_runner.py',
            'interface': 'agent_chat_interface.py',
            'collaborate': 'agent_studio.py'  # Launch Agent Studio with real agents + nice UI
        }

        if tool not in scripts:
            print(f"Unknown UI tool: {tool}")
            print(f"Available: {', '.join(scripts.keys())}")
            return

        script_name = scripts[tool]

        # Try different possible locations
        possible_paths = [
            PROJECT_ROOT / 'src' / 'ui' / script_name,
            PROJECT_ROOT / 'scripts' / 'ui' / script_name,
            PROJECT_ROOT / script_name,
        ]

        script_path = None
        for path in possible_paths:
            if path.exists():
                script_path = path
                break

        if not script_path:
            print(f"[ERROR] Could not find {script_name}")
            print(f"   Searched in: {', '.join(str(p.parent) for p in possible_paths)}")
            return

        print(f"Launching: {tool}")
        print(f"Script: {script_path}")
        print(f"URL: http://localhost:8501")
        print("="*70)
        print("\nOpening dashboard in 3 seconds...")
        time.sleep(3)

        # Launch with streamlit
        try:
            subprocess.Popen(['streamlit', 'run', str(script_path)])
            print("[OK] UI launched successfully!")
            print("   Press Ctrl+C to stop the dashboard")
        except Exception as e:
            print(f"[ERROR] Error launching UI: {e}")
            print(f"   You can manually run: streamlit run {script_path}")

    def _format_bytes(self, bytes: int) -> str:
        """Format bytes to human readable string"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024.0:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.2f} PB"


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Data Ingestion Pipeline for APEX EOR Platform',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete pipeline for all datasets
  python run_ingestion.py --all

  # Run pipeline and auto-launch UI
  python run_ingestion.py --all --launch-ui runner

  # Run only download and extract phases
  python run_ingestion.py --download --extract

  # Run for specific datasets
  python run_ingestion.py --all --datasets rrc_production fracfocus

  # Force re-download
  python run_ingestion.py --download --force

  # Generate context for UI tools (no data reload)
  python run_ingestion.py --generate-context

  # Generate context and auto-launch UI (no data reload)
  python run_ingestion.py --generate-context --launch-ui runner

  # Launch collaborative multi-agent system (RECOMMENDED for best results)
  python run_ingestion.py --generate-context --launch-ui collaborate

  # Dry run to see what would be done
  python run_ingestion.py --all --dry-run
        """
    )

    # Phase selection
    parser.add_argument('--all', action='store_true',
                        help='Run all phases (download, extract, parse)')
    parser.add_argument('--download', action='store_true',
                        help='Run download phase')
    parser.add_argument('--extract', action='store_true',
                        help='Run extract phase')
    parser.add_argument('--parse', action='store_true',
                        help='Run parse phase')
    parser.add_argument('--generate-context', action='store_true',
                        help='Generate context for UI tools')

    # Dataset selection
    parser.add_argument('--datasets', nargs='+',
                        help='Specific datasets to process (default: all discovered datasets)')

    # Options
    parser.add_argument('--force', action='store_true',
                        help='Force re-download even if files exist')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without executing')
    parser.add_argument('--base-dir', default='data/raw',
                        help='Base directory for raw data (default: data/raw)')

    # UI launching option
    parser.add_argument('--launch-ui', choices=['studio', 'runner', 'interface', 'collaborate'],
                        help='Auto-launch UI tool after pipeline completion (collaborate=multi-agent system)')

    args = parser.parse_args()

    # Initialize pipeline
    pipeline = IngestionPipeline(
        base_data_dir=args.base_dir,
        dry_run=args.dry_run
    )

    # Handle context generation
    if args.generate_context:
        pipeline.generate_and_save_context()

        # Launch UI if requested after context generation
        if args.launch_ui:
            pipeline.launch_ui_tool(args.launch_ui)
        return

    # Validate arguments
    if not (args.all or args.download or args.extract or args.parse):
        parser.error('Must specify at least one phase: --all, --download, --extract, --parse, or --generate-context')

    # Run requested phases
    if args.all:
        pipeline.run_all(args.datasets, args.force, launch_ui=args.launch_ui)
    else:
        if args.download:
            pipeline.run_download(args.datasets, args.force)
        if args.extract:
            pipeline.run_extract(args.datasets)
        if args.parse:
            pipeline.run_parse(args.datasets)

        # Generate context after individual phase runs
        pipeline.generate_and_save_context()

        # Launch UI if requested (even for partial runs)
        if args.launch_ui:
            pipeline.launch_ui_tool(args.launch_ui)


if __name__ == '__main__':
    main()
