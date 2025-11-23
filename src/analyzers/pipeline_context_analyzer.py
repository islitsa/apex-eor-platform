"""
Pipeline Context Analyzer - Scans petroleum data pipeline filesystem structure
Discovers data sources, datasets, and metrics dynamically from data/raw/ directory.

This is a domain-specific analyzer, not a generic utility.
It understands the petroleum data pipeline structure (sources/datasets/stages).
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class PipelineContextAnalyzer:
    """
    Analyzes petroleum data pipeline filesystem structure
    Scans data/raw/ to discover sources, datasets, and extract metrics
    """

    def __init__(self, data_root: str = None):
        if data_root is None:
            # Auto-detect project root
            current = Path(__file__).resolve()
            while current.parent != current:
                if (current / 'data').exists():
                    data_root = str(current / 'data')
                    break
                current = current.parent

        self.data_root = Path(data_root) if data_root else Path("data")
        self.raw_data_path = self.data_root / "raw"

    def generate_context_from_filesystem(self) -> Dict:
        """
        DEPRECATED: Use analyze_filesystem() instead
        Kept for backwards compatibility with existing code
        """
        import warnings
        warnings.warn(
            "generate_context_from_filesystem() is deprecated. Use analyze_filesystem() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.analyze_filesystem()

    def analyze_filesystem(self) -> Dict:
        """
        Analyze pipeline filesystem structure and extract context
        Scans data/raw/ to discover sources, datasets, stages, and metrics
        """
        context = {
            "screen_type": "pipeline_dashboard_multi_sor",
            "timestamp": datetime.now().isoformat(),
            "data_sources": {},
            "pipeline_info": {
                "stages": ["download", "extract", "parse"],
                "stage_descriptions": {
                    "download": "Fetch data from external sources",
                    "extract": "Uncompress and extract archives",
                    "parse": "Convert to structured formats (CSV/Parquet)"
                },
                "optional_stages": ["parse"],  # Parsing is optional if data is already in usable format
                "stage_notes": {
                    "parse": "Optional - only needed if extracted data is not already in CSV/Parquet format"
                }
            },
            "metrics": {
                "total_records": 0,
                "total_size_bytes": 0,
                "total_size_human": "",
                "active_sources": 0,
                "total_datasets": 0
            },
            "metadata_files": []  # For backward compatibility with existing patterns
        }

        # Scan for sources (top-level dirs in data/raw)
        sources = self.discover_sources()

        print(f"[AutoContext] Discovered {len(sources)} data sources")

        for source in sources:
            source_data = self.analyze_source(source)
            context["data_sources"][source.name] = source_data

            # Aggregate metrics from all datasets
            for dataset in source_data.get("datasets", {}).values():
                # Get parsed data metrics if available
                if "parsed" in dataset.get("pipeline_stages", {}):
                    parsed = dataset["pipeline_stages"]["parsed"]
                    records = parsed.get("total_rows", 0)
                    size_bytes = parsed.get("total_size_bytes", 0)

                    context["metrics"]["total_records"] += records
                    context["metrics"]["total_size_bytes"] += size_bytes

                    # Track metadata file if it exists
                    if dataset.get("metadata_file"):
                        context["metadata_files"].append(dataset["metadata_file"])

        context["metrics"]["active_sources"] = len(sources)
        context["metrics"]["total_datasets"] = sum(
            len(s.get("datasets", {}))
            for s in context["data_sources"].values()
        )

        # Convert total size to human readable
        context["metrics"]["total_size_human"] = self.format_file_size(
            context["metrics"]["total_size_bytes"]
        )

        print(f"[AutoContext] Total: {context['metrics']['total_records']:,} records, "
              f"{context['metrics']['total_size_human']}, "
              f"{context['metrics']['active_sources']} sources")

        return context

    def discover_sources(self) -> List[Path]:
        """
        Auto-discover data sources from filesystem
        NO HARDCODING - discovers all sources dynamically
        """
        sources = []

        if not self.raw_data_path.exists():
            print(f"[AutoContext] WARNING: {self.raw_data_path} does not exist")
            return sources

        # Known source patterns (for prioritization and naming)
        known_sources = {
            "rrc": "Railroad Commission of Texas",
            "fracfocus": "FracFocus Chemical Registry",
            "netl edx": "NETL EDX",
            "twdb": "Texas Water Development Board",
            "usgs": "US Geological Survey",
            "onepetro": "OnePetro"
        }

        for item in self.raw_data_path.iterdir():
            if item.is_dir():
                # Check if it's a known source or looks like a data source
                source_name_lower = item.name.lower()

                # Skip obvious non-source directories
                if source_name_lower in ['.git', '__pycache__', 'temp', 'tmp']:
                    continue

                # Check if it's a known source or has datasets inside
                is_known_source = source_name_lower in known_sources
                has_subdirs = any(sub.is_dir() for sub in item.iterdir())

                if is_known_source or has_subdirs:
                    sources.append(item)
                    print(f"[AutoContext]   Found source: {item.name}")

        return sources

    def analyze_source(self, source_path: Path) -> Dict:
        """
        Analyze a data source directory
        """
        source_data = {
            "name": source_path.name,
            "display_name": self.humanize_name(source_path.name),
            "type": "source_of_record",
            "status": "active",
            "datasets": {},
            "pipeline_stages_used": [],  # Which stages exist
            "processing_notes": {}  # Notes about processing (e.g., extraction was trivial)
        }

        # Find datasets within source
        # Datasets can be direct subdirs or metadata.json files
        for item in source_path.iterdir():
            if item.is_dir():
                # It's a dataset directory
                dataset_info = self.analyze_dataset(item)
                if dataset_info:  # Only add if we found actual data
                    source_data["datasets"][item.name] = dataset_info

                    # Use EXPLICIT data from metadata - whatever metadata says (NO INTERPRETATION)
                    metadata = dataset_info.get('metadata', {})
                    proc_state = metadata.get('processing_state', {})

                    # Show whatever metadata explicitly says completed
                    if proc_state.get('download') == 'complete':
                        if 'downloads' not in source_data['pipeline_stages_used']:
                            source_data['pipeline_stages_used'].append('downloads')

                    if proc_state.get('extraction') == 'complete':
                        if 'extracted' not in source_data['pipeline_stages_used']:
                            source_data['pipeline_stages_used'].append('extracted')

                    if proc_state.get('parsing') == 'complete':
                        if 'parsed' not in source_data['pipeline_stages_used']:
                            source_data['pipeline_stages_used'].append('parsed')

                    # Pass through notes as-is
                    if proc_state.get('parsing_note'):
                        source_data['processing_notes']['parsing_note'] = proc_state['parsing_note']

            elif item.name == "metadata.json":
                # Source-level metadata
                source_data["metadata"] = self.read_metadata(item)

        return source_data

    def analyze_dataset(self, dataset_path: Path) -> Dict:
        """
        Analyze a dataset directory - AUTO-DETECT everything
        """
        dataset = {
            "name": dataset_path.name,
            "display_name": self.humanize_name(dataset_path.name),
            "status": "unknown",
            "pipeline_stages": {},
            "metadata": {},
            "actions_available": [],
            "metadata_file": None
        }

        # Check for metadata.json first
        metadata_path = dataset_path / "metadata.json"
        if metadata_path.exists():
            dataset["metadata"] = self.read_metadata(metadata_path)
            dataset["metadata_file"] = str(metadata_path)
            dataset["actions_available"].append("view_metadata")

            # Extract key info from metadata if available
            if "parsed" in dataset["metadata"]:
                dataset["pipeline_stages"]["parsed"] = dataset["metadata"]["parsed"]
                dataset["status"] = dataset["metadata"]["parsed"].get("status", "unknown")

        # Check for pipeline stages directories
        stages = ["downloads", "extracted", "parsed"]

        for stage in stages:
            stage_path = dataset_path / stage
            if stage_path.exists() and stage_path.is_dir():
                # Only analyze if we don't already have info from metadata
                if stage not in dataset["pipeline_stages"]:
                    stage_info = self.analyze_stage(stage_path)
                    dataset["pipeline_stages"][stage] = stage_info

                # Update dataset status based on stages
                if stage == "parsed" and dataset["pipeline_stages"]["parsed"].get("status") == "complete":
                    dataset["status"] = "ready"

        # Determine available actions
        if dataset["status"] == "ready":
            dataset["actions_available"].extend(["view", "download", "re-run"])

        # Only return dataset if it has some actual content
        if dataset["pipeline_stages"] or dataset["metadata"]:
            return dataset
        else:
            return None

    def analyze_stage(self, stage_path: Path) -> Dict:
        """
        Analyze a pipeline stage directory
        """
        stage_info = {
            "status": "empty",
            "path": str(stage_path),
            "timestamp": datetime.fromtimestamp(stage_path.stat().st_mtime).isoformat()
        }

        # Count files and calculate size
        try:
            files = list(stage_path.glob("**/*"))
            file_list = [f for f in files if f.is_file()]

            if file_list:
                stage_info["status"] = "complete"
                stage_info["files"] = len(file_list)
                stage_info["size_bytes"] = sum(f.stat().st_size for f in file_list)
                stage_info["size_human"] = self.format_file_size(stage_info["size_bytes"])
        except Exception as e:
            print(f"[AutoContext] Warning: Could not analyze {stage_path}: {e}")

        return stage_info

    def read_metadata(self, metadata_path: Path) -> Dict:
        """
        Read and parse metadata.json
        """
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            return metadata

        except Exception as e:
            print(f"[AutoContext] Warning: Could not parse {metadata_path}: {e}")
            return {"error": str(e)}

    def humanize_name(self, name: str) -> str:
        """
        Convert technical names to display names
        """
        replacements = {
            "rrc": "RRC",
            "_": " ",
            "completions_data": "Completions",
            "horizontal_drilling_permits": "Horizontal Permits",
            "fracfocus": "FracFocus",
            "netl edx": "NETL EDX",
            "twdb": "TWDB",
            "usgs": "USGS",
            "onepetro": "OnePetro"
        }

        display = name
        for old, new in replacements.items():
            display = display.replace(old, new)

        # Title case
        return display.title()

    def format_file_size(self, size_bytes: int) -> str:
        """
        Convert bytes to human-readable format
        """
        if size_bytes == 0:
            return "0 B"

        units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0
        size = float(size_bytes)

        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1

        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        else:
            return f"{size:.2f} {units[unit_index]}"


# For backwards compatibility - keep old name as alias
AutoContextGenerator = PipelineContextAnalyzer


def main():
    """
    Test the pipeline context analyzer
    """
    print("="*70)
    print("PIPELINE CONTEXT ANALYZER TEST")
    print("="*70)

    analyzer = PipelineContextAnalyzer()
    context = analyzer.analyze_filesystem()

    print("\n" + "="*70)
    print("GENERATED CONTEXT")
    print("="*70)
    print(json.dumps(context, indent=2))

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total Records: {context['metrics']['total_records']:,}")
    print(f"Total Size: {context['metrics']['total_size_human']}")
    print(f"Active Sources: {context['metrics']['active_sources']}")
    print(f"Total Datasets: {context['metrics']['total_datasets']}")
    print(f"Metadata Files: {len(context['metadata_files'])}")


if __name__ == "__main__":
    main()
