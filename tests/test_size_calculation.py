"""Test size calculation logic"""

import json

# Load context
with open('C:/Users/irina/.apex_eor/pipeline_state.json') as f:
    data = json.load(f)

context = data['context']
source_data = context['data_sources']['fracfocus_chemical_data']
dir_structure = source_data['directory_structure']

file_count = 0
total_size_bytes = 0

# Count files and size recursively - same logic as API
def count_files(node):
    global file_count, total_size_bytes
    if isinstance(node, dict):
        # Add this directory's file count
        if 'file_count' in node:
            file_count += node['file_count']
            print(f"  Found file_count={node['file_count']} at {node.get('path', 'unknown')}")
        # Sum up individual file sizes
        if 'files' in node and isinstance(node['files'], list):
            for file_info in node['files']:
                if isinstance(file_info, dict) and 'size_bytes' in file_info:
                    total_size_bytes += file_info['size_bytes']
                    print(f"    Adding file: {file_info['name']} = {file_info['size_bytes']} bytes")
        # Recurse into subdirectories
        if 'subdirs' in node:
            for subdir in node['subdirs'].values():
                count_files(subdir)

print("Testing size calculation for fracfocus_chemical_data:\n")
count_files(dir_structure)

print(f"\nRESULTS:")
print(f"  File count: {file_count}")
print(f"  Total size: {total_size_bytes:,} bytes")
print(f"  Total size: {total_size_bytes / 1_000_000_000:.2f} GB")

if total_size_bytes > 0:
    print("\n✅ Size calculation works!")
else:
    print("\n❌ Size calculation returned 0")
