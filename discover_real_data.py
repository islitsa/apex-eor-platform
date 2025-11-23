"""
Real Data Discovery - Scan actual data files and create context

Scans data/interim/ for real parquet files and builds a context
with actual row counts for Agent Studio.
"""

import sys
from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from shared_state import PipelineState

print("=" * 70)
print("REAL DATA DISCOVERY")
print("=" * 70)

# Scan ALL data directories for sources (raw, external, interim, processed)
data_root = project_root / "data"
data_directories = ['raw', 'external', 'interim', 'processed']

if not data_root.exists():
    print(f"\n[ERROR] Data root not found: {data_root}")
    sys.exit(1)

print(f"\nScanning ALL data directories in: {data_root}")
print(f"Directories: {', '.join(data_directories)}")

discovered_sources = {}

# Scan each data directory type
for dir_type in data_directories:
    data_dir = data_root / dir_type

    if not data_dir.exists():
        print(f"\n[SKIP] {dir_type}/ does not exist")
        continue

    print(f"\n{'='*70}")
    print(f"SCANNING: {dir_type.upper()}/")
    print(f"{'='*70}")

    # Scan each source subdirectory
    for source_dir in data_dir.iterdir():
        if not source_dir.is_dir():
            continue

        source_name = source_dir.name

        print(f"\n[Discovering] {source_name} ({dir_type})...")

        # Find parquet files in this source
        parquet_files = list(source_dir.glob("**/*.parquet"))  # Recursive search

        if not parquet_files:
            print(f"  No parquet files found")
            continue

        # Count total rows across all files
        total_rows = 0
        file_count = 0

        for pq_file in parquet_files:
            try:
                df = pd.read_parquet(pq_file)
                rows = len(df)
                total_rows += rows
                file_count += 1
                # Show relative path from source dir
                rel_path = pq_file.relative_to(source_dir)
                print(f"  {rel_path}: {rows:,} rows")
            except Exception as e:
                print(f"  [WARN] Could not read {pq_file.name}: {e}")

        if total_rows > 0:
            # Preference order: processed > interim > external > raw
            dir_priority = {'processed': 4, 'interim': 3, 'external': 2, 'raw': 1}

            # Check if source already exists from another directory
            if source_name in discovered_sources:
                existing_priority = dir_priority.get(discovered_sources[source_name]['data_type'], 0)
                current_priority = dir_priority.get(dir_type, 0)

                if current_priority > existing_priority:
                    print(f"  [OVERRIDE] Preferring {dir_type} over {discovered_sources[source_name]['data_type']}")
                else:
                    print(f"  [SKIP] Already have {source_name} from {discovered_sources[source_name]['data_type']} (higher priority)")
                    continue

            # Use source_name directly (no suffix!)
            discovered_sources[source_name] = {
                'name': source_name,
                'row_count': total_rows,
                'file_count': file_count,
                'description': f'{source_name.upper()} data ({file_count} files)',
                'discovered': True,
                'location': str(source_dir),
                'data_type': dir_type  # Track which directory this came from
            }
            print(f"  TOTAL: {total_rows:,} rows across {file_count} files")

print("\n" + "=" * 70)
print("DISCOVERY SUMMARY")
print("=" * 70)

if not discovered_sources:
    print("\n[ERROR] No data sources found!")
    print(f"Expected parquet files in {data_root}/<directory>/<source_name>/")
    print(f"Searched directories: {', '.join(data_directories)}")
    sys.exit(1)

total_records = sum(s['row_count'] for s in discovered_sources.values())

# Group by directory type for summary
by_dir_type = {}
for key, info in discovered_sources.items():
    dir_type = info['data_type']
    if dir_type not in by_dir_type:
        by_dir_type[dir_type] = []
    by_dir_type[dir_type].append((key, info))

print(f"\nDiscovered {len(discovered_sources)} sources across {len(by_dir_type)} directories:")
for dir_type in data_directories:
    if dir_type in by_dir_type:
        print(f"\n  [{dir_type.upper()}]")
        for name, info in by_dir_type[dir_type]:
            print(f"    - {info['name']}: {info['row_count']:,} records ({info['file_count']} files)")

print(f"\nTotal records across all directories: {total_records:,}")

# Build context
context = {
    'data_sources': discovered_sources,
    'summary': {
        'total_sources': len(discovered_sources),
        'total_records': total_records,
        'discovery_method': 'real_data_discovery_all',
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
    print(f"\n[OK] Real data context saved!")
    print(f"     Location: {saved_path}")

    print("\n" + "=" * 70)
    print("READY FOR AGENT STUDIO")
    print("=" * 70)
    print("\nProtocol Layer will use this real data:")
    print(f"  Sources: {list(discovered_sources.keys())}")
    print(f"  Records: {total_records:,}")
    print("\nNext step:")
    print("  Run: streamlit run src/ui/agent_studio.py")
    print("\nWatch for:")
    print("  [Orchestrator] Building SessionContext...")
    print("  [Protocol] Filtered sources by scope...")

except Exception as e:
    print(f"\n[ERROR] Failed to save context: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
