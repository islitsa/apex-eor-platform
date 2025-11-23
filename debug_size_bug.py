"""Quick test to reproduce the 0 B bug"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from shared_state import PipelineState

context = PipelineState.load_context(check_freshness=False)
data_sources = context.get('data_sources', {})

# Test fracfocus_chemical_data
source_id = 'fracfocus_chemical_data'
source_data = data_sources.get(source_id, {})

print(f"Testing: {source_id}")
print(f"Display name: {source_data.get('display_name')}")

dir_structure = source_data.get('directory_structure', {})
print(f"Has directory_structure: {bool(dir_structure)}")

if not dir_structure:
    print("ERROR: No directory_structure!")
    exit(1)

# Initialize variables
file_count = 0
total_size_bytes = 0

# Define the counting function
def count_files(node):
    global file_count, total_size_bytes
    if isinstance(node, dict):
        if 'file_count' in node:
            file_count += node['file_count']
        if 'files' in node and isinstance(node['files'], list):
            for file_info in node['files']:
                if isinstance(file_info, dict) and 'size_bytes' in file_info:
                    total_size_bytes += file_info['size_bytes']
        if 'subdirs' in node:
            for subdir in node['subdirs'].values():
                count_files(subdir)

# Run the count
count_files(dir_structure)

# Format the size
if total_size_bytes >= 1_000_000_000:
    data_size = f"{total_size_bytes / 1_000_000_000:.1f} GB"
elif total_size_bytes >= 1_000_000:
    data_size = f"{total_size_bytes / 1_000_000:.1f} MB"
elif total_size_bytes >= 1_000:
    data_size = f"{total_size_bytes / 1_000:.1f} KB"
else:
    data_size = f"{total_size_bytes} B"

print(f"\nRESULTS:")
print(f"  file_count: {file_count}")
print(f"  total_size_bytes: {total_size_bytes:,}")
print(f"  data_size: {data_size}")

# Now test what the actual API returns
print("\n" + "="*80)
print("COMPARING WITH LIVE API RESPONSE:")
print("="*80)

import requests
try:
    r = requests.get('http://localhost:8000/api/pipelines', timeout=2)
    data = r.json()
    frac_chem = next((p for p in data['pipelines'] if 'Chemical_data' in p.get('display_name', '')), None)
    if frac_chem:
        print(f"API returned: {frac_chem['metrics']['data_size']}")
        print(f"We calculated: {data_size}")
        print(f"\nMATCH: {frac_chem['metrics']['data_size'] == data_size}")
    else:
        print("fracfocus/Chemical_data not found in API response!")
except Exception as e:
    print(f"API error: {e}")
