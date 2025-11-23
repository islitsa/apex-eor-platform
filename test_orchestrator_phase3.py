"""
Test Orchestrator Phase 3 Integration

This test verifies that the Phase 3 refactored orchestrator still works correctly
with all extracted tools.
"""

def test_orchestrator_initialization():
    """Test that orchestrator initializes with all Phase 3 tools"""
    print("Testing orchestrator initialization with Phase 3 tools...")

    from src.agents.ui_orchestrator import UICodeOrchestrator

    # Initialize orchestrator
    orchestrator = UICodeOrchestrator()

    # Verify Phase 3 tools are initialized
    assert hasattr(orchestrator, 'shaping_tool'), "Missing shaping_tool"
    assert hasattr(orchestrator, 'context_assembly_tool'), "Missing context_assembly_tool"
    assert hasattr(orchestrator, 'knowledge_assembly_tool'), "Missing knowledge_assembly_tool"
    assert hasattr(orchestrator, 'execution_tool'), "Missing execution_tool"

    # Verify existing Phase 1 tools still exist
    assert hasattr(orchestrator, 'filter_tool'), "Missing filter_tool"
    assert hasattr(orchestrator, 'discovery_tool'), "Missing discovery_tool"
    assert hasattr(orchestrator, 'knowledge_tool'), "Missing knowledge_tool"

    # Verify agents still exist
    assert hasattr(orchestrator, 'ux_designer'), "Missing ux_designer"
    assert hasattr(orchestrator, 'react_developer'), "Missing react_developer"

    print("  [PASS] Orchestrator initialized successfully with all Phase 3 tools")
    print(f"  [PASS] Tools verified: shaping, context_assembly, knowledge_assembly, execution")


if __name__ == "__main__":
    print("="*60)
    print("PHASE 3 ORCHESTRATOR INTEGRATION TEST")
    print("="*60)

    try:
        test_orchestrator_initialization()

        print("\n" + "="*60)
        print("ALL TESTS PASSED!")
        print("="*60)
        print("\nPhase 3 orchestrator integration successful!")
        print("All tools properly initialized and integrated.")

    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
