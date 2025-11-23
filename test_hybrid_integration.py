"""
Test Hybrid Integration with Agent Studio

Verifies that HybridStudioWrapper works correctly when integrated into agent_studio.py
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from src.ui.agent_studio import HybridStudioWrapper
from src.utils.context_extractor import PipelineContextExtractor

def test_hybrid_wrapper():
    """Test that HybridStudioWrapper initializes and generates code"""
    print("\n" + "="*80)
    print("TEST: Hybrid Studio Wrapper Integration")
    print("="*80)

    # Track messages
    user_messages = []
    agent_messages = []

    def user_callback(role, content, metadata=None):
        user_messages.append({'role': role, 'content': content})
        print(f"  [User Chat] {role}: {content}")

    def agent_callback(from_agent, to_agent, content, metadata=None):
        agent_messages.append({'from': from_agent, 'to': to_agent, 'content': content})
        print(f"  [Agent Chat] {from_agent} -> {to_agent}: {content}")

    # Create wrapper
    print("\n1. Creating HybridStudioWrapper...")
    wrapper = HybridStudioWrapper(
        user_callback=user_callback,
        agent_callback=agent_callback
    )

    # Verify agents are exposed
    assert hasattr(wrapper, 'ux_designer'), "Should expose ux_designer"
    assert hasattr(wrapper, 'gradio_developer'), "Should expose gradio_developer"
    print("   [OK] Wrapper initialized, agents exposed for Q&A")

    # Extract context
    print("\n2. Extracting pipeline context...")
    extractor = PipelineContextExtractor()
    context = extractor.extract_from_metadata()
    print(f"   [OK] Context extracted: {len(context.get('data_sources', {}))} sources")

    # Generate code (should hit snippet)
    print("\n3. Generating dashboard (expect snippet hit)...")
    requirements = {
        'screen_type': 'pipeline_dashboard_navigation',
        'intent': 'Browse pipeline data sources and datasets'
    }

    code = wrapper.generate_ui_code(requirements, context)

    print(f"\n   [OK] Generated {len(code):,} chars of code")

    # Verify callbacks were called
    print(f"\n4. Verifying callbacks...")
    print(f"   User messages: {len(user_messages)}")
    print(f"   Agent messages: {len(agent_messages)}")

    assert len(user_messages) >= 2, "Should have startup + completion messages"
    assert len(agent_messages) >= 1, "Should have agent-to-agent messages"

    # Check for hybrid-specific messages
    hybrid_messages = [msg for msg in user_messages if 'Hybrid' in msg['content'] or 'snippet' in msg['content']]
    assert len(hybrid_messages) > 0, "Should have hybrid-specific messages"

    print("   [OK] Callbacks working correctly")

    # Get stats
    stats = wrapper.hybrid_generator.get_stats()
    print(f"\n5. Performance Stats:")
    print(f"   Total generations: {stats['total_generations']}")
    print(f"   Snippet hits: {stats['snippet_hits']}")
    print(f"   LLM fallbacks: {stats['llm_fallbacks']}")
    print(f"   Hit rate: {stats['hit_rate']:.1f}%")
    print(f"   Total tokens: {stats['total_tokens_used']:,}")
    print(f"   Avg tokens/gen: {stats['avg_tokens_per_generation']:.0f}")
    print(f"   Savings vs 40k: {stats['estimated_savings_vs_baseline']:.1f}%")

    print("\n" + "="*80)
    print("[OK] ALL TESTS PASSED!")
    print("="*80)
    print("\nHybrid integration successful!")
    print(f"  - Generated {len(code):,} chars")
    print(f"  - Used {stats['total_tokens_used']:,} tokens")
    print(f"  - {stats['estimated_savings_vs_baseline']:.1f}% savings vs baseline")
    print("\nYou can now run: python scripts/pipeline/run_ingestion.py --ui")
    print("to use the hybrid system in the full UI!")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        test_hybrid_wrapper()
    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)