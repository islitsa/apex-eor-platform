"""
Comprehensive Data Discovery - ALL file types, not just parquet

Discovers and catalogs ALL files across data directories:
- Parquet, CSV, JSON, Excel, YAML, text, logs, etc.
- Shows file counts by type and location
- Provides size metrics
- Generates complete inventory for context
"""

import sys
from pathlib import Path
from typing import Dict, List, Any

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from shared_state import PipelineState

# File types we can discover
DATA_EXTENSIONS = {
    '.parquet': 'parquet',
    '.csv': 'csv',
    '.tsv': 'tsv',
    '.json': 'json',
    '.jsonl': 'jsonlines',
    '.xlsx': 'excel',
    '.xls': 'excel',
    '.pkl': 'pickle',
    '.h5': 'hdf5',
    '.hdf': 'hdf5',
    '.feather': 'feather',
    '.yaml': 'config',
    '.yml': 'config',
    '.txt': 'text',
    '.log': 'log',
    '.md': 'markdown',
    '.xml': 'xml',
    '.html': 'html'
}

print("=" * 70)
print("COMPREHENSIVE FILE DISCOVERY")
print("=" * 70)
print("\nDiscovering ALL file types, not just parquet!")

# Scan ALL data directories
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

        # Find ALL files (not just parquet!)
        all_files = list(source_dir.rglob("*"))

        files_by_type = {}
        total_size_bytes = 0

        for file_path in all_files:
            if file_path.is_file():
                ext = file_path.suffix.lower()
                file_type = DATA_EXTENSIONS.get(ext, 'other')

                if file_type not in files_by_type:
                    files_by_type[file_type] = []

                try:
                    size_bytes = file_path.stat().st_size
                except Exception:
                    size_bytes = 0

                file_info = {
                    'name': file_path.name,
                    'size_bytes': size_bytes,
                    'extension': ext,
                    'relative_path': str(file_path.relative_to(source_dir))
                }
                files_by_type[file_type].append(file_info)
                total_size_bytes += size_bytes

        if not files_by_type:
            print(f"  No files found")
            continue

        # Show breakdown by file type
        total_files = sum(len(files) for files in files_by_type.values())
        print(f"  Found {total_files} files:")

        for file_type, files in sorted(files_by_type.items()):
            type_size = sum(f['size_bytes'] for f in files)

            # Format size
            if type_size >= 1_000_000_000:
                size_str = f"{type_size / 1_000_000_000:.2f} GB"
            elif type_size >= 1_000_000:
                size_str = f"{type_size / 1_000_000:.1f} MB"
            elif type_size >= 1_000:
                size_str = f"{type_size / 1_000:.1f} KB"
            else:
                size_str = f"{type_size} B"

            print(f"    - {len(files)} {file_type} files ({size_str})")

            # Show first few files for context
            for file_info in files[:3]:
                print(f"      • {file_info['relative_path']}")
            if len(files) > 3:
                print(f"      ... and {len(files) - 3} more")

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
            'file_count': total_files,
            'files_by_type': {
                file_type: len(files)
                for file_type, files in files_by_type.items()
            },
            'total_size_bytes': total_size_bytes,
            'description': f'{source_name.upper()} data ({total_files} files)',
            'discovered': True,
            'location': str(source_dir),
            'data_type': dir_type,
            # Store actual file list for ContextAdapter
            'file_list': [
                {'name': f['name'], 'size_bytes': f['size_bytes']}
                for files in files_by_type.values()
                for f in files
            ]
        }

print("\n" + "=" * 70)
print("DISCOVERY SUMMARY")
print("=" * 70)

if not discovered_sources:
    print("\n[ERROR] No data sources found!")
    print(f"Expected files in {data_root}/<directory>/<source_name>/")
    print(f"Searched directories: {', '.join(data_directories)}")
    sys.exit(1)

# Group by directory type for summary
by_dir_type = {}
for key, info in discovered_sources.items():
    dir_type = info['data_type']
    if dir_type not in by_dir_type:
        by_dir_type[dir_type] = []
    by_dir_type[dir_type].append((key, info))

print(f"\nDiscovered {len(discovered_sources)} sources across {len(by_dir_type)} directories:")

total_files = 0
total_size_bytes = 0

for dir_type in data_directories:
    if dir_type in by_dir_type:
        print(f"\n  [{dir_type.upper()}]")
        for name, info in by_dir_type[dir_type]:
            # Format size
            size_bytes = info['total_size_bytes']
            if size_bytes >= 1_000_000_000:
                size_str = f"{size_bytes / 1_000_000_000:.2f} GB"
            elif size_bytes >= 1_000_000:
                size_str = f"{size_bytes / 1_000_000:.1f} MB"
            else:
                size_str = f"{size_bytes / 1_000:.1f} KB"

            print(f"    - {info['name']}: {info['file_count']} files ({size_str})")

            # Show file type breakdown
            file_types = info['files_by_type']
            type_summary = ', '.join(f"{count} {ftype}" for ftype, count in sorted(file_types.items()))
            print(f"      Types: {type_summary}")

            total_files += info['file_count']
            total_size_bytes += size_bytes

# Format total size
if total_size_bytes >= 1_000_000_000:
    total_size_str = f"{total_size_bytes / 1_000_000_000:.2f} GB"
elif total_size_bytes >= 1_000_000:
    total_size_str = f"{total_size_bytes / 1_000_000:.1f} MB"
else:
    total_size_str = f"{total_size_bytes / 1_000:.1f} KB"

print(f"\nTotal: {total_files} files, {total_size_str}")

# Build context (note: we're NOT including row_count since we didn't read the files)
# The ContextAdapter will handle this
context = {
    'data_sources': discovered_sources,
    'summary': {
        'total_sources': len(discovered_sources),
        'total_files': total_files,
        'total_size_bytes': total_size_bytes,
        'total_size_human': total_size_str,
        'discovery_method': 'comprehensive_all_files',
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
    print(f"\n[OK] Comprehensive file context saved!")
    print(f"     Location: {saved_path}")

    print("\n" + "=" * 70)
    print("READY FOR AGENT STUDIO")
    print("=" * 70)
    print("\nProtocol Layer will use this comprehensive data:")
    print(f"  Sources: {list(discovered_sources.keys())}")
    print(f"  Total Files: {total_files}")
    print(f"  Total Size: {total_size_str}")
    print("\nNext step:")
    print("  Run: streamlit run src/ui/agent_studio.py")

except Exception as e:
    print(f"\n[ERROR] Failed to save context: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
