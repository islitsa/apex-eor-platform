"""Debug pipeline structure to find where file sizes are stored"""

from pathlib import Path
import json

ctx_file = Path.home() / '.apex_eor' / 'pipeline_context.json'

if not ctx_file.exists():
    print("ERROR: Context file not found!")
    exit(1)

data = json.load(open(ctx_file))
fracfocus = data.get('data_sources', {}).get('fracfocus', {})

print("=" * 80)
print("FRACFOCUS DIRECTORY STRUCTURE")
print("=" * 80)

# Root level
root = fracfocus.get('directory_structure', {})
print(f"\nRoot level:")
print(f"  - Files: {len(root.get('files', []))}")
print(f"  - file_count: {root.get('file_count')}")
print(f"  - Subdirs: {list(root.get('subdirs', {}).keys())}")

# Chemical_data level
chem_data = root.get('subdirs', {}).get('Chemical_data', {})
print(f"\nChemical_data level:")
print(f"  - Files: {len(chem_data.get('files', []))}")
print(f"  - file_count: {chem_data.get('file_count')}")
print(f"  - Subdirs: {list(chem_data.get('subdirs', {}).keys())}")

# Check for parsed subdirectory
if 'parsed' in chem_data.get('subdirs', {}):
    parsed = chem_data['subdirs']['parsed']
    print(f"\nChemical_data/parsed level:")
    print(f"  - Files: {len(parsed.get('files', []))}")
    print(f"  - file_count: {parsed.get('file_count')}")

    if parsed.get('files'):
        print(f"\n  Sample file from parsed:")
        print(f"    {json.dumps(parsed['files'][0], indent=4)}")

        # Calculate total size
        total_size = sum(f.get('size_bytes', 0) for f in parsed.get('files', []))
        print(f"\n  Total size in parsed: {total_size:,} bytes ({total_size / 1e9:.2f} GB)")
else:
    # Check other subdirs
    for subdir_name, subdir in chem_data.get('subdirs', {}).items():
        print(f"\n{subdir_name}:")
        print(f"  - Files: {len(subdir.get('files', []))}")
        print(f"  - file_count: {subdir.get('file_count')}")
        print(f"  - Subdirs: {list(subdir.get('subdirs', {}).keys())}")

print("\n" + "=" * 80)
print("TESTING SIZE CALCULATION LOGIC")
print("=" * 80)

def count_files_recursive(node, level=0):
    """Recursively count files and sizes"""
    indent = "  " * level
    total_files = 0
    total_bytes = 0

    if isinstance(node, dict):
        # This node's file count
        node_file_count = node.get('file_count', 0)

        # Sum file sizes from files array
        files = node.get('files', [])
        for file_info in files:
            if isinstance(file_info, dict) and 'size_bytes' in file_info:
                total_bytes += file_info['size_bytes']

        print(f"{indent}Node: file_count={node_file_count}, files_array={len(files)}, bytes_from_files={total_bytes}")

        total_files += node_file_count

        # Recurse into subdirs
        subdirs = node.get('subdirs', {})
        for subdir_name, subdir in subdirs.items():
            print(f"{indent}Entering subdir: {subdir_name}")
            sub_files, sub_bytes = count_files_recursive(subdir, level + 1)
            total_files += sub_files
            total_bytes += sub_bytes

    return total_files, total_bytes

print("\nRecursive count for FracFocus:")
total_f, total_b = count_files_recursive(root)
print(f"\nFinal totals:")
print(f"  - Total files: {total_f}")
print(f"  - Total bytes: {total_b:,} ({total_b / 1e9:.2f} GB)")
