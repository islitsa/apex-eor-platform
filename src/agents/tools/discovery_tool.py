"""
DataDiscoveryTool - Phase 1.5

Encapsulates data discovery logic for fetching real data from backend API.

This tool isolates all API communication, making it:
- Testable without running full orchestrator
- Mock-able for unit tests
- Reusable across different orchestration strategies
"""

from typing import Dict, List, Optional, Any
import requests


class DataDiscoveryTool:
    """
    Handles data discovery by fetching real data from backend API.

    Phase 1.5: Extracted from orchestrator to centralize API communication.
    """

    def __init__(self, filter_tool=None, trace_collector=None):
        """
        Initialize DataDiscoveryTool.

        Args:
            filter_tool: Optional DataFilterTool for filtering pipelines
            trace_collector: Optional trace collector for observability
        """
        self.filter_tool = filter_tool
        self.trace_collector = trace_collector

    def fetch_data_context(
        self,
        api_url: str = "http://localhost:8000",
        filter_sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Fetch REAL DATA from backend API before designing UI.

        This is CRITICAL: UX Agent needs to see actual data structure
        to design appropriate visualizations, not design blindly!

        Args:
            api_url: API endpoint URL
            filter_sources: Optional list of source IDs to include (e.g., ['rrc', 'production'])
                           If None, returns all sources. If provided, only returns matching sources.

        Returns:
            {
                'pipelines': [...],  # Actual pipeline data (filtered if filter_sources provided)
                'summary': {...},    # Total records, size, etc.
                'success': bool,     # Whether API call succeeded
                'error': str | None  # Error message if failed
            }
        """
        print("[DataDiscoveryTool] Fetching REAL DATA from backend API...")
        print(f"  [API] Endpoint: {api_url}/api/pipelines")

        # Emit trace: Starting data fetch
        if self.trace_collector:
            self.trace_collector.trace_thinking(
                agent="DataDiscoveryTool",
                method="fetch_data_context",
                thought=f"Fetching REAL DATA from backend API: {api_url}/api/pipelines"
            )

        try:
            # Timeout: 15s to allow initial cache warming (first request scans directories)
            response = requests.get(f"{api_url}/api/pipelines", timeout=15)
            response.raise_for_status()

            data = response.json()
            pipelines = data.get('pipelines', [])
            summary = data.get('summary', {})

            # Filter pipelines if filter_sources is provided (using centralized tool)
            print(f"\n[DEBUG DataDiscoveryTool] filter_sources parameter: {filter_sources}")
            print(f"[DEBUG DataDiscoveryTool] Total pipelines before filter: {len(pipelines)}")

            if filter_sources and self.filter_tool:
                original_count = len(pipelines)
                pipelines = self.filter_tool.filter_pipelines(pipelines, filter_sources)
                filtered_count = len(pipelines)

                print(f"[DEBUG DataDiscoveryTool] Pipelines after filter: {filtered_count}")
                print(f"[DEBUG DataDiscoveryTool] Pipeline IDs kept: {[p.get('id') for p in pipelines]}")

                if filtered_count < original_count:
                    print(f"  [API] FILTERED: {filtered_count}/{original_count} pipelines match prompt scope: {filter_sources}")
            elif filter_sources and not self.filter_tool:
                print(f"[DEBUG DataDiscoveryTool] Warning: filter_sources provided but no filter_tool available")
            else:
                print(f"[DEBUG DataDiscoveryTool] No filtering - filter_sources is None")

            print(f"  [API] SUCCESS - Retrieved real data:")
            print(f"        - Pipelines: {len(pipelines)}")
            print(f"        - Total Records: {summary.get('total_records', 0):,}")
            print(f"        - Total Size: {summary.get('total_size', '0 B')}")

            # Show first 3 pipelines
            if pipelines:
                print(f"  [API] Sample pipelines:")
                for i, pipeline in enumerate(pipelines[:3], 1):
                    print(f"        {i}. {pipeline.get('display_name', pipeline.get('id'))}")
                    print(f"           Status: {pipeline.get('status')}, Files: {pipeline.get('metrics', {}).get('file_count', 0)}")

            # Emit trace: Success with detailed breakdown
            if self.trace_collector:
                pipeline_details = self._format_pipeline_breakdown(pipelines)

                self.trace_collector.trace_reasoning(
                    agent="DataDiscoveryTool",
                    method="fetch_data_context",
                    reasoning=f"""Successfully fetched REAL DATA from API:

SUMMARY:
- Total Pipelines: {len(pipelines)}
- Total Records: {summary.get('total_records', 0):,}
- Total Size: {summary.get('total_size', '0 B')}
- Datasets Available: {summary.get('datasets_available', len(pipelines))}

PIPELINE BREAKDOWN (by stage):
{pipeline_details}

This detailed data structure will be passed to BOTH UX Designer and React Developer!
NO EXCUSE for mock data generation."""
                )

            # FIX #15: Transform directory structures to FileNode[] format for React
            # The backend returns complex nested objects, but React expects a flat array of FileNode objects
            for pipeline in pipelines:
                if 'files' in pipeline and pipeline['files']:
                    pipeline['files'] = self._transform_dir_structure_to_file_nodes(
                        pipeline['files'],
                        pipeline.get('id', 'unknown')
                    )

            return {
                'pipelines': pipelines,
                'summary': summary,
                'success': True,
                'error': None
            }

        except requests.exceptions.ConnectionError:
            error_msg = f"Cannot connect to API at {api_url}. Is the backend running?"
            print(f"  [API] ERROR: {error_msg}")

            # Emit trace: Connection error
            if self.trace_collector:
                self.trace_collector.trace_thinking(
                    agent="DataDiscoveryTool",
                    method="fetch_data_context",
                    thought=f"API Connection Error: {error_msg}"
                )

            return {
                'pipelines': [],
                'summary': {},
                'success': False,
                'error': error_msg
            }

        except Exception as e:
            error_msg = f"Failed to fetch data: {str(e)}"
            print(f"  [API] ERROR: {error_msg}")

            # Emit trace: Other error
            if self.trace_collector:
                self.trace_collector.trace_thinking(
                    agent="DataDiscoveryTool",
                    method="fetch_data_context",
                    thought=f"API Error: {error_msg}"
                )

            return {
                'pipelines': [],
                'summary': {},
                'success': False,
                'error': error_msg
            }

    def _format_pipeline_breakdown(self, pipelines: List[Dict]) -> str:
        """
        Format pipeline breakdown for trace output.

        Philosophy: Show Everything, Assume Nothing
        - Display ALL locations (raw, interim, processed)
        - Show file counts and types for each location
        - NO assumptions about which is "best"

        Args:
            pipelines: List of pipeline dicts

        Returns:
            Formatted string showing pipeline details
        """
        def format_pipeline_detail(p):
            lines = [f"  >> {p.get('display_name', p.get('id'))}"]
            locations_shown = False

            # Check if this pipeline has NEW multi-location structure
            files_info = p.get('files', {})
            if files_info and isinstance(files_info, dict) and 'locations' in files_info:
                locations_data = files_info.get('locations', {})
                available_in = files_info.get('available_in', [])

                # Show each location that has data
                for location in ['raw', 'interim', 'processed']:
                    if location in locations_data:
                        loc_data = locations_data[location]
                        file_count = loc_data.get('file_count', 0)
                        size = loc_data.get('size', '0 B')

                        # Build file type breakdown
                        file_types = loc_data.get('file_types', {})
                        if file_types:
                            sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)
                            type_str = ', '.join([f"{count} {ext}" for ext, count in sorted_types])
                            type_str = f" ({type_str})"
                        else:
                            type_str = ""

                        # Add row count if available
                        rows = loc_data.get('row_count', 0)
                        row_str = f" - {rows:,} records" if rows else ""

                        # Format the location line
                        lines.append(f"     {location:<9} {file_count} files{type_str} - {size}{row_str}")
                        locations_shown = True

                # Show availability summary
                if available_in:
                    lines.append(f"")
                    lines.append(f"     Available in {len(available_in)} location(s)")

            # Fallback 1: Check for OLD subdirs structure (pipeline stages)
            elif files_info and isinstance(files_info, dict) and 'subdirs' in files_info:
                subdirs = files_info.get('subdirs', {})

                # Show breakdown by pipeline stage
                for stage_name in ['downloads', 'extracted', 'parsed']:
                    if stage_name in subdirs:
                        stage = subdirs[stage_name]
                        stage_files = len(stage.get('files', []))

                        # Calculate stage size
                        stage_size = 0
                        for f in stage.get('files', []):
                            if isinstance(f, dict):
                                stage_size += f.get('size_bytes', 0)

                        # Format size
                        if stage_size >= 1_000_000_000:
                            size_str = f"{stage_size / 1_000_000_000:.1f} GB"
                        elif stage_size >= 1_000_000:
                            size_str = f"{stage_size / 1_000_000:.1f} MB"
                        elif stage_size >= 1_000:
                            size_str = f"{stage_size / 1_000:.1f} KB"
                        else:
                            size_str = f"{stage_size} B"

                        lines.append(f"     - {stage_name}: {stage_files} files, {size_str}")
                        locations_shown = True

            # Fallback 2: Show total from metrics (legacy format)
            if not locations_shown and 'metrics' in p:
                file_count = p['metrics'].get('file_count', 0)
                data_size = p['metrics'].get('data_size', '0 B')
                lines.append(f"     - Total: {file_count} files, {data_size}")

            return "\n".join(lines)

        # Show ALL pipelines (no truncation)
        return "\n\n".join([format_pipeline_detail(p) for p in pipelines])

    def _transform_dir_structure_to_file_nodes(self, dir_structure: Dict, source_id: str) -> List[Dict]:
        """
        Transform backend directory structure to FileNode[] format for React.

        FIX #15: Bridges the gap between backend's nested directory structure and React's FileNode[] format.

        Handles three backend formats:
        1. New multi-location: {locations: {raw: {...}, interim: {...}, processed: {...}}}
        2. Real file system: {subdirs: {...}, files: [...], file_count: N, total_size_mb: X}
        3. Old format: {subdirs: {...}, files: [...]}

        Converts to React format:
        {
          name: string,
          path: string,
          type: 'file' | 'folder',
          size?: number,
          children?: FileNode[]
        }

        Args:
            dir_structure: Backend directory structure object
            source_id: Pipeline ID for generating paths

        Returns:
            List of FileNode objects (flat array with nested children)
        """
        if not dir_structure or not isinstance(dir_structure, dict):
            return []

        file_nodes = []

        # Format 1: New multi-location structure
        if 'locations' in dir_structure:
            locations = dir_structure.get('locations', {})

            # Create a folder node for each location that has data
            for location_name in ['raw', 'interim', 'processed']:
                if location_name in locations:
                    loc_data = locations[location_name]
                    file_count = loc_data.get('file_count', 0)

                    if file_count > 0:
                        # Create folder node for this location
                        folder_node = {
                            'name': location_name,
                            'path': f'{source_id}/{location_name}',
                            'type': 'folder',
                            'file_count': file_count
                        }

                        # If we have file type breakdown, create child nodes
                        file_types = loc_data.get('file_types', {})
                        if file_types:
                            children = []
                            for ext, count in file_types.items():
                                # Create a representative file node for each file type
                                children.append({
                                    'name': f'{ext} files ({count})',
                                    'path': f'{source_id}/{location_name}/*.{ext}',
                                    'type': 'file',
                                    'count': count
                                })
                            folder_node['children'] = children

                        file_nodes.append(folder_node)

        # Format 2 & 3: Real file system or old format with subdirs
        elif 'subdirs' in dir_structure:
            subdirs = dir_structure.get('subdirs', {})

            # Create folder nodes for each subdir
            for subdir_name, subdir_data in subdirs.items():
                folder_node = {
                    'name': subdir_name,
                    'path': f'{source_id}/{subdir_name}',
                    'type': 'folder'
                }

                # Recursively process subdirectory
                if isinstance(subdir_data, dict):
                    # Get files in this directory
                    files_list = subdir_data.get('files', [])
                    children = []

                    # Add file nodes
                    for file_info in files_list:
                        if isinstance(file_info, dict):
                            file_node = {
                                'name': file_info.get('name', 'unknown'),
                                'path': f"{source_id}/{subdir_name}/{file_info.get('name', 'unknown')}",
                                'type': 'file',
                                'size': file_info.get('size_bytes', 0)
                            }
                            children.append(file_node)
                        elif isinstance(file_info, str):
                            # Just a filename string
                            children.append({
                                'name': file_info,
                                'path': f'{source_id}/{subdir_name}/{file_info}',
                                'type': 'file'
                            })

                    # Recursively process nested subdirs
                    if 'subdirs' in subdir_data:
                        nested_nodes = self._transform_dir_structure_to_file_nodes(
                            {'subdirs': subdir_data['subdirs']},
                            f'{source_id}/{subdir_name}'
                        )
                        children.extend(nested_nodes)

                    if children:
                        folder_node['children'] = children

                file_nodes.append(folder_node)

        # Also check for files at root level
        if 'files' in dir_structure:
            files_list = dir_structure.get('files', [])
            for file_info in files_list:
                if isinstance(file_info, dict):
                    file_node = {
                        'name': file_info.get('name', 'unknown'),
                        'path': f"{source_id}/{file_info.get('name', 'unknown')}",
                        'type': 'file',
                        'size': file_info.get('size_bytes', 0)
                    }
                    file_nodes.append(file_node)
                elif isinstance(file_info, str):
                    file_nodes.append({
                        'name': file_info,
                        'path': f'{source_id}/{file_info}',
                        'type': 'file'
                    })

        return file_nodes
