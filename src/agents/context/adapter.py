"""
Context Adapter - Bridges Discovery and Pipeline Data Models

Architectural Role:
This adapter translates between two parallel data models that serve different purposes:

1. Discovery Model (lightweight):
   - Created by discover_real_data.py
   - Flat structure: {source: {row_count, file_count, location}}
   - Purpose: Quick context for Protocol layer validation

2. Pipeline Model (comprehensive):
   - Created by full pipeline processing
   - Nested structure: {source: {directory_structure: {subdirs, files}}}
   - Purpose: Detailed metadata for API endpoints and visualization

The adapter ensures both models can coexist without breaking changes to either system.
"""

from typing import Dict, Any, Optional
from pathlib import Path


class ContextAdapter:
    """
    Translates between discovery context and pipeline context formats.

    This is a service boundary adapter that handles impedance mismatch
    between lightweight discovery and comprehensive pipeline processing.

    Philosophy: Show Everything, Assume Nothing
    - Reports ALL locations where data exists (raw, interim, processed)
    - Makes NO assumptions about which location is "best"
    - Lets the user/orchestrator decide which data to use
    """

    def __init__(self, assume_best: bool = False):
        """
        Initialize adapter with configuration.

        Args:
            assume_best: If False (default), show all locations without prioritization.
                        If True, use legacy behavior (prioritize one location).
                        Provided for migration path - default should remain False.
        """
        self.assume_best = assume_best

    @staticmethod
    def discovery_to_pipeline(context: Dict[str, Any], assume_best: bool = False) -> Dict[str, Any]:
        """
        Convert lightweight discovery context to pipeline format.

        Enriches discovery context with synthetic directory_structure
        so the API can process both context types uniformly.

        Args:
            context: Discovery context from discover_real_data.py or
                    full pipeline context (pass-through)

        Returns:
            Context with directory_structure added where missing

        Examples:
            # Discovery context (before)
            {
                'data_sources': {
                    'fracfocus': {
                        'row_count': 13907094,
                        'file_count': 2,
                        'location': 'data/interim/fracfocus'
                    }
                }
            }

            # Adapted context (after)
            {
                'data_sources': {
                    'fracfocus': {
                        'row_count': 13907094,
                        'file_count': 2,
                        'location': 'data/interim/fracfocus',
                        'directory_structure': {
                            'files': [
                                {'name': 'file_0.parquet', 'size_bytes': 0},
                                {'name': 'file_1.parquet', 'size_bytes': 0}
                            ]
                        }
                    }
                }
            }
        """
        # Deep copy to avoid mutating original
        adapted = {}

        for key, value in context.items():
            if key == 'data_sources':
                adapted[key] = ContextAdapter._adapt_sources(value, assume_best)
            else:
                # Pass through other context keys (summary, initial_prompt, etc.)
                adapted[key] = value

        return adapted

    @staticmethod
    def _adapt_sources(sources: Dict[str, Any], assume_best: bool = False) -> Dict[str, Any]:
        """
        Adapt data_sources dict by adding multi-location directory_structure.

        Philosophy: Show Everything, Assume Nothing
        - Enumerates ALL locations (raw, interim, processed)
        - Reports facts about each location
        - Does NOT prioritize or filter locations

        Args:
            sources: Dictionary of source_id -> source_data
            assume_best: If True, use legacy single-location behavior (for migration)

        Returns:
            Adapted sources with multi-location directory_structure
        """
        adapted_sources = {}

        for source_id, source_data in sources.items():
            # Copy original data
            adapted = source_data.copy()

            # Check if this is discovery context (has file_count but no directory_structure)
            is_discovery = (
                'file_count' in source_data and
                'directory_structure' not in source_data
            )

            if is_discovery:
                all_locations = source_data.get('all_locations', {})

                # Build multi-location structure
                locations_data = {}
                available_in = []

                # Process each location (raw, interim, processed)
                for location_type in ['raw', 'interim', 'processed']:
                    if location_type in all_locations:
                        loc_info = all_locations[location_type]
                        file_count = loc_info.get('file_count', 0)

                        if file_count > 0:
                            # Use file type information from all_locations (already computed)
                            # NO need to scan directories - that's too slow!
                            file_types = loc_info.get('types', {})

                            # Build location data structure
                            locations_data[location_type] = {
                                'files': [],  # Don't enumerate files - too slow
                                'subdirs': {},  # Discovery doesn't track subdirectories
                                'file_count': file_count,
                                'size': loc_info.get('size', '0 B'),
                                'file_types': file_types
                            }

                            # Add row count if available
                            if 'rows' in loc_info and loc_info['rows']:
                                locations_data[location_type]['row_count'] = loc_info['rows']

                            available_in.append(location_type)

                # Build final directory structure
                adapted['directory_structure'] = {
                    'locations': locations_data,
                    'available_in': available_in
                }

                # Add metadata to indicate this was adapted
                adapted['_adapted'] = True
                adapted['_adapter_version'] = '2.0'  # New multi-location version
                adapted['_assume_best'] = assume_best

            adapted_sources[source_id] = adapted

        return adapted_sources

    @staticmethod
    def _enumerate_location_files(location: str, file_count: int, location_type: str) -> list:
        """
        Enumerate actual files from a specific location directory.

        This is the NEW multi-location aware version that:
        - Scans actual directories (raw, interim, processed)
        - Enumerates ALL file types (not just parquet)
        - Returns complete file metadata

        Args:
            location: Path to data directory for this location
            file_count: Expected number of files (from all_locations)
            location_type: Type of location ('raw', 'interim', 'processed')

        Returns:
            List of file metadata dicts with name, size_bytes, type
        """
        files = []

        if not location:
            return files

        try:
            location_path = Path(location)

            if not location_path.exists() or not location_path.is_dir():
                # Location doesn't exist, return empty
                return files

            # For raw, scan subdirectories (e.g., Chemical_data/)
            if location_type == 'raw':
                # Look for data in subdirectories
                for subdir in location_path.iterdir():
                    if subdir.is_dir() and subdir.name not in ['metadata', '.git', '__pycache__']:
                        # Scan this subdirectory recursively
                        files.extend(ContextAdapter._scan_directory_files(subdir))
            else:
                # For interim/processed, scan the location directly
                files.extend(ContextAdapter._scan_directory_files(location_path))

        except Exception as e:
            # If enumeration fails, return empty list
            # The file_count from all_locations will still be used
            pass

        return files

    @staticmethod
    def _scan_directory_files(directory: Path) -> list:
        """
        Recursively scan a directory and return all file metadata.

        Args:
            directory: Path object to scan

        Returns:
            List of file metadata dicts
        """
        files = []

        try:
            for item in directory.rglob('*'):
                if item.is_file():
                    try:
                        size = item.stat().st_size
                    except Exception:
                        size = 0

                    files.append({
                        'name': item.name,
                        'path': str(item.relative_to(directory.parent)),
                        'size_bytes': size,
                        'type': item.suffix.lower()
                    })
        except Exception:
            pass

        return files

    @staticmethod
    def _enumerate_files(location: str, file_count: int) -> list:
        """
        Try to enumerate actual files from location, or synthesize placeholders.

        Args:
            location: Path to data directory
            file_count: Number of files expected

        Returns:
            List of file metadata dicts
        """
        files = []

        if location:
            try:
                location_path = Path(location)
                if location_path.exists() and location_path.is_dir():
                    # Enumerate actual parquet files
                    for i, parquet_file in enumerate(location_path.glob('*.parquet')):
                        if i >= file_count:
                            break

                        try:
                            size = parquet_file.stat().st_size
                        except Exception:
                            size = 0

                        files.append({
                            'name': parquet_file.name,
                            'size_bytes': size
                        })
            except Exception:
                # If enumeration fails, fall through to synthetic files
                pass

        # If we couldn't enumerate actual files, create synthetic placeholders
        if len(files) < file_count:
            remaining = file_count - len(files)
            for i in range(remaining):
                files.append({
                    'name': f'file_{i}.parquet',
                    'size_bytes': 0  # Unknown size
                })

        return files

    @staticmethod
    def is_discovery_context(source_data: Dict[str, Any]) -> bool:
        """
        Check if source data is from discovery (vs full pipeline).

        Args:
            source_data: Single source's metadata

        Returns:
            True if this looks like discovery context
        """
        return (
            'file_count' in source_data and
            'directory_structure' not in source_data
        )

    @staticmethod
    def is_pipeline_context(source_data: Dict[str, Any]) -> bool:
        """
        Check if source data is from full pipeline processing.

        Args:
            source_data: Single source's metadata

        Returns:
            True if this looks like pipeline context
        """
        return 'directory_structure' in source_data
