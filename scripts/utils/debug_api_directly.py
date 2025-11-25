"""Debug API /pipelines endpoint directly - bypass HTTP server"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from shared_state import PipelineState

print("=" * 80)
print("DIRECT API LOGIC TEST - BYPASSING HTTP SERVER")
print("=" * 80)

# Load context (same as API does)
context = PipelineState.load_context(check_freshness=False)

if not context:
    print("ERROR: No context!")
    exit(1)

data_sources = context.get('data_sources', {})

print(f"\nTotal data sources in context: {len(data_sources)}")
print(f"Data source IDs: {list(data_sources.keys())}\n")

# Test the EXACT logic from data_service.py get_pipelines() endpoint
pipelines = []

for source_id, source_data in data_sources.items():
    # Only show fracfocus_chemical_data for now
    if 'chemical' not in source_id.lower() and 'fracfocus' not in source_id.lower():
        continue

    print(f"\n{'='*80}")
    print(f"Processing: {source_id}")
    print(f"{'='*80}")

    display_name = source_data.get('display_name', source_id)
    status = source_data.get('status', 'unknown')

    # Get directory structure
    dir_structure = source_data.get('directory_structure', {})

    print(f"Display name: {display_name}")
    print(f"Status: {status}")
    print(f"Has directory_structure: {bool(dir_structure)}")

    if dir_structure:
        print(f"Dir structure keys: {list(dir_structure.keys())}")
        print(f"Dir structure type: {dir_structure.get('type')}")
        print(f"Dir structure has files: {'files' in dir_structure}")
        print(f"Dir structure has subdirs: {'subdirs' in dir_structure}")

    # Initialize counters
    file_count = 0
    total_size_bytes = 0

    print("\n--- Starting recursive count ---")

    # EXACT COUNT LOGIC FROM data_service.py - must be defined in same scope as counters
    if dir_structure and isinstance(dir_structure, dict):
        # Recursive function to count files and sizes
        def count_files(node, level=0):
            nonlocal file_count, total_size_bytes
            indent = "  " * level

            if isinstance(node, dict):
                # Add this directory's file count
                if 'file_count' in node:
                    print(f"{indent}[count_files] Adding file_count: {node['file_count']}")
                    file_count += node['file_count']

                # Sum up individual file sizes
                if 'files' in node and isinstance(node['files'], list):
                    print(f"{indent}[count_files] Processing {len(node['files'])} files in files array")
                    for file_info in node['files']:
                        if isinstance(file_info, dict) and 'size_bytes' in file_info:
                            print(f"{indent}  - {file_info['name']}: {file_info['size_bytes']:,} bytes")
                            total_size_bytes += file_info['size_bytes']

                # Recurse into subdirectories
                if 'subdirs' in node:
                    print(f"{indent}[count_files] Recursing into {len(node['subdirs'])} subdirs")
                    for subdir_name, subdir in node['subdirs'].items():
                        print(f"{indent}[count_files] Entering subdir: {subdir_name}")
                        count_files(subdir, level + 1)

        count_files(dir_structure)
    else:
        print("  [WARNING] No valid directory_structure to count!")

    print("--- Finished recursive count ---\n")

    file_size_bytes = total_size_bytes

    # Format size (EXACT logic from data_service.py)
    if file_size_bytes >= 1_000_000_000:
        data_size = f"{file_size_bytes / 1_000_000_000:.1f} GB"
    elif file_size_bytes >= 1_000_000:
        data_size = f"{file_size_bytes / 1_000_000:.1f} MB"
    elif file_size_bytes >= 1_000:
        data_size = f"{file_size_bytes / 1_000:.1f} KB"
    else:
        data_size = f"{file_size_bytes} B"

    print(f"\nFINAL RESULTS:")
    print(f"  file_count: {file_count}")
    print(f"  total_size_bytes: {total_size_bytes:,}")
    print(f"  data_size: {data_size}")

    pipeline = {
        "id": source_id,
        "display_name": display_name,
        "metrics": {
            "file_count": file_count,
            "data_size": data_size
        }
    }
    pipelines.append(pipeline)

print("\n" + "=" * 80)
print("SUMMARY OF ALL PIPELINES")
print("=" * 80)
for p in pipelines:
    print(f"{p['display_name']}: {p['metrics']['file_count']} files, {p['metrics']['data_size']}")
