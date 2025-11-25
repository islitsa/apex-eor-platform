"""
Phase 3A: Data Access API

Simple REST API for generated dashboards to fetch real data from the repository.

Architecture:
- Reads parquet/CSV files from data/raw/{source}/{data_type}/parsed/
- Returns JSON for React dashboards
- Handles basic queries (filters, limits, pagination)

This is Phase 3A (generic data access). Phase 3B will add APEX attribution integration.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd
import json
from pydantic import BaseModel
import sys

# Add parent directory to path for shared_state import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Initialize FastAPI app
app = FastAPI(
    title="APEX EOR Data API",
    description="Phase 3A: Generic data access for generated dashboards",
    version="3.0.0"
)

# Enable CORS for React dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data root paths
DATA_ROOT = Path(__file__).parent.parent.parent / "data" / "raw"
DATA_BASE = Path(__file__).parent.parent.parent / "data"  # For interim/processed access

# Cache for directory structures (avoid re-scanning on every request)
_directory_structure_cache: Dict[str, Any] = {}


# ========================================
# Models
# ========================================

class DataSourceInfo(BaseModel):
    """Metadata about a data source"""
    name: str
    data_types: List[str]  # e.g., ['Chemical_data', 'Geographic_data']
    stages: List[str]  # e.g., ['downloads', 'extracted', 'parsed']
    row_count: int
    columns: List[str]
    schema: Dict[str, str]  # column_name -> dtype


class QueryRequest(BaseModel):
    """Request to query a data source"""
    source: str
    data_type: Optional[str] = None  # Auto-detect if not specified
    columns: Optional[List[str]] = None  # Return all if None
    filters: Optional[Dict[str, Any]] = None  # {column: value} exact match
    limit: int = 1000
    offset: int = 0


# ========================================
# Helper Functions
# ========================================

def find_parsed_file(source: str, data_type: Optional[str] = None) -> Optional[Path]:
    """
    Find the parsed data file for a data source (any supported format).

    Search order:
    1. data/raw/{source}/parsed/*
    2. data/raw/{source}/{data_type}/parsed/*
    3. data/interim/{source}*.*  (for interim processed files)
    4. data/processed/{source}*.*  (for final processed files)

    Supported formats: parquet, csv, json, jsonl
    """
    # Supported file extensions (in priority order)
    SUPPORTED_EXTENSIONS = ['*.parquet', '*.csv', '*.json', '*.jsonl']

    def find_in_dir(directory: Path) -> Optional[Path]:
        """Find first supported file in directory"""
        if not directory.exists():
            return None
        for ext_pattern in SUPPORTED_EXTENSIONS:
            files = list(directory.glob(ext_pattern))
            if files:
                return files[0]
        return None

    def find_by_prefix(directory: Path, prefix: str) -> Optional[Path]:
        """Find first file starting with prefix in directory"""
        if not directory.exists():
            return None
        for ext_pattern in SUPPORTED_EXTENSIONS:
            # Match files like "fracfocus*.parquet", "rrc*.parquet", etc.
            files = list(directory.glob(f"{prefix}{ext_pattern[1:]}"))
            if files:
                return files[0]
        return None

    # PRIORITY 1: Check raw/{source}/parsed/ (standard location)
    source_path = DATA_ROOT / source
    if source_path.exists():
        # If data_type specified, use it directly
        if data_type:
            parsed_dir = source_path / data_type / "parsed"
            result = find_in_dir(parsed_dir)
            if result:
                return result

        # Check flat structure (source/parsed/)
        parsed_dir = source_path / "parsed"
        result = find_in_dir(parsed_dir)
        if result:
            return result

        # Check nested structure (source/*/parsed/)
        for subdir in source_path.iterdir():
            if subdir.is_dir() and subdir.name not in ['downloads', 'extracted', 'parsed', 'metadata']:
                parsed_dir = subdir / "parsed"
                result = find_in_dir(parsed_dir)
                if result:
                    return result

    # PRIORITY 2: Check interim/{source}*.* (common for processed datasets)
    interim_dir = DATA_BASE / "interim"
    result = find_by_prefix(interim_dir, source)
    if result:
        return result

    # PRIORITY 3: Check processed/{source}*.* (final output location)
    processed_dir = DATA_BASE / "processed"
    result = find_by_prefix(processed_dir, source)
    if result:
        return result

    return None


def load_dataframe(source: str, data_type: Optional[str] = None, limit: Optional[int] = None, offset: int = 0) -> pd.DataFrame:
    """
    Load dataframe from parsed file with optional pagination.

    Args:
        source: Data source name
        data_type: Optional data type
        limit: Max rows to return (None = all rows, but defaults to 1000 in endpoints)
        offset: Number of rows to skip

    Returns:
        DataFrame with requested rows
    """
    file_path = find_parsed_file(source, data_type)

    if not file_path:
        raise HTTPException(
            status_code=404,
            detail=f"No parsed data found for source '{source}'" +
                   (f" with data_type '{data_type}'" if data_type else "")
        )

    try:
        if file_path.suffix == '.parquet':
            # Use pyarrow for efficient row-level access (lazy loading)
            import pyarrow.parquet as pq

            # Read parquet file metadata only (fast!)
            parquet_file = pq.ParquetFile(file_path)

            # Calculate which row groups to read
            total_rows = parquet_file.metadata.num_rows

            # If no limit specified, cap at 1000 rows by default for safety
            if limit is None:
                limit = min(1000, total_rows - offset)

            # Read only the needed rows using pyarrow (much faster!)
            table = parquet_file.read_row_groups(
                row_groups=list(range(parquet_file.num_row_groups)),
                columns=None  # Read all columns (can optimize later)
            )

            # Convert to pandas and slice
            df = table.to_pandas()
            return df.iloc[offset:offset + limit]

        elif file_path.suffix == '.csv':
            # For CSV, use skiprows and nrows for pagination
            return pd.read_csv(file_path, skiprows=range(1, offset + 1), nrows=limit)
        elif file_path.suffix in ['.json', '.jsonl']:
            # For JSON/JSONL, load entire file and slice
            # TODO: Optimize for large files with chunked reading
            df = pd.read_json(file_path, lines=(file_path.suffix == '.jsonl'))

            # If no limit specified, cap at 1000 rows by default
            if limit is None:
                limit = min(1000, len(df) - offset)

            return df.iloc[offset:offset + limit]
        else:
            raise HTTPException(status_code=500, detail=f"Unsupported file format: {file_path.suffix}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")


def get_data_types(source: str) -> List[str]:
    """Get list of data types for a source"""
    source_path = DATA_ROOT / source

    if not source_path.exists():
        return []

    data_types = []
    for subdir in source_path.iterdir():
        if subdir.is_dir() and subdir.name not in ['downloads', 'extracted', 'parsed', 'metadata']:
            # Check if it has a parsed directory
            if (subdir / "parsed").exists():
                data_types.append(subdir.name)

    return data_types


def get_file_metadata(source: str, data_type: Optional[str] = None) -> dict:
    """
    Get metadata (row count, columns, schema) WITHOUT loading full dataset.

    Supports multiple formats:
    - Parquet: Uses pyarrow metadata (fast)
    - CSV: Counts lines (moderate)
    - JSON/JSONL: Loads to count (slower but works)
    """
    file_path = find_parsed_file(source, data_type)

    if not file_path:
        raise HTTPException(
            status_code=404,
            detail=f"No parsed data found for source '{source}'"
        )

    try:
        if file_path.suffix == '.parquet':
            import pyarrow.parquet as pq

            # Read only metadata (super fast!)
            parquet_file = pq.ParquetFile(file_path)
            schema = parquet_file.schema_arrow

            return {
                'row_count': parquet_file.metadata.num_rows,
                'columns': schema.names,
                'schema': {name: str(schema.field(name).type) for name in schema.names}
            }
        elif file_path.suffix == '.csv':
            # For CSV, need to load to get metadata (slower)
            df = pd.read_csv(file_path, nrows=0)  # Read only headers
            total_rows = sum(1 for _ in open(file_path)) - 1  # Count lines

            return {
                'row_count': total_rows,
                'columns': df.columns.tolist(),
                'schema': {col: str(dtype) for col, dtype in df.dtypes.items()}
            }
        elif file_path.suffix in ['.json', '.jsonl']:
            # For JSON, read just first row to get columns, then count all rows
            df = pd.read_json(file_path, lines=(file_path.suffix == '.jsonl'), nrows=1)

            # Count total rows (have to load file, but pandas is optimized)
            df_full = pd.read_json(file_path, lines=(file_path.suffix == '.jsonl'))

            return {
                'row_count': len(df_full),
                'columns': df.columns.tolist(),
                'schema': {col: str(dtype) for col, dtype in df.dtypes.items()}
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Unsupported file format: {file_path.suffix}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading metadata: {str(e)}")


def transform_dir_structure_to_file_nodes(dir_structure: dict, source_id: str) -> list:
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
      type: 'file' | 'directory',
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
                        'type': 'directory',
                        'file_count': file_count
                    }

                    # If we have file type breakdown, create child nodes
                    # Support both 'file_types' (real structure) and 'types' (context structure)
                    file_types = loc_data.get('file_types') or loc_data.get('types', {})
                    if file_types:
                        children = []
                        for ext, count in file_types.items():
                            # Create a representative file node for each file type
                            # Handle extensions that may or may not have leading dot
                            ext_display = ext if ext.startswith('.') else f'.{ext}'
                            children.append({
                                'name': f'{ext_display} files ({count})',
                                'path': f'{source_id}/{location_name}/*{ext_display}',
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
                'type': 'directory'
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
                    nested_nodes = transform_dir_structure_to_file_nodes(
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


# ========================================
# API Endpoints
# ========================================

@app.get("/")
async def root():
    """API health check"""
    return {
        "service": "APEX EOR Data API",
        "version": "3.0.0",
        "phase": "3A - Generic Data Access",
        "status": "running"
    }


@app.get("/api/sources", response_model=List[str])
async def list_sources():
    """
    List all available data sources.

    Returns:
        List of source names (e.g., ['fracfocus', 'rrc', 'usgs'])
    """
    if not DATA_ROOT.exists():
        return []

    sources = []
    for source_dir in DATA_ROOT.iterdir():
        if source_dir.is_dir() and source_dir.name not in ['.git', '__pycache__']:
            sources.append(source_dir.name)

    return sorted(sources)


@app.get("/api/sources/{source}/info", response_model=DataSourceInfo)
async def get_source_info(source: str):
    """
    Get metadata about a specific data source.

    Args:
        source: Source name (e.g., 'fracfocus')

    Returns:
        Metadata including columns, row count, available data types
    """
    # Get metadata WITHOUT loading full dataset (fast!)
    try:
        metadata = get_file_metadata(source)
    except HTTPException as e:
        raise e

    # Get data types
    data_types = get_data_types(source)

    return DataSourceInfo(
        name=source,
        data_types=data_types if data_types else ["default"],
        stages=["parsed"],  # Only exposing parsed data for now
        row_count=metadata['row_count'],
        columns=metadata['columns'],
        schema=metadata['schema']
    )


@app.post("/api/query")
async def query_data(request: QueryRequest):
    """
    Query data from a source with filters and pagination.

    Args:
        request: Query parameters (source, columns, filters, limit, offset)

    Returns:
        {
            "data": [...],  # Array of records
            "total": 1000,  # Total matching rows
            "returned": 100,  # Rows in this response
            "offset": 0
        }
    """
    # Get total row count from metadata (fast!)
    try:
        metadata = get_file_metadata(request.source, request.data_type)
        total = metadata['row_count']
    except HTTPException as e:
        raise e

    # Load ONLY the requested rows (lazy loading with limit/offset)
    try:
        df = load_dataframe(request.source, request.data_type, limit=request.limit, offset=request.offset)
    except HTTPException as e:
        raise e

    # Apply column selection
    if request.columns:
        # Validate columns exist
        missing_cols = set(request.columns) - set(df.columns)
        if missing_cols:
            raise HTTPException(
                status_code=400,
                detail=f"Columns not found: {list(missing_cols)}"
            )
        df = df[request.columns]

    # Note: Filters are applied AFTER loading for now
    # TODO: Push filters down to parquet reader for even better performance
    if request.filters:
        for col, value in request.filters.items():
            if col not in df.columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"Filter column not found: {col}"
                )
            df = df[df[col] == value]
        # Adjust total after filtering
        total = len(df)

    # Convert to JSON-serializable format (pandas handles NaN conversion automatically)
    import json
    records_json = df.to_json(orient='records')
    records = json.loads(records_json)  # This automatically converts NaN to null

    return {
        "data": records,
        "total": total,
        "returned": len(records),
        "offset": request.offset
    }


@app.get("/api/sources/{source}/data")
async def get_data(
    source: str,
    data_type: Optional[str] = None,
    limit: int = Query(1000, ge=1, le=10000),
    offset: int = Query(0, ge=0),
    columns: Optional[str] = Query(None, description="Comma-separated column names")
):
    """
    Simple GET endpoint to fetch data (alternative to POST /api/query).

    Args:
        source: Source name (e.g., 'fracfocus')
        data_type: Optional data type (e.g., 'Chemical_data')
        limit: Max rows to return (default 1000, max 10000)
        offset: Pagination offset (default 0)
        columns: Comma-separated column names to return (optional)

    Returns:
        {
            "data": [...],
            "total": 1000,
            "returned": 100,
            "offset": 0
        }
    """
    # Parse columns
    column_list = None
    if columns:
        column_list = [c.strip() for c in columns.split(",")]

    # Build request
    request = QueryRequest(
        source=source,
        data_type=data_type,
        columns=column_list,
        filters=None,
        limit=limit,
        offset=offset
    )

    return await query_data(request)


def parse_size_string(size_str: str) -> int:
    """
    Parse size string like "7.16 GB", "970.9 MB" into bytes.

    Args:
        size_str: Size string with unit (e.g., "7.16 GB")

    Returns:
        Size in bytes as integer
    """
    size_str = size_str.strip()
    if not size_str or size_str == "0 B":
        return 0

    # Extract number and unit
    parts = size_str.split()
    if len(parts) != 2:
        return 0

    try:
        value = float(parts[0])
        unit = parts[1].upper()

        # Convert to bytes
        multipliers = {
            'B': 1,
            'KB': 1_000,
            'MB': 1_000_000,
            'GB': 1_000_000_000,
            'TB': 1_000_000_000_000
        }

        return int(value * multipliers.get(unit, 1))
    except (ValueError, KeyError):
        return 0


@app.get("/api/pipelines")
async def get_pipelines():
    """
    Get pipeline metadata from shared state.

    UPDATED v3: Uses PipelineAssemblyTool for real filesystem-detected stages!

    Returns information about all data pipelines including:
    - Pipeline stages (download, extract, parse, validate, load) - DETECTED FROM FILESYSTEM
    - Current status of each stage
    - File counts and metrics
    - Directory structure

    Returns:
        {
            "pipelines": [
                {
                    "id": "fracfocus",
                    "name": "fracfocus",
                    "display_name": "FracFocus Chemical Data",
                    "status": "processed",
                    "metrics": {
                        "file_count": 156,
                        "record_count": 239059,
                        "data_size": "34.2 GB"
                    },
                    "stages": [
                        {"name": "downloads", "status": "complete", "file_count": 1},
                        {"name": "extracted", "status": "complete", "file_count": 17},
                        {"name": "parsed", "status": "complete", "file_count": 17}
                    ],
                    "files": {...}
                }
            ],
            "summary": {
                "total_pipelines": 10,
                "total_records": 224044778,
                "total_size": "36.49 GB"
            }
        }
    """
    try:
        from src.shared_state import PipelineState
        from src.agents.context.adapter import ContextAdapter
        from src.agents.tools.pipeline_assembly_tool import PipelineAssemblyTool

        # Load pipeline context
        context = PipelineState.load_context(check_freshness=False)

        if not context:
            return {
                "pipelines": [],
                "summary": {
                    "total_pipelines": 0,
                    "total_records": 0,
                    "total_size": "0 B"
                }
            }

        # Adapt context: bridge discovery and pipeline formats
        context = ContextAdapter.discovery_to_pipeline(context)

        import sys
        sys.stderr.write(f"[ContextAdapter] Applied context adaptation\n")
        sys.stderr.flush()

        # Extract pipeline data from context
        pipelines = []
        total_records = 0
        total_size_bytes = 0  # Track total size across all pipelines

        data_sources = context.get('data_sources', {})

        for source_id, source_data in data_sources.items():
            # Get display name
            display_name = source_data.get('display_name', source_id)

            # Get status
            status = source_data.get('status', 'unknown')

            # Get processing state (stages)
            processing_state = source_data.get('processing_state', {})

            # Separate actual pipeline stages from metadata
            # Valid stage names: download, extraction, parsing, validation, loading
            VALID_STAGES = {'download', 'extraction', 'parsing', 'validation', 'loading',
                           'extract', 'parse', 'validate', 'load', 'processed'}

            stages = []
            metadata = {}

            for key, value in processing_state.items():
                # Check if this is an actual stage or metadata
                # Order matters: check metadata patterns FIRST before stage matching

                # If key contains 'date', 'files', 'count', 'note' - it's metadata
                if any(x in key.lower() for x in ['date', 'files', 'count', 'note']):
                    metadata[key] = value
                # If value is a number or ISO timestamp - it's metadata
                elif isinstance(value, (int, float)):
                    metadata[key] = value
                elif isinstance(value, str) and 'T' in value and ':' in value:  # ISO timestamp
                    metadata[key] = value
                # If key exactly matches a known stage name, it's a stage
                elif key.lower() in VALID_STAGES:
                    stages.append({
                        "name": key,
                        "status": str(value) if value else 'unknown'
                    })
                # Unknown - treat as metadata to be safe
                else:
                    metadata[key] = value

            # Get REAL directory structure from file system (not from adapter's meta-structure)
            # Use cache to avoid re-scanning on every request
            real_dir_structure = None
            if source_id in _directory_structure_cache:
                real_dir_structure = _directory_structure_cache[source_id]
            else:
                # Only scan if source directory actually exists
                source_dir = DATA_ROOT / source_id
                if source_dir.exists() and source_dir.is_dir():
                    from src.knowledge.repository_index import RepositoryIndex
                    indexer = RepositoryIndex()

                    # Fetch actual file system structure with depth limit for performance
                    # max_depth=3 shows: fracfocus/ -> chemical_data/ -> downloads/extracted/parsed/ -> files
                    real_dir_structure = indexer.get_directory_structure(source_id, max_depth=3)

                    # Cache it for future requests
                    if real_dir_structure:
                        _directory_structure_cache[source_id] = real_dir_structure
                else:
                    # Source doesn't have raw directory, cache None to avoid checking again
                    _directory_structure_cache[source_id] = None

            # Use real structure if available, otherwise fall back to context
            import sys
            sys.stderr.write(f"[DEBUG] {source_id}: real_dir_structure = {bool(real_dir_structure)}\n")
            sys.stderr.flush()

            if real_dir_structure:
                dir_structure = real_dir_structure
            else:
                # Fallback to context (for backward compatibility)
                dir_structure = source_data.get('directory_structure', {})
                sys.stderr.write(f"[DEBUG] {source_id}: dir_structure from context = {bool(dir_structure)}, has all_locations = {'all_locations' in source_data}\n")
                sys.stderr.flush()

                # FIX #16: If directory_structure not found, try using all_locations from context
                if not dir_structure and 'all_locations' in source_data:
                    # Convert all_locations to locations format for transformation
                    dir_structure = {'locations': source_data['all_locations']}
                    sys.stderr.write(f"[FIX #16] {source_id}: Using all_locations from context - {list(source_data['all_locations'].keys())}\n")
                    sys.stderr.flush()

            file_count = 0
            total_size_bytes = 0
            record_count = 0

            # Debug: Check if directory_structure exists
            if not dir_structure:
                print(f"[DEBUG] {source_id}: NO directory_structure found!")
            else:
                print(f"[DEBUG] {source_id}: dir_structure keys = {list(dir_structure.keys())}")

            # Handle NEW multi-location structure vs OLD subdirs structure
            if 'locations' in dir_structure:
                # NEW multi-location structure
                for loc_name, loc_data in dir_structure.get('locations', {}).items():
                    file_count += loc_data.get('file_count', 0)

                    # Parse size string (e.g., "7.16 GB", "970.9 MB")
                    size_str = loc_data.get('size', '0 B')
                    size_bytes = parse_size_string(size_str)
                    total_size_bytes += size_bytes

                    # Get record count if available
                    if 'row_count' in loc_data:
                        record_count += loc_data.get('row_count', 0)
            else:
                # Real file system structure - use pre-computed counts
                if 'file_count' in dir_structure and 'total_size_mb' in dir_structure:
                    # Real structure from get_directory_structure() has pre-computed counts
                    file_count = dir_structure.get('file_count', 0)
                    total_size_bytes = int(dir_structure.get('total_size_mb', 0) * 1024 * 1024)
                else:
                    # OLD subdirs structure - count files recursively
                    def count_files(node):
                        nonlocal file_count, total_size_bytes
                        if isinstance(node, dict):
                            # Count files at THIS level only (not subdirs - we'll recurse for those)
                            if 'files' in node and isinstance(node['files'], list):
                                file_count += len(node['files'])  # Count actual files, not pre-computed total
                                # Sum up individual file sizes
                                for file_info in node['files']:
                                    if isinstance(file_info, dict) and 'size_bytes' in file_info:
                                        total_size_bytes += file_info['size_bytes']
                            # Recurse into subdirectories
                            if 'subdirs' in node:
                                for subdir in node['subdirs'].values():
                                    count_files(subdir)

                    count_files(dir_structure)

            # Use calculated total size
            file_size_bytes = total_size_bytes

            # Debug logging - ALWAYS show for now to diagnose issue
            import sys
            sys.stderr.write(f"[DEBUG] {source_id}: file_count={file_count}, total_size_bytes={total_size_bytes}, record_count={record_count}, formatted={file_size_bytes / 1e9:.2f} GB\n")
            sys.stderr.flush()

            # Format file size
            if file_size_bytes >= 1_000_000_000:
                data_size = f"{file_size_bytes / 1_000_000_000:.1f} GB"
            elif file_size_bytes >= 1_000_000:
                data_size = f"{file_size_bytes / 1_000_000:.1f} MB"
            elif file_size_bytes >= 1_000:
                data_size = f"{file_size_bytes / 1_000:.1f} KB"
            else:
                data_size = f"{file_size_bytes} B"

            # FIX: Get ACTUAL record count from data files (parquet/CSV/etc)
            # The context data doesn't include record counts, so we need to read from files
            # This is fast because we only read metadata, not the actual data
            if record_count == 0:  # Only fetch if not already set from context
                try:
                    # Try to get metadata from parsed files
                    # This handles parquet (pyarrow metadata) and CSV (line counting)
                    file_metadata = get_file_metadata(source_id)
                    if file_metadata:
                        record_count = file_metadata.get('row_count', 0)
                        sys.stderr.write(f"[FIX] {source_id}: Fetched record_count={record_count} from file metadata\n")
                        sys.stderr.flush()
                except HTTPException:
                    # No parsed files found - that's OK, record_count stays 0
                    sys.stderr.write(f"[INFO] {source_id}: No parsed files found for record count\n")
                    sys.stderr.flush()
                except Exception as e:
                    # Log but don't fail - record_count stays 0
                    sys.stderr.write(f"[WARN] {source_id}: Error reading record count: {e}\n")
                    sys.stderr.flush()

            # FIX #15: Transform directory structure to FileNode[] format for React
            file_nodes = transform_dir_structure_to_file_nodes(dir_structure, source_id)

            pipeline = {
                "id": source_id,
                "name": source_id,
                "display_name": display_name,
                "status": status,
                "metrics": {
                    "file_count": file_count,
                    "record_count": record_count,
                    "data_size": data_size
                },
                "stages": stages,
                "metadata": metadata,  # Separated from stages
                "files": file_nodes  # Now returns FileNode[] instead of raw dir_structure
            }

            pipelines.append(pipeline)
            total_records += record_count
            total_size_bytes += file_size_bytes  # Accumulate total size

        # Format total size from accumulated bytes
        if total_size_bytes >= 1_000_000_000:
            total_size_str = f"{total_size_bytes / 1_000_000_000:.2f} GB"
        elif total_size_bytes >= 1_000_000:
            total_size_str = f"{total_size_bytes / 1_000_000:.1f} MB"
        elif total_size_bytes >= 1_000:
            total_size_str = f"{total_size_bytes / 1_000:.1f} KB"
        else:
            total_size_str = f"{total_size_bytes} B"

        # Get summary from context
        summary_data = context.get('summary', {})

        # ENRICHMENT: Use PipelineAssemblyTool to detect stages from filesystem
        # This ensures React UI gets real stage data (downloads/extracted/parsed)
        try:
            pipeline_tool = PipelineAssemblyTool(data_root="data/raw")

            # Build data_context format that PipelineAssemblyTool expects
            enrichment_context = {
                "pipelines": pipelines,
                "summary": summary_data
            }

            # Call assembly tool to enhance pipelines with filesystem-detected stages
            enriched_pipelines = pipeline_tool.assemble_pipelines(enrichment_context)

            import sys
            sys.stderr.write(f"[API ENRICHMENT] Enhanced {len(enriched_pipelines)} pipelines with stage detection\n")
            sys.stderr.flush()

            # Use enriched pipelines instead of original
            pipelines = enriched_pipelines

        except Exception as e:
            # Don't fail the entire API call if enrichment fails
            # Log the error and continue with un-enriched pipelines
            import sys
            sys.stderr.write(f"[API ENRICHMENT WARNING] Failed to enrich pipelines: {e}\n")
            sys.stderr.flush()

        return {
            "pipelines": pipelines,
            "summary": {
                "total_pipelines": len(pipelines),
                "total_records": summary_data.get('total_records', total_records),
                "total_size": total_size_str,  # Use calculated total!
                "datasets_available": summary_data.get('datasets_available', len(pipelines))
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading pipeline context: {str(e)}"
        )


# ========================================
# Development Server
# ========================================

if __name__ == "__main__":
    import uvicorn

    print("=" * 80)
    print("PHASE 3A: DATA ACCESS API")
    print("=" * 80)
    print()
    print("Starting API server...")
    print("API will be available at: http://localhost:8000")
    print("API docs: http://localhost:8000/docs")
    print()
    print("Example requests:")
    print("  - List sources: GET http://localhost:8000/api/sources")
    print("  - Get info: GET http://localhost:8000/api/sources/fracfocus/info")
    print("  - Get data: GET http://localhost:8000/api/sources/fracfocus/data?limit=10")
    print()

    uvicorn.run(
        "src.api.data_service:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on file changes
    )
