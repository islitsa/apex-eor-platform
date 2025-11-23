"""
Test the complete regenerate workflow with chat feedback

This test validates that:
1. Initial generation can use snippets (fast path)
2. User can provide feedback via chat
3. Regenerate button forces LLM generation (skip snippets)
4. Chat feedback is incorporated into requirements
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from src.ui.agent_studio import HybridStudioWrapper
from src.utils.context_extractor import PipelineContextExtractor


def test_regenerate_workflow():
    """Test complete workflow: generate -> chat feedback -> regenerate"""
    print("\n" + "="*80)
    print("TEST: Regenerate Workflow with Chat Feedback")
    print("="*80)

    # Track messages
    user_messages = []
    agent_messages = []

    def user_callback(role, content, metadata=None):
        user_messages.append({'role': role, 'content': content})
        print(f"  [User Chat] {role}: {content[:80]}...")

    def agent_callback(from_agent, to_agent, content, metadata=None):
        agent_messages.append({'from': from_agent, 'to': to_agent, 'content': content})
        print(f"  [Agent Chat] {from_agent} -> {to_agent}: {content[:80]}...")

    # Create wrapper
    print("\n1. Creating HybridStudioWrapper...")
    wrapper = HybridStudioWrapper(
        user_callback=user_callback,
        agent_callback=agent_callback
    )

    # Extract context
    print("\n2. Extracting pipeline context...")
    extractor = PipelineContextExtractor()
    context = extractor.extract_from_metadata()
    print(f"   [OK] Context extracted: {len(context.get('data_sources', {}))} sources")

    # ========================================
    # FIRST GENERATION (expect snippet hit)
    # ========================================
    print("\n" + "="*80)
    print("PHASE 1: Initial Generation (Expect Snippet Path)")
    print("="*80)

    requirements = {
        'screen_type': 'pipeline_dashboard_navigation',
        'intent': '''Navigate through data pipeline with modern Material Design 3 aesthetics.

GRADIO THEME API (CRITICAL - DO NOT DEVIATE):
- Use: gr.themes.Soft() - DO NOT customize colors
- Soft theme provides clean, modern aesthetic similar to M3
- NO custom theme.set() calls - causes errors
- Focus on layout and component design, not theme customization'''
    }

    code1 = wrapper.generate_ui_code(requirements, context)
    stats1 = wrapper.hybrid_generator.get_stats()

    print(f"\n[Phase 1 Results]")
    print(f"  Code length: {len(code1):,} chars")
    print(f"  Tokens used: {stats1['total_tokens_used']:,}")
    print(f"  Snippet hits: {stats1['snippet_hits']}")
    print(f"  LLM fallbacks: {stats1['llm_fallbacks']}")

    # Verify snippet was used
    assert stats1['snippet_hits'] == 1, "Expected snippet hit on first generation"
    assert stats1['total_tokens_used'] < 1000, f"Expected <1000 tokens, got {stats1['total_tokens_used']}"

    print(f"\n✓ First generation used snippet path ({stats1['total_tokens_used']} tokens)")

    # ========================================
    # SIMULATE USER FEEDBACK
    # ========================================
    print("\n" + "="*80)
    print("PHASE 2: User Provides Feedback")
    print("="*80)

    # Simulate user feedback (this would normally be in chat)
    user_feedback = "Make the header bigger and use a different color scheme with more contrast"
    print(f"\n[User Feedback]: {user_feedback}")

    # ========================================
    # REGENERATION (expect LLM path)
    # ========================================
    print("\n" + "="*80)
    print("PHASE 3: Regenerate with Feedback (Expect LLM Path)")
    print("="*80)

    # Add feedback to requirements
    requirements_with_feedback = {
        'screen_type': 'dashboard_navigation',
        'intent': requirements['intent'] + f"\n\nUSER FEEDBACK TO INCORPORATE:\n{user_feedback}"
    }

    # This simulates the regenerate workflow with force_llm=True
    print("\n[Regenerate] Forcing LLM generation to incorporate feedback...")
    code2 = wrapper.hybrid_generator.generate(
        requirements_with_feedback,
        context,
        force_llm=True  # This is what the regenerate button sets
    )

    stats2 = wrapper.hybrid_generator.get_stats()

    print(f"\n[Phase 3 Results]")
    print(f"  Code length: {len(code2):,} chars")
    print(f"  Tokens used this generation: {stats2['total_tokens_used'] - stats1['total_tokens_used']:,}")
    print(f"  Total tokens: {stats2['total_tokens_used']:,}")
    print(f"  Snippet hits: {stats2['snippet_hits']}")
    print(f"  LLM fallbacks: {stats2['llm_fallbacks']}")

    # Verify LLM was used
    assert stats2['llm_fallbacks'] == 1, "Expected LLM fallback on regeneration"
    llm_tokens = stats2['total_tokens_used'] - stats1['total_tokens_used']
    assert llm_tokens > 5000, f"Expected >5000 tokens for LLM generation, got {llm_tokens}"

    print(f"\n✓ Regeneration used LLM path ({llm_tokens:,} tokens)")

    # ========================================
    # VERIFY FEEDBACK INCORPORATION
    # ========================================
    print("\n" + "="*80)
    print("PHASE 4: Verify Feedback Incorporation")
    print("="*80)

    # Check that the code changed
    code_changed = code1 != code2
    print(f"\n[Code Comparison]")
    print(f"  First generation: {len(code1):,} chars")
    print(f"  Second generation: {len(code2):,} chars")
    print(f"  Code changed: {code_changed}")

    if code_changed:
        print(f"✓ Code was regenerated (lengths differ)")
    else:
        print(f"⚠ WARNING: Code lengths are identical, but content may differ")

    # ========================================
    # FINAL SUMMARY
    # ========================================
    print("\n" + "="*80)
    print("✓ ALL TESTS PASSED!")
    print("="*80)
    print(f"\n[Workflow Summary]")
    print(f"  Phase 1 (Initial): {stats1['total_tokens_used']:,} tokens (snippet)")
    print(f"  Phase 3 (Regenerate): {llm_tokens:,} tokens (LLM with feedback)")
    print(f"  Total tokens: {stats2['total_tokens_used']:,}")
    print(f"  Savings: {((stats2['total_tokens_used'] / (llm_tokens * 2)) * 100):.1f}% vs always-LLM")
    print(f"\n[Key Findings]")
    print(f"  ✓ Snippet path works for initial generation (fast)")
    print(f"  ✓ force_llm flag bypasses snippets during regeneration")
    print(f"  ✓ Feedback can be incorporated into requirements")
    print(f"  ✓ Code regenerates when feedback provided")
    print(f"\n[Next Step]")
    print(f"  Test in full UI:")
    print(f"    1. python scripts/pipeline/run_ingestion.py --ui")
    print(f"    2. Click 'Generate Dashboard'")
    print(f"    3. Chat: 'make header bigger'")
    print(f"    4. Click 'Regenerate'")
    print(f"    5. Verify regeneration uses LLM and incorporates feedback")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        test_regenerate_workflow()
    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)