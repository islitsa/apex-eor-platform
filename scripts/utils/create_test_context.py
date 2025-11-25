"""
Create test context for Agent Studio with Protocol Layer

This creates a context with discovered data sources so Agent Studio
can test the Protocol layer integration.
"""

from shared_state import PipelineState
from pathlib import Path
import json

print("=" * 70)
print("Creating Test Context for Agent Studio")
print("=" * 70)

# Create test context with realistic data sources
test_context = {
    'data_sources': {
        'fracfocus': {
            'name': 'fracfocus',
            'row_count': 239059,
            'description': 'FracFocus Chemical Disclosure Registry',
            'discovered': True
        },
        'rrc': {
            'name': 'rrc',
            'row_count': 18200,
            'description': 'Railroad Commission of Texas',
            'discovered': True
        }
    },
    'summary': {
        'total_sources': 2,
        'total_records': 257259,
        'discovery_time': '2024-01-15T10:30:00',
        'discovery_method': 'manual_test_context'
    },
    'initial_prompt': 'Create a dashboard showing fracfocus and rrc data with filtering and visualizations'
}

print("\nTest Context:")
print(f"  Sources: {list(test_context['data_sources'].keys())}")
print(f"  Total records: {test_context['summary']['total_records']:,}")
print(f"  Initial prompt: {test_context['initial_prompt']}")

# Save it using PipelineState
try:
    PipelineState.save_context(test_context)
    print("\n[OK] Test context saved successfully!")
    print("\nContext location:")

    # Show where it was saved
    project_root = Path(__file__).parent
    context_file = project_root / "data" / "pipeline_context.json"
    if context_file.exists():
        print(f"  {context_file}")
        print(f"  Size: {context_file.stat().st_size} bytes")

    print("\nNext steps:")
    print("  1. Run: streamlit run src/ui/agent_studio.py")
    print("  2. Click 'Generate Initial UI'")
    print("  3. Watch for [Protocol] messages in console")
    print("  4. The Protocol layer will validate the context!")

except Exception as e:
    print(f"\n[ERROR] Failed to save context: {e}")
    print("\nManual save option:")
    print("  Create: data/pipeline_context.json")
    print("  Content:")
    print(json.dumps(test_context, indent=2))

print("\n" + "=" * 70)
