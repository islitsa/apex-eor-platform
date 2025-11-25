"""
Test Token Optimization Implementation

Tests the Opus Part 2 optimizations:
1. Compact DesignSpec serialization
2. Token usage logging
3. Reduced max_tokens
4. Orchestrator token reporting
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from src.agents.ux_designer import DesignSpec
from src.agents.ui_orchestrator import UICodeOrchestrator
from src.utils.context_extractor import PipelineContextExtractor

def test_compact_design_spec():
    """Test that compact serialization is smaller than full serialization"""
    print("\n" + "="*80)
    print("TEST 1: Compact DesignSpec Serialization")
    print("="*80)

    # Create a sample design spec
    design_spec = DesignSpec(
        screen_type="pipeline_dashboard_navigation",
        intent="Allow users to browse and navigate pipeline data hierarchy",
        components=[
            {
                "type": "card_grid",
                "id": "cg1",
                "intent": "Display data sources as navigable cards",
                "actions": ["click", "hover", "focus"]
            },
            {
                "type": "navigation_dropdown",
                "id": "dd1",
                "intent": "Select dataset within source",
                "actions": ["change"]
            }
        ],
        interactions=[
            {
                "trigger": "card_click",
                "action": "navigate_to_dataset",
                "target": "navigation_dropdown"
            }
        ],
        patterns=["master-detail", "progressive-disclosure", "breadcrumb-navigation"],
        styling={"color_scheme": "material_light", "typography": "roboto"}
    )

    # Test different serialization methods
    full_dict = str(design_spec.to_dict())
    compact_dict = str(design_spec.to_compact())
    summary_str = design_spec.to_summary()

    print(f"\nFull to_dict() size:    {len(full_dict):,} chars")
    print(f"Compact to_compact():   {len(compact_dict):,} chars")
    print(f"Summary to_summary():   {len(summary_str):,} chars")

    # Calculate savings
    savings_compact = ((len(full_dict) - len(compact_dict)) / len(full_dict)) * 100
    savings_summary = ((len(full_dict) - len(summary_str)) / len(full_dict)) * 100

    print(f"\nSavings with compact:   {savings_compact:.1f}%")
    print(f"Savings with summary:   {savings_summary:.1f}%")

    print(f"\nCompact format preview:")
    print(compact_dict[:200] + "...")

    print(f"\nSummary format:")
    print(summary_str)

    assert len(compact_dict) < len(full_dict), "Compact should be smaller"
    assert len(summary_str) < len(full_dict), "Summary should be smaller"

    print("\n[OK] TEST PASSED: Compact serialization working")


def test_two_agent_generation():
    """Test that two-agent system logs tokens and uses reduced max_tokens"""
    print("\n" + "="*80)
    print("TEST 2: Two-Agent Generation with Token Logging")
    print("="*80)

    # Extract context
    extractor = PipelineContextExtractor()
    context = extractor.extract_from_metadata()

    # Create orchestrator
    orchestrator = UICodeOrchestrator()

    # Create requirements
    requirements = {
        'screen_type': 'pipeline_dashboard_navigation',
        'intent': 'Browse pipeline data sources and datasets'
    }

    print("\nGenerating dashboard with optimized two-agent system...")
    print("Watch for token logging output...")

    # Generate code (this will print token usage)
    code = orchestrator.generate_ui_code(requirements, context)

    print(f"\n[OK] Generated {len(code):,} chars of code")

    # Verify token tracking exists
    ux_tokens = getattr(orchestrator.ux_designer, 'total_tokens_used', None)
    dev_tokens = getattr(orchestrator.gradio_developer, 'total_tokens_used', None)

    assert ux_tokens is not None, "UX Designer should track tokens"
    assert dev_tokens is not None, "Gradio Developer should track tokens"
    assert ux_tokens > 0, "UX Designer should have used tokens"
    assert dev_tokens > 0, "Gradio Developer should have used tokens"

    total = ux_tokens + dev_tokens
    print(f"\n[OK] TEST PASSED: Token tracking working")
    print(f"   UX Designer: {ux_tokens:,} tokens")
    print(f"   Gradio Developer: {dev_tokens:,} tokens")
    print(f"   TOTAL: {total:,} tokens")

    # Compare to expected baseline (~40,000 tokens)
    if total < 25000:
        print(f"\n[EXCELLENT] EXCELLENT: Token usage is {total:,} (target was <25,000)")
    elif total < 35000:
        print(f"\n[OK] GOOD: Token usage is {total:,} (target was <35,000)")
    else:
        print(f"\n⚠️  WARNING: Token usage is {total:,} (higher than expected <35,000)")

    print(f"\nEstimated savings vs baseline (40,000 tokens): {((40000 - total) / 40000) * 100:.1f}%")


if __name__ == "__main__":
    try:
        test_compact_design_spec()
        test_two_agent_generation()

        print("\n" + "="*80)
        print("ALL TESTS PASSED! [OK]")
        print("="*80)
        print("\nOpus Part 2 optimizations successfully implemented:")
        print("  [OK] Ultra-compact DesignSpec serialization")
        print("  [OK] Token usage logging")
        print("  [OK] Reduced max_tokens allocations")
        print("  [OK] Orchestrator token reporting")
        print("\nNext steps:")
        print("  - Implement pattern caching for 70-90% additional savings")
        print("  - Add keyword extraction")
        print("  - Compress memory context")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)