"""
Test UX Designer fix - verify component parsing from design reasoning
"""
from src.agents.ux_designer import UXDesignerAgent

# Sample design reasoning with COMPONENTS section
sample_reasoning = """
LAYOUT: Grid-based layout with emphasis on visual hierarchy

COMPONENTS:
- SummaryStats: Display key metrics (files, records, size) with Material Symbols icons
- NavigationSidebar: Allow users to drill down into data hierarchy with breadcrumbs
- StageOverview: Show pipeline stages with progress bars and status indicators
- PipelineCards: Display individual pipelines in expandable card format with file browsers
- DataTable: Show detailed records with sorting and filtering capabilities

ICONS: Use Material Symbols Rounded for all icons

INTERACTIONS:
- Click to expand pipeline cards
- Hover for tooltips
- Drill-down navigation with breadcrumbs

VISUAL HIERARCHY: Bold headers, clear spacing, card-based layout
"""

def test_component_parsing():
    """Test that components are parsed from reasoning"""
    print("Testing UX Designer component parsing fix...\n")

    # Create agent (without needing API key for this test)
    try:
        agent = UXDesignerAgent()
    except ValueError:
        # API key not needed for parsing test
        print("Note: Skipping API initialization for parsing test\n")
        # Create minimal agent instance for testing parsing
        from unittest.mock import Mock
        agent = Mock(spec=UXDesignerAgent)
        agent._parse_components_from_reasoning = UXDesignerAgent._parse_components_from_reasoning.__get__(agent)
        agent._infer_component_type = UXDesignerAgent._infer_component_type.__get__(agent)
        agent._infer_pattern = UXDesignerAgent._infer_pattern.__get__(agent)
        agent._extract_features = UXDesignerAgent._extract_features.__get__(agent)

    # Test parsing
    components = agent._parse_components_from_reasoning(sample_reasoning)

    print(f"[OK] Parsed {len(components)} components from reasoning:\n")

    for i, comp in enumerate(components, 1):
        print(f"{i}. {comp['name']}")
        print(f"   Type: {comp['type']}")
        print(f"   Pattern: {comp['pattern']}")
        print(f"   Features: {comp['features']}")
        print(f"   Intent: {comp['intent'][:60]}...")
        print()

    # Verify we got all 5 components
    assert len(components) == 5, f"Expected 5 components, got {len(components)}"

    # Verify component names
    expected_names = ['SummaryStats', 'NavigationSidebar', 'StageOverview', 'PipelineCards', 'DataTable']
    actual_names = [c['name'] for c in components]

    for expected in expected_names:
        assert expected in actual_names, f"Missing component: {expected}"

    print("[OK] All tests passed! UX Designer now parses components from design reasoning.\n")
    print("Before fix: Only 1 component (hardcoded DataDisplay)")
    print(f"After fix: {len(components)} components (parsed from LLM reasoning)")

if __name__ == "__main__":
    test_component_parsing()
