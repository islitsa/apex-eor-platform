"""Test what the new hierarchical trace format will look like"""

import requests

r = requests.get('http://localhost:8000/api/pipelines')
data = r.json()

print("=" * 80)
print("NEW TRACE FORMAT - HIERARCHICAL PIPELINE BREAKDOWN")
print("=" * 80)
print()

for p in data['pipelines'][:3]:
    print(f"  >> {p['display_name']}")

    files_info = p.get('files', {})
    if files_info and 'subdirs' in files_info:
        subdirs = files_info.get('subdirs', {})

        for stage_name in ['downloads', 'extracted', 'parsed']:
            if stage_name in subdirs:
                stage = subdirs[stage_name]
                stage_files = len(stage.get('files', []))

                # Calculate size
                stage_size = sum(f.get('size_bytes', 0) for f in stage.get('files', []))

                if stage_size >= 1_000_000_000:
                    size_str = f"{stage_size / 1_000_000_000:.1f} GB"
                elif stage_size >= 1_000_000:
                    size_str = f"{stage_size / 1_000_000:.1f} MB"
                elif stage_size >= 1_000:
                    size_str = f"{stage_size / 1_000:.1f} KB"
                else:
                    size_str = f"{stage_size} B"

                nested_subdirs = len(stage.get('subdirs', {}))
                nested_note = f" (+ {nested_subdirs} nested dirs)" if nested_subdirs > 5 else ""

                print(f"     |-- {stage_name}: {stage_files} files, {size_str}{nested_note}")
    else:
        print(f"     |-- Total: {p['metrics']['file_count']} files, {p['metrics']['data_size']}")

    print()
