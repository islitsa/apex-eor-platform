"""Count processed datasets in saved context"""
from shared_state import PipelineState

ctx = PipelineState.load_context(check_freshness=False)

processed = []
for name, data in ctx['data_sources'].items():
    if data.get('status') == 'processed' and '/' in data.get('display_name', ''):
        processed.append(name)

print('Processed datasets with slash in display_name (actual child datasets):')
for ds in processed:
    print(f'  - {ds}')

print(f'\nTotal: {len(processed)} datasets')
print()
print('Expected: 4 datasets (fracfocus_chemical_data + 3 rrc datasets)')
print('Note: usgs/produced_water is NOT in the saved context!')
