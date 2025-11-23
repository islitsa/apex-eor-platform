"""
Debug script to understand why API shows 0 files
"""

import json
from pathlib import Path

# Load the context
context_file = Path.home() / '.apex_eor' / 'pipeline_state.json'

with open(context_file) as f:
    data = json.load(f)

context = data.get('context', {})
data_sources = context.get('data_sources', {})

print("="*80)
print("DEBUGGING FILE COUNT CALCULATION")
print("="*80)

# Test with fracfocus
source_id = 'fracfocus'
source_data = data_sources.get(source_id, {})

print(f"\n1. Source: {source_id}")
print(f"   Has directory_structure: {'directory_structure' in source_data}")

dir_structure = source_data.get('directory_structure', {})

print(f"\n2. Directory structure keys: {list(dir_structure.keys())}")
print(f"   Top level file_count: {dir_structure.get('file_count', 'NOT FOUND')}")
print(f"   Top level subdirs: {list(dir_structure.get('subdirs', {}).keys())}")

# Test the actual counting logic from the API
file_count = 0

def count_files(node):
    global file_count
    if isinstance(node, dict):
        # Add this directory's file count
        if 'file_count' in node:
            print(f"   Found file_count={node['file_count']} at path={node.get('path', 'unknown')}")
            file_count += node['file_count']
        # Recurse into subdirectories
        if 'subdirs' in node:
            for subdir in node['subdirs'].values():
                count_files(subdir)

print(f"\n3. Counting files recursively:")
count_files(dir_structure)

print(f"\n4. TOTAL FILE COUNT: {file_count}")

# Also check Chemical_data specifically
print(f"\n5. Checking fracfocus_chemical_data:")
chem_data = data_sources.get('fracfocus_chemical_data', {})
print(f"   Exists: {bool(chem_data)}")
if chem_data:
    chem_structure = chem_data.get('directory_structure', {})
    chem_file_count = 0

    def count_chem_files(node):
        global chem_file_count
        if isinstance(node, dict):
            if 'file_count' in node:
                chem_file_count += node['file_count']
            if 'subdirs' in node:
                for subdir in node['subdirs'].values():
                    count_chem_files(subdir)

    count_chem_files(chem_structure)
    print(f"   File count: {chem_file_count}")

print("\n" + "="*80)
