"""Explain why fracfocus has 37 files vs fracfocus/Chemical_data has 36 files"""

from pathlib import Path
import json

ctx = json.load(open(Path.home() / '.apex_eor' / 'pipeline_context.json'))

fracfocus = ctx['data_sources']['fracfocus']
frac_chem = ctx['data_sources']['fracfocus_chemical_data']

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
print("FRACFOCUS (parent dataset)")
print("=" * 80)
fracfocus_total = count_files_detailed(fracfocus['directory_structure'], 'fracfocus')
print(f"\n✅ Total: {fracfocus_total} files\n")

print("=" * 80)
print("FRACFOCUS / CHEMICAL_DATA (nested dataset)")
print("=" * 80)
frac_chem_total = count_files_detailed(frac_chem['directory_structure'], 'fracfocus/Chemical_data')
print(f"\n✅ Total: {frac_chem_total} files\n")

print("=" * 80)
print("EXPLANATION")
print("=" * 80)
print(f"""
The difference is {fracfocus_total - frac_chem_total} file(s).

FRACFOCUS (37 files) includes:
  - fracfocus/metadata.json (1 file at root level)
  - fracfocus/Chemical_data/* (36 files - all the data)

FRACFOCUS/CHEMICAL_DATA (36 files) includes:
  - fracfocus/Chemical_data/metadata.json (1 file)
  - fracfocus/Chemical_data/downloads/* (1 file - the zip)
  - fracfocus/Chemical_data/extracted/* (17 CSV files)
  - fracfocus/Chemical_data/parsed/* (17 CSV files - same as extracted)

So fracfocus has 1 EXTRA file at its root: fracfocus/metadata.json
""")
