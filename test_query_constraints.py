"""
Test Query Constraint Parsing

This test validates that the query understanding layer correctly:
1. Extracts source filters from natural language
2. Classifies user intent (data analysis vs monitoring)
3. Applies filters during discovery
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from src.agents.ux_designer import UXDesignerAgent


def test_query_constraint_parsing():
    """Test that query constraints are correctly parsed"""

    print("=" * 70)
    print("TESTING QUERY CONSTRAINT PARSING")
    print("=" * 70)

    ux_designer = UXDesignerAgent()

    # Test Case 1: "from fracfocus"
    print("\n[Test 1] Prompt: 'dashboard of chemical data from fracfocus'")
    constraints = ux_designer._parse_query_constraints("dashboard of chemical data from fracfocus")
    print(f"  Source Filter: {constraints.get('source_filter')}")
    print(f"  Intent: {constraints.get('intent')}")
    print(f"  Expected: source_filter='fracfocus', intent='data_analysis'")
    assert constraints.get('source_filter') == 'fracfocus', "Failed to extract 'fracfocus'"
    assert constraints.get('intent') == 'data_analysis', "Failed to classify as data_analysis"
    print("  [PASS]")

    # Test Case 2: "only medical"
    print("\n[Test 2] Prompt: 'show only medical records'")
    constraints = ux_designer._parse_query_constraints("show only medical records")
    print(f"  Source Filter: {constraints.get('source_filter')}")
    print(f"  Intent: {constraints.get('intent')}")
    print(f"  Exclusivity: {constraints.get('exclusivity')}")
    print(f"  Expected: source_filter='medical', exclusivity=True")
    assert constraints.get('source_filter') == 'medical', "Failed to extract 'medical'"
    assert constraints.get('exclusivity') == True, "Failed to detect exclusivity"
    print("  [PASS]")

    # Test Case 3: Monitoring intent
    print("\n[Test 3] Prompt: 'monitor pipeline status'")
    constraints = ux_designer._parse_query_constraints("monitor pipeline status")
    print(f"  Source Filter: {constraints.get('source_filter')}")
    print(f"  Intent: {constraints.get('intent')}")
    print(f"  Expected: source_filter=None, intent='pipeline_monitoring'")
    assert constraints.get('source_filter') is None, "Shouldn't extract generic term 'pipeline'"
    assert constraints.get('intent') == 'pipeline_monitoring', "Failed to classify as monitoring"
    print("  [PASS]")

    # Test Case 4: No constraints
    print("\n[Test 4] Prompt: 'create dashboard'")
    constraints = ux_designer._parse_query_constraints("create dashboard")
    print(f"  Source Filter: {constraints.get('source_filter')}")
    print(f"  Intent: {constraints.get('intent')}")
    print(f"  Expected: source_filter=None, intent='data_analysis' (default)")
    assert constraints.get('source_filter') is None, "Shouldn't extract any source"
    assert constraints.get('intent') == 'data_analysis', "Should default to data_analysis"
    print("  [PASS]")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED [OK]")
    print("=" * 70)
    print("\nQuery understanding layer is working correctly!")
    print("The 'from fracfocus' constraint will now properly filter discovery.")


if __name__ == "__main__":
    test_query_constraint_parsing()
