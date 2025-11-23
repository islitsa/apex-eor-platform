"""
Data Shaping Tool - Phase 3 Step 1

Responsibility: Pipeline formatting, normalization, and record count computation.
Zero dependencies on other tools.

This tool stabilizes the data layer by:
1. Normalizing pipeline structures (multi-location vs legacy formats)
2. Computing summary metrics (totals, counts, sizes)
3. Formatting data for display (human-readable sizes, structured breakdowns)
4. Extracting record counts for session context

Philosophy: Show Everything, Assume Nothing
- Display ALL locations (raw, interim, processed)
- Show file counts and types for each location
- NO assumptions about which is "best"
"""

from typing import Dict, List, Any


class DataShapingTool:
    """
    Phase 3: Extract data shaping logic from orchestrator.

    This tool handles all pipeline data formatting and normalization,
    making the orchestrator smaller and more focused on coordination.
    """

    def __init__(self):
        """Initialize the data shaping tool."""
        pass

    def format_pipeline_for_display(self, pipeline: Dict) -> str:
        """
        Format pipeline with multi-location breakdown for display/tracing.

        Philosophy: Show Everything, Assume Nothing
        - Display ALL locations (raw, interim, processed)
        - Show file counts and types for each location
        - NO assumptions about which is "best"

        Args:
            pipeline: Pipeline dictionary from API

        Returns:
            Formatted string with hierarchical breakdown
        """
        lines = [f"  >> {pipeline.get('display_name', pipeline.get('id'))}"]
        locations_shown = False

        # Check if this pipeline has NEW multi-location structure
        files_info = pipeline.get('files', {})
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
                        # Sort by count descending
                        sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)
                        type_str = ', '.join([f"{count} {ext}" for ext, count in sorted_types])
                        type_str = f" ({type_str})"
                    else:
                        type_str = ""

                    # Add row count if available
                    rows = loc_data.get('row_count', 0)
                    row_str = f" - {rows:,} records" if rows else ""

                    # Format the location line
                    lines.append(f"     📁 {location:<9} {file_count} files{type_str} - {size}{row_str}")
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
                    size_str = self.format_size(stage_size)

                    lines.append(f"     └─ {stage_name}: {stage_files} files, {size_str}")
                    locations_shown = True

        # Fallback 2: Show total from metrics (legacy format)
        if not locations_shown:
            metrics = pipeline.get('metrics', {})
            file_count = metrics.get('file_count', 0)
            data_size = metrics.get('data_size', '0 B')
            lines.append(f"     └─ Total: {file_count} files, {data_size}")

        return "\n".join(lines)

    def format_size(self, size_bytes: int) -> str:
        """
        Format bytes into human-readable size.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string (e.g., "1.5 GB", "234 MB")
        """
        if size_bytes >= 1_000_000_000:
            return f"{size_bytes / 1_000_000_000:.1f} GB"
        elif size_bytes >= 1_000_000:
            return f"{size_bytes / 1_000_000:.1f} MB"
        elif size_bytes >= 1_000:
            return f"{size_bytes / 1_000:.1f} KB"
        else:
            return f"{size_bytes} B"

    def normalize_pipelines(self, pipelines: List[Dict]) -> List[Dict]:
        """
        Normalize pipeline structures to ensure consistent format.

        This handles differences between API versions and ensures
        all pipelines have the expected fields.

        Args:
            pipelines: Raw pipeline list from API

        Returns:
            Normalized pipeline list
        """
        normalized = []

        for pipeline in pipelines:
            # Ensure required fields exist
            normalized_pipeline = {
                'id': pipeline.get('id', ''),
                'display_name': pipeline.get('display_name', pipeline.get('id', '')),
                'status': pipeline.get('status', 'unknown'),
                'metrics': pipeline.get('metrics', {}),
                'files': pipeline.get('files', {}),
            }

            # Ensure metrics has required fields
            if 'file_count' not in normalized_pipeline['metrics']:
                # Try to compute from files
                files_info = normalized_pipeline['files']
                if isinstance(files_info, dict) and 'locations' in files_info:
                    # Sum file counts across all locations
                    total_files = 0
                    for loc_data in files_info.get('locations', {}).values():
                        total_files += loc_data.get('file_count', 0)
                    normalized_pipeline['metrics']['file_count'] = total_files
                else:
                    normalized_pipeline['metrics']['file_count'] = 0

            # Ensure metrics has data_size
            if 'data_size' not in normalized_pipeline['metrics']:
                normalized_pipeline['metrics']['data_size'] = '0 B'

            # Ensure metrics has record_count
            if 'record_count' not in normalized_pipeline['metrics']:
                # Try to compute from locations
                files_info = normalized_pipeline['files']
                if isinstance(files_info, dict) and 'locations' in files_info:
                    # Sum record counts across all locations
                    total_records = 0
                    for loc_data in files_info.get('locations', {}).values():
                        total_records += loc_data.get('row_count', 0)
                    normalized_pipeline['metrics']['record_count'] = total_records
                else:
                    normalized_pipeline['metrics']['record_count'] = 0

            normalized.append(normalized_pipeline)

        return normalized

    def compute_summary_metrics(self, pipelines: List[Dict]) -> Dict[str, Any]:
        """
        Compute summary metrics from pipeline list.

        Args:
            pipelines: Normalized pipeline list

        Returns:
            Summary dict with total_records, total_size, datasets_available, etc.
        """
        total_records = 0
        total_files = 0
        total_size_bytes = 0

        for pipeline in pipelines:
            metrics = pipeline.get('metrics', {})

            # Sum records
            total_records += metrics.get('record_count', 0)

            # Sum files
            total_files += metrics.get('file_count', 0)

            # Sum size (parse from string if needed)
            data_size = metrics.get('data_size', '0 B')
            if isinstance(data_size, str):
                # Try to parse size string back to bytes (rough approximation)
                # For now, just keep as string - proper parsing would need more logic
                pass
            elif isinstance(data_size, int):
                total_size_bytes += data_size

        return {
            'total_records': total_records,
            'total_files': total_files,
            'total_size': self.format_size(total_size_bytes) if total_size_bytes > 0 else '0 B',
            'datasets_available': len(pipelines)
        }

    def extract_record_counts(self, pipelines: List[Dict]) -> Dict[str, int]:
        """
        Extract record counts for each pipeline to build session context.

        Args:
            pipelines: Normalized pipeline list

        Returns:
            Dict mapping pipeline_id -> record_count
        """
        record_counts = {}

        for pipeline in pipelines:
            pipeline_id = pipeline.get('id')
            metrics = pipeline.get('metrics', {})
            record_count = metrics.get('record_count', 0)

            if pipeline_id:
                record_counts[pipeline_id] = record_count

        return record_counts

    def extract_sources_list(self, pipelines: List[Dict]) -> List[str]:
        """
        Extract list of source IDs from pipelines.

        Args:
            pipelines: Normalized pipeline list

        Returns:
            List of pipeline IDs
        """
        return [p.get('id') for p in pipelines if p.get('id')]
