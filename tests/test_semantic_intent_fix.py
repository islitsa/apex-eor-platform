"""
Test the semantic intent parsing fix for Phase 1.6

This verifies that "production data from rrc" correctly maps to:
  source: "rrc"
  domain: "production"
NOT sources: ["rrc", "production"]
"""

from src.agents.tools.filter_tool import DataFilterTool


def test_production_data_from_rrc():
    """
    CRITICAL TEST: User prompt "production data from rrc"
    Should filter to RRC only, NOT both RRC and production pipeline
    """
    filter_tool = DataFilterTool()

    # User's exact prompt
    prompt = "pls generate a dashboard of production data from rrc"

    # Available sources (including the problematic "production" pipeline)
    all_sources = ["rrc", "production", "fracfocus", "injection", "allocations"]

    # Parse intent
    intent = filter_tool.parse_intent(prompt, all_sources)

    print("\n" + "="*70)
    print("TEST: Semantic Intent Parsing Fix (Phase 1.6)")
    print("="*70)
    print(f"\nPrompt: {prompt}")
    print(f"Available sources: {all_sources}")
    print(f"\nParsed intent:")
    print(f"  source: {intent.get('source')}")
    print(f"  domain: {intent.get('domain')}")
    print(f"  is_multi_source: {intent.get('is_multi_source')}")

    # Get filtered sources
    filtered_sources = filter_tool.filter_by_prompt(prompt, all_sources)

    print(f"\nFiltered sources: {filtered_sources}")

    # Verify correctness
    print("\n" + "-"*70)
    print("VERIFICATION:")
    print("-"*70)

    assert intent.get('source') == 'rrc', f"Expected source='rrc', got {intent.get('source')}"
    assert intent.get('domain') == 'production', f"Expected domain='production', got {intent.get('domain')}"
    assert not intent.get('is_multi_source'), "Should be single source, not multi-source"
    assert filtered_sources == ['rrc'], f"Expected ['rrc'], got {filtered_sources}"

    print("PASS: 'production data from rrc' -> source='rrc' (production pipeline excluded)")
    print("Domain correctly identified as 'production' (data context, not pipeline)")
    print("\n" + "="*70 + "\n")


def test_multi_source_request():
    """
    Test that explicit multi-source requests still work
    """
    filter_tool = DataFilterTool()

    prompt = "show me rrc and production pipelines"
    all_sources = ["rrc", "production", "fracfocus"]

    intent = filter_tool.parse_intent(prompt, all_sources)
    filtered_sources = filter_tool.filter_by_prompt(prompt, all_sources)

    print("\n" + "="*70)
    print("TEST: Multi-Source Request")
    print("="*70)
    print(f"\nPrompt: {prompt}")
    print(f"Filtered sources: {filtered_sources}")

    assert intent.get('is_multi_source') == True, "Should detect multi-source request"
    assert set(filtered_sources) == {'rrc', 'production'}, f"Expected both sources, got {filtered_sources}"

    print("PASS: Multi-source requests still work correctly")
    print("\n" + "="*70 + "\n")


def test_production_pipeline_explicit():
    """
    Test that explicit "production pipeline" requests still work
    """
    filter_tool = DataFilterTool()

    prompt = "show me the production pipeline"
    all_sources = ["rrc", "production", "fracfocus"]

    intent = filter_tool.parse_intent(prompt, all_sources)
    filtered_sources = filter_tool.filter_by_prompt(prompt, all_sources)

    print("\n" + "="*70)
    print("TEST: Explicit Production Pipeline Request")
    print("="*70)
    print(f"\nPrompt: {prompt}")
    print(f"Filtered sources: {filtered_sources}")

    assert intent.get('source') == 'production', "Should match production pipeline when explicit"
    assert filtered_sources == ['production'], f"Expected ['production'], got {filtered_sources}"

    print("PASS: Explicit 'production pipeline' request works")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    print("\n*** PHASE 1.6: SEMANTIC INTENT PARSING FIX ***")
    print("Goal: Distinguish SOURCE vs DOMAIN in user prompts\n")

    test_production_data_from_rrc()
    test_multi_source_request()
    test_production_pipeline_explicit()

    print("="*70)
    print("ALL TESTS PASSED")
    print("="*70)
    print("\nThe semantic intent parser correctly handles:")
    print("   1. 'production data from X' -> source=X, domain=production")
    print("   2. 'X and Y pipelines' -> sources=[X, Y]")
    print("   3. 'production pipeline' -> source=production")
    print("\nThis fixes the root cause of the hallucination/convergence issues!")
    print("="*70 + "\n")
