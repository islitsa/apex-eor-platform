"""Compare fracfocus vs rrc file structures"""

from pathlib import Path
import json

ctx = json.load(open(Path.home() / '.apex_eor' / 'pipeline_context.json'))
fracfocus = ctx['data_sources']['fracfocus']
rrc = ctx['data_sources']['rrc']

def count_by_level(node, name='root', level=0):
    indent = '  ' * level
    files = len(node.get('files', []))
    print(f'{indent}{name}: {files} files')

    total = files
    subdirs = node.get('subdirs', {})
    for subdir_name, subdir in subdirs.items():
        total += count_by_level(subdir, subdir_name, level + 1)

    return total

print("=" * 80)
print("FRACFOCUS - File Count Breakdown")
print("=" * 80)
f_total = count_by_level(fracfocus['directory_structure'], 'fracfocus')
print(f'\nTotal fracfocus: {f_total} files')

print("\n" + "=" * 80)
print("RRC - File Count Breakdown")
print("=" * 80)
r_total = count_by_level(rrc['directory_structure'], 'rrc')
print(f'\nTotal rrc: {r_total} files')

print("\n" + "=" * 80)
print("COMPARISON")
print("=" * 80)
print(f"""
FRACFOCUS:
  - Root level: 1 file (metadata.json)
  - Total recursive: {f_total} files

RRC:
  - Root level: 3 files (DATA_SUMMARY.md, QUICK_START.md, README.md)
  - Total recursive: {r_total} files

WHY DIFFERENT?
  Fracfocus has FEWER root files (1) but MORE total files ({f_total})
  because it has MORE data in subdirectories (Chemical_data/downloads/extracted/parsed).

  RRC has MORE root files (3) but the comparison depends on subdirectory contents.
""")
