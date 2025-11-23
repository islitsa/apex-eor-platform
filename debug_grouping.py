"""Debug dataset grouping logic"""
from shared_state import PipelineState

ctx = PipelineState.load_context(check_freshness=False)
data_sources = ctx['data_sources']

print("="*80)
print("DEBUGGING PARENT SOURCE GROUPING")
print("="*80)

sources_map = {}

for name, data in data_sources.items():
    display_name = data.get('display_name', name)
    status = data.get('status', '')

    print(f"\nProcessing: {name}")
    print(f"  Display: {display_name}")
    print(f"  Status: {status}")

    if '/' in display_name:
        # Child dataset
        parts = display_name.split('/')
        parent_source = parts[0].strip().lower().replace(' ', '_')
        print(f"  -> Child dataset of parent: {parent_source}")

        if parent_source not in sources_map:
            sources_map[parent_source] = []
        sources_map[parent_source].append({
            'name': name,
            'status': status
        })
    else:
        # Parent dir
        parent_source = name.lower().replace(' ', '_')
        print(f"  -> Parent dir: {parent_source}")

        if parent_source not in sources_map:
            sources_map[parent_source] = []

print("\n" + "="*80)
print("GROUPED BY PARENT SOURCE")
print("="*80)

total_datasets = 0
for parent, datasets in sorted(sources_map.items()):
    print(f"\n{parent}: {len(datasets)} dataset(s)")
    for ds in datasets:
        if ds['status'] == 'processed':
            print(f"  ✓ {ds['name']} (processed)")
            total_datasets += 1
        else:
            print(f"  - {ds['name']} ({ds['status']})")

print("\n" + "="*80)
print(f"Total processed datasets: {total_datasets}")
print("="*80)
