"""
Repository Indexer for Context Swimming

Indexes data sources, schemas, and file structures to enable autonomous agent discovery.
Agents can query "what data exists" instead of being manually told.
"""

import os
import json
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.knowledge.design_kb_pinecone import DesignKnowledgeBasePinecone


class RepositoryIndex:
    """
    Index repository artifacts (data sources, schemas, files) for agent discovery

    Context Swimming Architecture:
    - Agents query index to discover what exists
    - No manual configuration of data sources
    - Adapts automatically as data changes
    """

    def __init__(
        self,
        index_name: str = "gradio-design-kb",  # Reuse existing index
        namespace: str = "repo-artifacts"  # New namespace for artifacts
    ):
        """
        Initialize repository indexer

        Args:
            index_name: Pinecone index name (reuse design KB index)
            namespace: Namespace for repo artifacts (separate from design guidelines)
        """
        self.kb = DesignKnowledgeBasePinecone(
            index_name=index_name,
            namespace=namespace
        )
        self.namespace = namespace

    def index_data_directory(self, data_root: Path) -> Dict[str, Any]:
        """
        Index entire /data directory structure

        Discovers:
        - Data sources (fracfocus, rrc, NETL EDX, etc.)
        - Subdirectories (Chemical_data, production, completions, etc.)
        - File counts, sizes, types
        - Processing status (raw, processed, parsed)

        Args:
            data_root: Path to /data directory

        Returns:
            Index statistics
        """
        data_root = Path(data_root)
        stats = {
            'sources_indexed': 0,
            'subdirectories_indexed': 0,
            'files_analyzed': 0
        }

        print(f"[INDEXING] Repository: {data_root}")

        # Find top-level data sources
        if (data_root / 'raw').exists():
            raw_dir = data_root / 'raw'
            for source_dir in raw_dir.iterdir():
                if source_dir.is_dir():
                    print(f"\n[SOURCE] Indexing data source: {source_dir.name}")
                    source_stats = self._index_data_source(source_dir)
                    stats['sources_indexed'] += 1
                    stats['subdirectories_indexed'] += source_stats['subdirs']
                    stats['files_analyzed'] += source_stats['files']

        print(f"\n[COMPLETE] Indexing complete:")
        print(f"   - Data sources: {stats['sources_indexed']}")
        print(f"   - Subdirectories: {stats['subdirectories_indexed']}")
        print(f"   - Files analyzed: {stats['files_analyzed']}")

        return stats

    def _index_data_source(self, source_path: Path) -> Dict[str, int]:
        """
        Index a single data source (e.g., fracfocus/, rrc/)

        Args:
            source_path: Path to data source directory

        Returns:
            Statistics about indexed content
        """
        stats = {'subdirs': 0, 'files': 0}

        # Analyze directory structure
        metadata = self._analyze_directory(source_path)
        stats['subdirs'] = metadata['subdirectory_count']
        stats['files'] = metadata['file_count']

        # Create searchable content for this data source
        content = self._create_data_source_content(source_path, metadata)

        # Index in Pinecone
        self.kb.add_guideline(
            guideline_id=f"data-source-{source_path.name}",
            title=f"Data Source: {source_path.name}",
            content=content,
            category="data-source",
            metadata={
                'type': 'data-source',
                'path': str(source_path),
                'name': source_path.name,
                'subdirectories': list(metadata['subdirectories'].keys()),
                'file_count': metadata['file_count'],
                'total_size_mb': metadata['total_size_mb'],
                'processing_stages': metadata['stages'],
                'last_modified': metadata['last_modified'] or 'unknown',  # Pinecone doesn't accept None
                'has_downloads': metadata['has_downloads'],
                'has_extracted': metadata['has_extracted'],
                'has_parsed': metadata['has_parsed']
            }
        )

        # Also index major subdirectories
        for subdir_name, subdir_info in metadata['subdirectories'].items():
            if subdir_info['file_count'] > 0:  # Only index non-empty
                self._index_subdirectory(
                    source_name=source_path.name,
                    subdir_name=subdir_name,
                    subdir_info=subdir_info
                )

        return stats

    def _index_subdirectory(
        self,
        source_name: str,
        subdir_name: str,
        subdir_info: Dict[str, Any]
    ):
        """Index a subdirectory (e.g., fracfocus/Chemical_data)"""

        content = f"""
Subdirectory: {source_name}/{subdir_name}
Parent Source: {source_name}
Files: {subdir_info['file_count']}
Size: {subdir_info['size_mb']:.1f} MB
File Types: {', '.join(subdir_info['file_types'])}
Last Modified: {subdir_info['last_modified']}
"""

        self.kb.add_guideline(
            guideline_id=f"subdir-{source_name}-{subdir_name}",
            title=f"{source_name}/{subdir_name}",
            content=content,
            category="subdirectory",
            metadata={
                'type': 'subdirectory',
                'source': source_name,
                'name': subdir_name,
                'file_count': subdir_info['file_count'],
                'size_mb': subdir_info['size_mb'],
                'file_types': subdir_info['file_types']
            }
        )

    def _analyze_directory(self, dir_path: Path) -> Dict[str, Any]:
        """
        Analyze directory structure and contents

        Returns:
            Metadata about directory (subdirs, files, sizes, stages)
        """
        metadata = {
            'file_count': 0,
            'total_size_mb': 0,
            'subdirectories': {},
            'subdirectory_count': 0,
            'stages': [],
            'has_downloads': False,
            'has_extracted': False,
            'has_parsed': False,
            'last_modified': None
        }

        # Detect processing stages
        if (dir_path / 'downloads').exists():
            metadata['stages'].append('download')
            metadata['has_downloads'] = True
        if (dir_path / 'extracted').exists():
            metadata['stages'].append('extract')
            metadata['has_extracted'] = True
        if (dir_path / 'parsed').exists():
            metadata['stages'].append('parse')
            metadata['has_parsed'] = True

        # Analyze subdirectories
        try:
            for item in dir_path.rglob('*'):
                if item.is_file():
                    metadata['file_count'] += 1
                    try:
                        size_mb = item.stat().st_size / (1024 * 1024)
                        metadata['total_size_mb'] += size_mb

                        # Track last modified
                        mtime = datetime.fromtimestamp(item.stat().st_mtime)
                        if not metadata['last_modified']:
                            metadata['last_modified'] = mtime
                        elif isinstance(metadata['last_modified'], datetime) and mtime > metadata['last_modified']:
                            metadata['last_modified'] = mtime
                        elif isinstance(metadata['last_modified'], str):
                            # Already converted to string, compare as datetime
                            current_dt = datetime.fromisoformat(metadata['last_modified'])
                            if mtime > current_dt:
                                metadata['last_modified'] = mtime

                    except (OSError, PermissionError):
                        pass

                elif item.is_dir() and item.parent == dir_path:
                    # Track immediate subdirectories
                    subdir_name = item.name
                    metadata['subdirectories'][subdir_name] = self._analyze_subdirectory(item)
                    metadata['subdirectory_count'] += 1

        except (OSError, PermissionError) as e:
            print(f"   [WARNING] Permission error reading {dir_path}: {e}")

        # Convert datetime to ISO string before returning
        if metadata['last_modified'] and isinstance(metadata['last_modified'], datetime):
            metadata['last_modified'] = metadata['last_modified'].isoformat()

        return metadata

    def _analyze_subdirectory(self, subdir_path: Path) -> Dict[str, Any]:
        """Analyze a single subdirectory"""
        info = {
            'file_count': 0,
            'size_mb': 0,
            'file_types': set(),
            'last_modified': None
        }

        try:
            for item in subdir_path.rglob('*'):
                if item.is_file():
                    info['file_count'] += 1
                    info['file_types'].add(item.suffix or 'no-extension')
                    try:
                        info['size_mb'] += item.stat().st_size / (1024 * 1024)
                        mtime = datetime.fromtimestamp(item.stat().st_mtime)
                        if not info['last_modified']:
                            info['last_modified'] = mtime
                        elif mtime > info['last_modified']:
                            info['last_modified'] = mtime
                    except (OSError, PermissionError):
                        pass
        except (OSError, PermissionError):
            pass

        info['file_types'] = sorted(list(info['file_types']))
        # Convert datetime to ISO string
        if info['last_modified']:
            info['last_modified'] = info['last_modified'].isoformat()
        return info

    def _create_data_source_content(
        self,
        source_path: Path,
        metadata: Dict[str, Any]
    ) -> str:
        """Create searchable text content for data source"""

        # Build human-readable description
        content = f"""
Data Source: {source_path.name}
Location: {source_path}

Overview:
- Total files: {metadata['file_count']:,}
- Total size: {metadata['total_size_mb']:.1f} MB
- Subdirectories: {metadata['subdirectory_count']}
- Last updated: {metadata['last_modified'] or 'Unknown'}

Structure:
{self._format_subdirectories(metadata['subdirectories'])}

Processing Pipeline:
- Stages present: {', '.join(metadata['stages']) if metadata['stages'] else 'Raw data only'}
- Has downloads: {'Yes' if metadata['has_downloads'] else 'No'}
- Has extracted files: {'Yes' if metadata['has_extracted'] else 'No'}
- Has parsed data: {'Yes' if metadata['has_parsed'] else 'No'}

Search keywords: {source_path.name} data source pipeline files extraction processing
"""
        return content.strip()

    def _format_subdirectories(self, subdirs: Dict[str, Dict]) -> str:
        """Format subdirectory listing for content"""
        if not subdirs:
            return "  (No subdirectories)"

        lines = []
        for name, info in sorted(subdirs.items()):
            lines.append(
                f"  - {name}/: {info['file_count']} files, "
                f"{info['size_mb']:.1f} MB, "
                f"types: {', '.join(info['file_types'][:3])}"
            )
        return '\n'.join(lines)

    def query_data_sources(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Query for relevant data sources

        Args:
            query: Search query (e.g., "chemical data", "production wells")
            top_k: Number of results to return

        Returns:
            List of matching data sources with metadata
        """
        results = self.kb.query(
            query_text=query,
            top_k=top_k,
            category="data-source"
        )

        return results

    def get_directory_structure(self, source_name: str, max_depth: int = 4) -> Optional[Dict[str, Any]]:
        """
        Get complete directory structure for a data source.

        Supports patterns:
          - data/raw/<dataset>/<data_type>/<stage>/files...
          - data/raw/<dataset>/<data_type>/files...
          - data/interim/<dataset>/<data_type>/files...
          - data/processed/<dataset>/files...

        Returns a tree in the "subdirs/files" format that
        data_service.transform_dir_structure_to_file_nodes() already understands.

        Root structure example:
        {
            "name": "fracfocus",
            "path": ".../data/raw/fracfocus",
            "subdirs": {
                "Chemical_data": {
                    "subdirs": {
                        "downloads": {...},
                        "extracted": {...},
                        "parsed": {...}
                    },
                    "files": [],
                    "file_count": N,
                    "total_size_mb": X
                }
            },
            "files": [],
            "file_count": N_total,
            "total_size_mb": X_total
        }
        """
        # We only scan RAW here; processed/interim are already coming from context/all_locations
        data_root = Path(__file__).parent.parent.parent / "data" / "raw"
        source_path = data_root / source_name

        if not source_path.exists():
            print(f"[WARNING] Data source not found in raw/: {source_name}")
            return None

        def build_tree(path: Path, current_depth: int = 0) -> Dict[str, Any]:
            """
            Recursively build a {subdirs, files, file_count, total_size_mb} tree.
            Depth 0 = <dataset>
            Depth 1 = <data_type>
            Depth 2 = <stage> (downloads/extracted/parsed)
            Depth 3+ = any nested dirs/files under stage
            """
            node: Dict[str, Any] = {
                "name": path.name,
                "path": str(path),
                "subdirs": {},
                "files": [],
                "file_count": 0,
                "total_size_mb": 0.0,
            }

            # If this is a file, just capture its size and return
            if path.is_file():
                try:
                    stat = path.stat()
                    size_bytes = stat.st_size
                    node["files"].append({
                        "name": path.name,
                        "size_bytes": size_bytes,
                    })
                    node["file_count"] = 1
                    node["total_size_mb"] = size_bytes / (1024 * 1024)
                except (OSError, PermissionError):
                    pass
                return node

            # Directory: walk children
            try:
                for entry in sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
                    # If we've hit max_depth and this is a directory, don't recurse further
                    if entry.is_dir() and current_depth >= max_depth:
                        # Represent it as an empty subdir placeholder
                        node["subdirs"][entry.name] = {
                            "name": entry.name,
                            "path": str(entry),
                            "subdirs": {},
                            "files": [],
                            "file_count": 0,
                            "total_size_mb": 0.0,
                            "_truncated": True,
                        }
                        continue

                    if entry.is_file():
                        try:
                            stat = entry.stat()
                            size_bytes = stat.st_size
                            node["files"].append({
                                "name": entry.name,
                                "size_bytes": size_bytes,
                            })
                            node["file_count"] += 1
                            node["total_size_mb"] += size_bytes / (1024 * 1024)
                        except (OSError, PermissionError):
                            continue
                    else:
                        # Recurse into subdirectory
                        child_tree = build_tree(entry, current_depth + 1)
                        node["subdirs"][entry.name] = child_tree
                        node["file_count"] += child_tree.get("file_count", 0)
                        node["total_size_mb"] += child_tree.get("total_size_mb", 0.0)
            except (OSError, PermissionError) as e:
                print(f"[WARNING] Cannot read directory {path}: {e}")

            return node

        structure = build_tree(source_path, current_depth=0)
        print(
            f"[Directory Structure] {source_name}: "
            f"{structure.get('file_count', 0)} files, "
            f"{structure.get('total_size_mb', 0.0):.1f} MB"
        )
        return structure

    def get_schema(self, source_name: str, file_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get schema (columns, types) for a data source.

        Reads actual file to extract column names and types.
        Agents use this to verify columns before generating code.

        Args:
            source_name: Name of data source (e.g., "fracfocus")
            file_path: Optional specific file path. If None, finds first parsed file.

        Returns:
            Schema dict:
            {
                'source': source_name,
                'file': file_path,
                'columns': ['col1', 'col2', ...],
                'dtypes': {'col1': 'string', 'col2': 'int64', ...},
                'row_count': N,
                'sample': [{...}, {...}]  # First 5 rows
            }
        """
        import pandas as pd

        # Find parsed file
        if file_path:
            target_file = Path(file_path)
        else:
            # Look for first parsed CSV/Parquet file
            data_root = Path(__file__).parent.parent.parent / "data" / "raw"
            source_path = data_root / source_name

            if not source_path.exists():
                print(f"[WARNING] Data source not found: {source_name}")
                return None

            # Search recursively for parsed directories and files
            # Look in source_name/parsed or source_name/*/parsed
            parsed_files = []

            # Try direct parsed/ directory
            direct_parsed = source_path / "parsed"
            if direct_parsed.exists():
                parsed_files = list(direct_parsed.glob('*.csv')) + list(direct_parsed.glob('*.parquet'))

            # If not found, search in subdirectories
            if not parsed_files:
                for parsed_dir in source_path.rglob('parsed'):
                    if parsed_dir.is_dir():
                        parsed_files = list(parsed_dir.glob('*.csv')) + list(parsed_dir.glob('*.parquet'))
                        if parsed_files:
                            break  # Found some files, stop searching

            if not parsed_files:
                print(f"[WARNING] No CSV/Parquet files in parsed directories for: {source_name}")
                return None

            target_file = parsed_files[0]

        if not target_file.exists():
            print(f"[WARNING] File not found: {target_file}")
            return None

        # Read schema
        try:
            if target_file.suffix == '.csv':
                df = pd.read_csv(target_file, nrows=5)
            elif target_file.suffix == '.parquet':
                df = pd.read_parquet(target_file)
                df = df.head(5)
            else:
                print(f"[WARNING] Unsupported file type: {target_file.suffix}")
                return None

            # Build schema
            schema = {
                'source': source_name,
                'file': str(target_file),
                'columns': list(df.columns),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'row_count': len(df),
                'sample': df.head(5).to_dict(orient='records')
            }

            # Get TOTAL row count across ALL files (not just first file!)
            # This is important for sources with multiple parsed files (e.g., RRC with 29 files)
            try:
                if file_path:
                    # If specific file requested, just count that one
                    if target_file.suffix == '.csv':
                        full_df = pd.read_csv(target_file)
                        schema['row_count'] = len(full_df)
                    elif target_file.suffix == '.parquet':
                        full_df = pd.read_parquet(target_file)
                        schema['row_count'] = len(full_df)
                else:
                    # No specific file - aggregate ALL parsed files for accurate total
                    total_rows = 0
                    files_counted = 0

                    for pf in parsed_files[:50]:  # Limit to first 50 files to avoid long wait
                        try:
                            if pf.suffix == '.csv':
                                count_df = pd.read_csv(pf)
                                total_rows += len(count_df)
                                files_counted += 1
                            elif pf.suffix == '.parquet':
                                count_df = pd.read_parquet(pf)
                                total_rows += len(count_df)
                                files_counted += 1
                        except:
                            continue  # Skip files that can't be read

                    schema['row_count'] = total_rows
                    schema['file_count'] = files_counted
                    schema['total_files'] = len(parsed_files)

                    if files_counted < len(parsed_files):
                        print(f"[Schema] {source_name}: Counted {files_counted}/{len(parsed_files)} files")
            except:
                pass  # Keep sample row count if full read fails

            print(f"[Schema] {source_name}: {len(schema['columns'])} columns, {schema['row_count']:,} rows")
            return schema

        except Exception as e:
            print(f"[ERROR] Cannot read schema from {target_file}: {e}")
            return None

    def get_processing_status(self, source_name: str) -> Optional[Dict[str, Any]]:
        """
        Get processing pipeline status for a data source.

        Checks which stages are complete: download → extract → parse
        Agents use this to understand data availability.

        Args:
            source_name: Name of data source

        Returns:
            Status dict:
            {
                'source': source_name,
                'has_downloads': bool,
                'has_extracted': bool,
                'has_parsed': bool,
                'stages': ['download', 'extract', 'parse'],
                'files_by_stage': {
                    'downloads': 5,
                    'extracted': 5,
                    'parsed': 5
                },
                'status': 'complete' | 'in_progress' | 'not_started'
            }
        """
        data_root = Path(__file__).parent.parent.parent / "data" / "raw"
        source_path = data_root / source_name

        if not source_path.exists():
            print(f"[WARNING] Data source not found: {source_name}")
            return None

        # Check each stage
        # Updated to handle nested structure: {source}/{data_type}/{stage}
        # Examples: fracfocus/Chemical_data/parsed, rrc/production/downloads
        stages_present = []
        files_by_stage = {}

        for stage in ['downloads', 'extracted', 'parsed']:
            # First check direct path (backward compatibility)
            stage_path = source_path / stage
            if stage_path.exists() and stage_path.is_dir():
                stages_present.append(stage)
                files = list(stage_path.rglob('*'))
                files_by_stage[stage] = sum(1 for f in files if f.is_file())
            else:
                # Search in subdirectories (data type folders)
                # Look for {source}/{data_type}/{stage}
                found_in_subdir = False
                for subdir in source_path.iterdir():
                    if subdir.is_dir() and subdir.name not in ['downloads', 'extracted', 'parsed', 'metadata']:
                        # This is a data type folder (e.g., Chemical_data, production)
                        nested_stage_path = subdir / stage
                        if nested_stage_path.exists() and nested_stage_path.is_dir():
                            if not found_in_subdir:
                                # Only add to stages_present once
                                stages_present.append(stage)
                                files_by_stage[stage] = 0
                                found_in_subdir = True
                            # Count files from all data type subdirectories
                            files = list(nested_stage_path.rglob('*'))
                            files_by_stage[stage] += sum(1 for f in files if f.is_file())

        # Determine overall status
        if 'parsed' in stages_present and files_by_stage.get('parsed', 0) > 0:
            status = 'complete'
        elif any(stage in stages_present for stage in ['downloads', 'extracted']):
            status = 'in_progress'
        else:
            status = 'not_started'

        result = {
            'source': source_name,
            'has_downloads': 'downloads' in stages_present,
            'has_extracted': 'extracted' in stages_present,
            'has_parsed': 'parsed' in stages_present,
            'stages': stages_present,
            'files_by_stage': files_by_stage,
            'status': status
        }

        print(f"[Processing Status] {source_name}: {status} - {', '.join(stages_present)}")
        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about indexed repository"""
        stats = self.kb.get_stats()

        # Filter to our namespace
        namespace_stats = stats.get('namespaces', {}).get(self.namespace, {})

        return {
            'index_name': self.kb.index_name,
            'namespace': self.namespace,
            'total_artifacts': namespace_stats.get('vector_count', 0),
            'dimension': stats.get('dimension', 1024)
        }


def main():
    """Test indexing"""
    import sys
    from pathlib import Path

    # Initialize indexer
    print("Initializing Repository Index...")
    indexer = RepositoryIndex()

    # Index data directory
    data_dir = Path(__file__).parent.parent.parent / "data"

    if not data_dir.exists():
        print(f"[ERROR] Data directory not found: {data_dir}")
        return

    # Run indexing
    stats = indexer.index_data_directory(data_dir)

    # Test queries
    print("\n" + "="*80)
    print("TEST QUERIES")
    print("="*80)

    test_queries = [
        "chemical data fracfocus",
        "production wells rrc",
        "completions drilling permits",
        "NETL enhanced oil recovery"
    ]

    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = indexer.query_data_sources(query, top_k=3)

        if results:
            print(f"  Found {len(results)} matches:")
            for i, result in enumerate(results, 1):
                # Handle different result formats (with or without 'metadata' key)
                if 'metadata' in result:
                    name = result['metadata'].get('name', 'Unknown')
                    files = result['metadata'].get('file_count', 0)
                else:
                    name = result.get('title', 'Unknown')
                    files = 0
                score = result.get('score', 0.0)
                print(f"    {i}. {name} (score: {score:.3f}, files: {files:,})")
        else:
            print("  No matches found")

    # Show stats
    print("\n" + "="*80)
    print("FINAL STATS")
    print("="*80)
    final_stats = indexer.get_stats()
    print(f"  Index: {final_stats['index_name']}")
    print(f"  Namespace: {final_stats['namespace']}")
    print(f"  Total artifacts indexed: {final_stats['total_artifacts']}")


if __name__ == "__main__":
    main()
