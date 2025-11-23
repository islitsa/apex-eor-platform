"""
Direct test of API logic without HTTP
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from shared_state import PipelineState

# Load pipeline context (same as API does)
context = PipelineState.load_context(check_freshness=False)

if not context:
    print("ERROR: No context found!")
    sys.exit(1)

data_sources = context.get('data_sources', {})

print("="*80)
print("TESTING API LOGIC DIRECTLY")
print("="*80)

# Test with fracfocus (same logic as API)
source_id = 'fracfocus'
source_data = data_sources.get(source_id, {})

print(f"\n1. Source: {source_id}")
print(f"   Display name: {source_data.get('display_name', source_id)}")
print(f"   Status: {source_data.get('status', 'unknown')}")

# Get metrics from directory structure (SAME CODE AS API)
dir_structure = source_data.get('directory_structure', {})
file_count = 0
record_count = 0

# Count files recursively - sum up file_count from each directory
def count_files(node):
    global file_count
    if isinstance(node, dict):
        # Add this directory's file count
        if 'file_count' in node:
            fc = node['file_count']
            print(f"   Found file_count={fc} at path={node.get('path', 'unknown')}")
            file_count += fc
        # Recurse into subdirectories
        if 'subdirs' in node:
            for subdir in node['subdirs'].values():
                count_files(subdir)

print(f"\n2. Counting files:")
count_files(dir_structure)

print(f"\n3. RESULT: file_count = {file_count}")

# Also check what test_api_pipelines.py would see via HTTP
print(f"\n4. What the HTTP API would return:")
print(f"   - File count: {file_count}")
print(f"   - Expected: 37 (from debug_api_file_count.py)")

if file_count == 37:
    print("\n[OK] API logic is working correctly!")
else:
    print(f"\n[FAIL] API logic returned {file_count}, expected 37")

print("="*80)
