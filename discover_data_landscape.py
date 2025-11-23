"""
Data Landscape Discovery - Neutral Observer

Shows ALL data locations without making quality judgments.
Reports facts about data state, not assumptions about "best" version.

Philosophy:
- raw/, interim/, processed/ are STATES not quality levels
- User might be mid-migration, testing, debugging, rolling back
- System should show everything, let user decide
- Gradient context needs semantic relationships, not hierarchical assumptions
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from shared_state import PipelineState

print("=" * 70)
print("DATA LANDSCAPE DISCOVERY - NEUTRAL OBSERVER")
print("=" * 70)
print("\nShowing ALL data locations without assumptions")
print("Each location is a STATE, not a quality judgment\n")

# Scan ALL data directories
data_root = project_root / "data"
data_directories = ['raw', 'external', 'interim', 'processed']

if not data_root.exists():
    print(f"\n[ERROR] Data root not found: {data_root}")
    sys.exit(1)

# Build landscape: source_name -> {locations: {dir_type: info}}
data_landscape = {}

# Scan each directory
for dir_type in data_directories:
    data_dir = data_root / dir_type

    if not data_dir.exists():
        continue

    print(f"\n{'='*70}")
    print(f"SCANNING: {dir_type.upper()}/")
    print(f"{'='*70}")

    # Scan each source subdirectory
    for source_dir in data_dir.iterdir():
        if not source_dir.is_dir():
            continue

        source_name = source_dir.name

        print(f"\n[Observing] {source_name} in {dir_type}/...")

        # Find ALL files (not just parquet!)
        all_files = list(source_dir.rglob("*"))

        if not all_files:
            print(f"  No files found")
            continue

        # Classify files by type
        files_by_type = {}
        total_size_bytes = 0
        parquet_files = []

        for file_path in all_files:
            if not file_path.is_file():
                continue

            ext = file_path.suffix.lower()

            # Group by extension
            if ext not in files_by_type:
                files_by_type[ext] = []

            try:
                size_bytes = file_path.stat().st_size
            except Exception:
                size_bytes = 0

            file_info = {
                'name': file_path.name,
                'size_bytes': size_bytes,
                'path': str(file_path.relative_to(source_dir))
            }

            files_by_type[ext].append(file_info)
            total_size_bytes += size_bytes

            # Track parquet files for row counting
            if ext == '.parquet':
                parquet_files.append(file_path)

        if not files_by_type:
            continue

        # Count rows from parquet files if available
        total_rows = 0
        if parquet_files:
            print(f"  Counting rows from {len(parquet_files)} parquet files...")
            for pq_file in parquet_files:
                try:
                    df = pd.read_parquet(pq_file)
                    rows = len(df)
                    total_rows += rows
                except Exception as e:
                    print(f"    [WARN] Could not read {pq_file.name}: {e}")

        # Format size
        if total_size_bytes >= 1_000_000_000:
            size_str = f"{total_size_bytes / 1_000_000_000:.2f} GB"
        elif total_size_bytes >= 1_000_000:
            size_str = f"{total_size_bytes / 1_000_000:.1f} MB"
        elif total_size_bytes >= 1_000:
            size_str = f"{total_size_bytes / 1_000:.1f} KB"
        else:
            size_str = f"{total_size_bytes} B"

        total_files = sum(len(files) for files in files_by_type.values())

        # Show what we found
        print(f"  {total_files} files, {size_str}")
        for ext, files in sorted(files_by_type.items()):
            print(f"    - {len(files)} {ext or 'no-ext'} files")
        if total_rows > 0:
            print(f"  Rows: {total_rows:,}")

        # Add to landscape
        if source_name not in data_landscape:
            data_landscape[source_name] = {'locations': {}}

        data_landscape[source_name]['locations'][dir_type] = {
            'path': str(source_dir),
            'file_count': total_files,
            'files_by_type': {
                ext: len(files) for ext, files in files_by_type.items()
            },
            'total_size_bytes': total_size_bytes,
            'total_size_human': size_str,
            'row_count': total_rows if total_rows > 0 else None,
            'file_list': [
                {'name': f['name'], 'size_bytes': f['size_bytes']}
                for files in files_by_type.values()
                for f in files
            ]
        }

print("\n" + "=" * 70)
print("DATA LANDSCAPE SUMMARY")
print("=" * 70)

if not data_landscape:
    print("\n[ERROR] No data sources found!")
    print(f"Searched: {', '.join(data_directories)}")
    sys.exit(1)

print(f"\nObserved {len(data_landscape)} sources across data directories:\n")

# Show landscape for each source
for source_name, source_info in sorted(data_landscape.items()):
    locations = source_info['locations']

    print(f"{source_name.upper()}:")

    for dir_type in data_directories:
        if dir_type in locations:
            loc = locations[dir_type]

            # Build type summary
            types = ', '.join(f"{count} {ext or 'no-ext'}"
                            for ext, count in sorted(loc['files_by_type'].items()))

            row_info = f", {loc['row_count']:,} records" if loc['row_count'] else ""

            print(f"  [{dir_type:10}] -> {loc['file_count']:4} files ({types}) = {loc['total_size_human']}{row_info}")

    print(f"  Available in {len(locations)} location(s)")
    print()

# Build context with ALL locations visible
# User can later select which locations to use
context_sources = {}

for source_name, source_info in data_landscape.items():
    locations = source_info['locations']

    # For now, use the LAST location found (processed > interim > external > raw)
    # But SHOW all locations in metadata
    selected_location = None
    for dir_type in ['processed', 'interim', 'external', 'raw']:
        if dir_type in locations:
            selected_location = dir_type
            break

    if selected_location:
        loc_data = locations[selected_location]

        context_sources[source_name] = {
            'name': source_name,
            'file_count': loc_data['file_count'],
            'total_size_bytes': loc_data['total_size_bytes'],
            'row_count': loc_data['row_count'],
            'description': f'{source_name.upper()} from {selected_location}/',
            'discovered': True,
            'location': loc_data['path'],
            'data_type': selected_location,
            'file_list': loc_data['file_list'],
            # CRITICAL: Include ALL locations for transparency
            'all_locations': {
                dir_type: {
                    'file_count': loc['file_count'],
                    'size': loc['total_size_human'],
                    'rows': loc['row_count'],
                    'types': loc['files_by_type']
                }
                for dir_type, loc in locations.items()
            }
        }

# Calculate totals
total_files = sum(s['file_count'] for s in context_sources.values())
total_size_bytes = sum(s['total_size_bytes'] for s in context_sources.values())
total_records = sum(s.get('row_count') or 0 for s in context_sources.values())

# Format total size
if total_size_bytes >= 1_000_000_000:
    total_size_str = f"{total_size_bytes / 1_000_000_000:.2f} GB"
elif total_size_bytes >= 1_000_000:
    total_size_str = f"{total_size_bytes / 1_000_000:.1f} MB"
else:
    total_size_str = f"{total_size_bytes / 1_000:.1f} KB"

print("=" * 70)
print("SELECTED FOR CONTEXT (defaults to processed > interim > raw)")
print("=" * 70)
print(f"\n{len(context_sources)} sources selected:")
for name, info in context_sources.items():
    row_str = f", {info['row_count']:,} records" if info['row_count'] else ""
    size_bytes = info['total_size_bytes']
    if size_bytes >= 1_000_000_000:
        size_str = f"{size_bytes / 1_000_000_000:.2f} GB"
    elif size_bytes >= 1_000_000:
        size_str = f"{size_bytes / 1_000_000:.1f} MB"
    else:
        size_str = f"{size_bytes / 1_000:.1f} KB"

    print(f"  - {name} ({info['data_type']}/): {info['file_count']} files, {size_str}{row_str}")

print(f"\nTotals: {total_files} files, {total_size_str}, {total_records:,} records")

# Build context
context = {
    'data_sources': context_sources,
    'summary': {
        'total_sources': len(context_sources),
        'total_files': total_files,
        'total_size_bytes': total_size_bytes,
        'total_size_human': total_size_str,
        'total_records': total_records,
        'discovery_method': 'landscape_neutral_observer',
        'data_location': str(data_root),
        'scanned_directories': data_directories
    },
    'initial_prompt': f"Create a dashboard showing data from all sources"
}

# Save context
print("\n" + "=" * 70)
print("SAVING CONTEXT")
print("=" * 70)

try:
    saved_path = PipelineState.save_context(context)
    print(f"\n[OK] Data landscape context saved!")
    print(f"     Location: {saved_path}")

    print("\n" + "=" * 70)
    print("READY FOR AGENT STUDIO")
    print("=" * 70)
    print("\nProtocol Layer will use this data:")
    print(f"  Sources: {list(context_sources.keys())}")
    print(f"  Files: {total_files}")
    print(f"  Size: {total_size_str}")
    print(f"  Records: {total_records:,}")
    print("\nNext step:")
    print("  Run: streamlit run src/ui/agent_studio.py")

except Exception as e:
    print(f"\n[ERROR] Failed to save context: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
