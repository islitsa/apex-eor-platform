"""
Test that gradient hints are generated correctly
"""
import sys
import io

# Fix Unicode encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.agents.react_developer import ReactDeveloperAgent

print("="*80)
print("TESTING GRADIENT HINTS GENERATION")
print("="*80)

# Create agent
agent = ReactDeveloperAgent(styling_framework="tailwind")

# Mock gradient context (like orchestrator creates)
gradient_context = {
    'domain_signals': {
        'domain': 'petroleum_energy',
        'structure': 'nested_directories',
        'keywords': ['fracfocus', 'rrc', 'chemical', 'completion'],
        'data_types': ['chemical_data', 'operational_data'],
        'metrics': {
            'max_depth': 3,
            'total_files': 37
        }
    },
    'boost_hierarchical_navigation': True,
    'boost_tree_views': False,
    'boost_data_drill_down': True
}

# Test hint generation
hints = agent._build_gradient_hints(gradient_context)

print("\n✓ Gradient hints generated:")
print("-"*80)
print(hints)
print("-"*80)

# Check that key hints are present
checks = [
    ("Domain mentioned", "petroleum_energy" in hints),
    ("Structure mentioned", "nested_directories" in hints),
    ("Depth mentioned", "3 levels deep" in hints),
    ("Files mentioned", "37 total files" in hints),
    ("Hierarchical nav boosted", "HIERARCHICAL NAVIGATION BOOSTED" in hints),
    ("Tree views NOT boosted", "TREE/ACCORDION VIEWS BOOSTED" not in hints),
    ("Drill-down boosted", "DATA DRILL-DOWN BOOSTED" in hints),
    ("Nested data handling", "NESTED DATA HANDLING" in hints),
    ("Array access hint", "pipeline.files.subdirs['dir_name'].files[0]" in hints),
]

print("\n✅ Verification:")
for check_name, result in checks:
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"  {status} - {check_name}")

print("\n" + "="*80)
if all(result for _, result in checks):
    print("✅ ALL TESTS PASSED - Gradient hints working!")
else:
    print("❌ SOME TESTS FAILED - Check implementation")
print("="*80)
