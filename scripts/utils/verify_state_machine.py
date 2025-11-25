"""
Quick verification for Phase 1.1: State Machine

This script verifies that state transitions are working correctly.
Run this before testing with Agent Studio.
"""

from src.agents.ui_orchestrator import UICodeOrchestrator, OrchestratorState


def test_state_initialization():
    """Test that orchestrator initializes in IDLE state"""
    print("=" * 80)
    print("TEST 1: State Initialization")
    print("=" * 80)

    orchestrator = UICodeOrchestrator()

    if orchestrator.current_state == OrchestratorState.IDLE:
        print("[PASS] Orchestrator initialized in IDLE state")
        return True
    else:
        print(f"[FAIL] Expected IDLE, got {orchestrator.current_state}")
        return False


def test_state_transitions():
    """Test manual state transitions"""
    print("\n" + "=" * 80)
    print("TEST 2: Manual State Transitions")
    print("=" * 80)

    orchestrator = UICodeOrchestrator()

    # Test transition sequence
    expected_transitions = [
        OrchestratorState.PARSING_REQUIREMENTS,
        OrchestratorState.DISCOVERING_DATA,
        OrchestratorState.FETCHING_KNOWLEDGE,
        OrchestratorState.BUILDING_SESSION,
        OrchestratorState.DESIGNING_UX,
        OrchestratorState.GENERATING_CODE,
        OrchestratorState.COMPLETED,
    ]

    print("\nTesting state transition sequence:")
    all_pass = True

    for expected_state in expected_transitions:
        orchestrator._transition_to(expected_state)
        if orchestrator.current_state == expected_state:
            print(f"  [PASS] Transitioned to {expected_state.value}")
        else:
            print(f"  [FAIL] Expected {expected_state.value}, got {orchestrator.current_state.value}")
            all_pass = False

    if all_pass:
        print("\n[PASS] All state transitions successful")
    else:
        print("\n[FAIL] Some state transitions failed")

    return all_pass


def test_state_enum():
    """Test that all expected states exist in enum"""
    print("\n" + "=" * 80)
    print("TEST 3: State Enum Completeness")
    print("=" * 80)

    expected_states = [
        'idle', 'parsing_requirements', 'discovering_data',
        'fetching_knowledge', 'analyzing_gradient', 'designing_ux',
        'building_session', 'generating_code', 'completed', 'error'
    ]

    actual_states = [state.value for state in OrchestratorState]

    print(f"\nExpected states: {expected_states}")
    print(f"Actual states:   {actual_states}")

    if set(expected_states) == set(actual_states):
        print("\n[PASS] All expected states present in enum")
        return True
    else:
        missing = set(expected_states) - set(actual_states)
        extra = set(actual_states) - set(expected_states)
        if missing:
            print(f"\n[FAIL] Missing states: {missing}")
        if extra:
            print(f"\n[FAIL] Unexpected states: {extra}")
        return False


def main():
    """Run all verification tests"""
    print("\n")
    print("+" + "=" * 78 + "+")
    print("|" + " " * 22 + "State Machine Verification" + " " * 29 + "|")
    print("+" + "=" * 78 + "+")
    print()

    try:
        test1 = test_state_initialization()
        test2 = test_state_transitions()
        test3 = test_state_enum()

        print("\n" + "=" * 80)
        if test1 and test2 and test3:
            print("[PASS] ALL TESTS PASSED")
            print("   State machine is working correctly!")
            print("   Ready for Agent Studio integration.")
        else:
            print("[FAIL] SOME TESTS FAILED")
            print("   Review output above for details.")
        print("=" * 80)

    except Exception as e:
        print(f"\n[FAIL] ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
