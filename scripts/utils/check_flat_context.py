"""Check run_ingestion.py flat context structure"""
from shared_state import PipelineState

ctx = PipelineState.load_context(check_freshness=False)

print("="*80)
print("run_ingestion.py FLAT CONTEXT STRUCTURE")
print("="*80)
print(f"\nTotal entries: {len(ctx['data_sources'])}")
print()

for i, (name, data) in enumerate(ctx['data_sources'].items(), 1):
    status = data.get('status', 'unknown')
    display_name = data.get('display_name', name)
    print(f"{i:2}. {name:40} status={status:15} display={display_name}")

print()
print("="*80)
print("PROBLEM: This counts both parent dirs AND subdirs as separate entries!")
print("="*80)
