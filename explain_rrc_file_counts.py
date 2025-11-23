"""Explain RRC file counts - why parent has 345 files vs nested datasets"""

from pathlib import Path
import json

ctx = json.load(open(Path.home() / '.apex_eor' / 'pipeline_context.json'))

rrc = ctx['data_sources']['rrc']
rrc_comp = ctx['data_sources']['rrc_completions_data']
rrc_horiz = ctx['data_sources']['rrc_horizontal_drilling_permits']
rrc_prod = ctx['data_sources']['rrc_production']

def count_files_detailed(node, path='', level=0):
    """Count files and show breakdown"""
    indent = "  " * level
    total = 0

    if isinstance(node, dict):
        # Files at this level
        files = node.get('files', [])
        if files:
            print(f"{indent}{path}: {len(files)} files")
            total += len(files)

        # Recurse into subdirs
        subdirs = node.get('subdirs', {})
        for name, subdir in subdirs.items():
            subpath = f"{path}/{name}" if path else name
            total += count_files_detailed(subdir, subpath, level + 1)

    return total

print("=" * 80)
print("RRC (PARENT) - Contains all RRC data")
print("=" * 80)
rrc_total = count_files_detailed(rrc['directory_structure'], 'rrc')
print(f"\nTotal: {rrc_total} files")

print("\n" + "=" * 80)
print("RRC / COMPLETIONS_DATA (nested)")
print("=" * 80)
comp_total = count_files_detailed(rrc_comp['directory_structure'], 'rrc/completions_data')
print(f"\nTotal: {comp_total} files")

print("\n" + "=" * 80)
print("RRC / HORIZONTAL_DRILLING_PERMITS (nested)")
print("=" * 80)
horiz_total = count_files_detailed(rrc_horiz['directory_structure'], 'rrc/horizontal_drilling_permits')
print(f"\nTotal: {horiz_total} files")

print("\n" + "=" * 80)
print("RRC / PRODUCTION (nested)")
print("=" * 80)
prod_total = count_files_detailed(rrc_prod['directory_structure'], 'rrc/production')
print(f"\nTotal: {prod_total} files")

print("\n" + "=" * 80)
print("BREAKDOWN")
print("=" * 80)
print(f"""
RRC (parent) has {rrc_total} files total, which includes:
  - completions_data: {comp_total} files
  - horizontal_drilling_permits: {horiz_total} files
  - production: {prod_total} files
  - Other files (root + metadata): {rrc_total - comp_total - horiz_total - prod_total} files

Expected if summing nested: {comp_total} + {horiz_total} + {prod_total} = {comp_total + horiz_total + prod_total}
Actual parent count: {rrc_total}
Difference: {rrc_total - (comp_total + horiz_total + prod_total)} files (likely root metadata files)
""")
