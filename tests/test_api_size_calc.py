"""Test API size calculation to find the 0 KB bug"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from shared_state import PipelineState

# Load context
context = PipelineState.load_context(check_freshness=False)

if not context:
    print("ERROR: No context found!")
    exit(1)

data_sources = context.get('data_sources', {})
source_id = 'fracfocus_chemical_data'
source_data = data_sources.get(source_id, {})

print("=" * 80)
print(f"TESTING SIZE CALCULATION FOR: {source_id}")
print("=" * 80)

# Reproduce the exact logic from data_service.py lines 480-520
dir_structure = source_data.get('directory_structure', {})
file_count = 0
total_size_bytes = 0

print(f"\nInitial dir_structure keys: {list(dir_structure.keys())}")
print(f"Initial file_count: {dir_structure.get('file_count')}")
print(f"Initial files: {len(dir_structure.get('files', []))}")

# Count files and size recursively - EXACT CODE FROM data_service.py
def count_files(node):
    global file_count, total_size_bytes
    if isinstance(node, dict):
        # Add this directory's file count
        if 'file_count' in node:
            print(f"  Adding file_count: {node['file_count']}")
            file_count += node['file_count']
        # Sum up individual file sizes
        if 'files' in node and isinstance(node['files'], list):
            for file_info in node['files']:
                if isinstance(file_info, dict) and 'size_bytes' in file_info:
                    print(f"    Adding file: {file_info['name']} - {file_info['size_bytes']:,} bytes")
                    total_size_bytes += file_info['size_bytes']
        # Recurse into subdirectories
        if 'subdirs' in node:
            for subdir_name, subdir in node['subdirs'].items():
                print(f"  Entering subdir: {subdir_name}")
                count_files(subdir)

count_files(dir_structure)

# Use calculated total size (line 506)
file_size_bytes = total_size_bytes

print(f"\n" + "=" * 80)
print(f"AFTER COUNTING:")
print(f"  file_count = {file_count}")
print(f"  total_size_bytes = {total_size_bytes:,}")
print(f"  file_size_bytes = {file_size_bytes:,}")

# Format file size (lines 512-520)
if file_size_bytes >= 1_000_000_000:
    data_size = f"{file_size_bytes / 1_000_000_000:.1f} GB"
elif file_size_bytes >= 1_000_000:
    data_size = f"{file_size_bytes / 1_000_000:.1f} MB"
elif file_size_bytes >= 1_000:
    data_size = f"{file_size_bytes / 1_000:.1f} KB"
else:
    data_size = f"{file_size_bytes} B"

print(f"\nFORMATTED:")
print(f"  data_size = {data_size}")

# Record count (lines 522-524)
record_count = 0  # HARDCODED TO 0!

print(f"  record_count = {record_count}")

# Final pipeline object (lines 526-538)
pipeline = {
    "id": source_id,
    "name": source_id,
    "display_name": source_data.get('display_name', source_id),
    "status": source_data.get('status', 'unknown'),
    "metrics": {
        "file_count": file_count,
        "record_count": record_count,
        "data_size": data_size
    }
}

print(f"\n" + "=" * 80)
print("FINAL PIPELINE OBJECT:")
print(f"  display_name: {pipeline['display_name']}")
print(f"  file_count: {pipeline['metrics']['file_count']}")
print(f"  record_count: {pipeline['metrics']['record_count']}")
print(f"  data_size: {pipeline['metrics']['data_size']}")
print("=" * 80)
