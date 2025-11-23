"""
Test Phase 2 evaluation and decision logic
"""
from src.agents.ui_orchestrator import UICodeOrchestrator, EvaluationResult, OrchestratorState
from src.agents.ux_designer import DesignSpec

def test_evaluation_result():
    """Test EvaluationResult dataclass"""
    print("Testing EvaluationResult...")

    eval_result = EvaluationResult(
        satisfactory=False,
        issues=["Missing components", "Invalid data source"],
        can_retry=True,
        suggested_action="retry_ux_protocol"
    )

    assert eval_result.satisfactory == False
    assert len(eval_result.issues) == 2
    assert eval_result.can_retry == True
    assert eval_result.suggested_action == "retry_ux_protocol"

    print("  [PASS] EvaluationResult works correctly")

def test_evaluate_ux_spec():
    """Test UX spec evaluation"""
    print("\nTesting _evaluate_ux_spec...")

    orchestrator = UICodeOrchestrator()

    # Test 1: Empty design spec
    eval_result = orchestrator._evaluate_ux_spec(None, {})
    assert eval_result.satisfactory == False
    assert "empty design_spec" in eval_result.issues[0]
    print("  [PASS] Detects empty design spec")

    # Test 2: Valid design spec
    data_context = {
        'success': True,
        'pipelines': [
            {'id': 'fracfocus', 'name': 'fracfocus'}
        ]
    }

    design_spec = DesignSpec(
        screen_type='dashboard',
        intent='Show data',
        components=['header', 'data_table'],
        interactions=['click', 'select'],
        patterns=['master_detail'],
        styling={'theme': 'material'},
        data_sources={'fracfocus': {'row_count': 1000}}
    )

    eval_result = orchestrator._evaluate_ux_spec(design_spec, data_context)
    assert eval_result.satisfactory == True
    assert len(eval_result.issues) == 0
    print("  [PASS] Validates correct design spec")

    # Test 3: Hallucinated pipeline
    bad_design_spec = DesignSpec(
        screen_type='dashboard',
        intent='Show data',
        components=['header'],
        interactions=[],
        patterns=[],
        styling={},
        data_sources={'nonexistent_pipeline': {'row_count': 100}}
    )

    eval_result = orchestrator._evaluate_ux_spec(bad_design_spec, data_context)
    assert eval_result.satisfactory == False
    assert any('hallucinated' in issue.lower() for issue in eval_result.issues)
    print("  [PASS] Detects hallucinated pipelines")

def test_evaluate_react_output():
    """Test React output evaluation"""
    print("\nTesting _evaluate_react_output...")

    orchestrator = UICodeOrchestrator()

    # Test 1: Empty output
    eval_result = orchestrator._evaluate_react_output(None)
    assert eval_result.satisfactory == False
    print("  [PASS] Detects empty output")

    # Test 2: Valid output
    valid_code = """
import React from 'react'
import { useState } from 'react'

const Dashboard = () => {
    return <div>Dashboard</div>
}

export default Dashboard
"""

    eval_result = orchestrator._evaluate_react_output(valid_code)
    assert eval_result.satisfactory == True
    print("  [PASS] Validates correct React code")

    # Test 3: Too short output
    eval_result = orchestrator._evaluate_react_output("x")
    assert eval_result.satisfactory == False
    assert any('short' in issue.lower() for issue in eval_result.issues)
    print("  [PASS] Detects suspiciously short output")

def test_decide_next_action():
    """Test decision logic"""
    print("\nTesting _decide_next_action...")

    orchestrator = UICodeOrchestrator()

    # Test 1: UX evaluation failed
    ux_eval = EvaluationResult(
        satisfactory=False,
        issues=["Missing components"],
        can_retry=True,
        suggested_action="retry_ux_protocol"
    )

    action = orchestrator._decide_next_action(
        OrchestratorState.DESIGNING_UX,
        ux_eval=ux_eval
    )
    assert action == "retry_ux_protocol"
    print("  [PASS] Decides to retry UX when evaluation fails")

    # Test 2: Error state with protocol error
    action = orchestrator._decide_next_action(
        OrchestratorState.ERROR,
        last_error="UX protocol error: something went wrong"
    )
    assert action == "fallback_to_ux_legacy"
    print("  [PASS] Decides to fallback to legacy on protocol error")

    # Test 3: All evaluations passed
    ux_eval_passed = EvaluationResult(
        satisfactory=True,
        issues=[],
        can_retry=True,
        suggested_action=None
    )

    react_eval_passed = EvaluationResult(
        satisfactory=True,
        issues=[],
        can_retry=True,
        suggested_action=None
    )

    action = orchestrator._decide_next_action(
        OrchestratorState.GENERATING_CODE,
        ux_eval=ux_eval_passed,
        react_eval=react_eval_passed
    )
    assert action == "proceed_to_completion"
    print("  [PASS] Proceeds to completion when all evaluations pass")

if __name__ == "__main__":
    print("="*60)
    print("PHASE 2 EVALUATION AND DECISION LOGIC TESTS")
    print("="*60)

    try:
        test_evaluation_result()
        test_evaluate_ux_spec()
        test_evaluate_react_output()
        test_decide_next_action()

        print("\n" + "="*60)
        print("ALL TESTS PASSED!")
        print("="*60)
        print("\nPhase 2 implementation is working correctly:")
        print("  [PASS] EvaluationResult dataclass")
        print("  [PASS] _evaluate_ux_spec function")
        print("  [PASS] _evaluate_react_output function")
        print("  [PASS] _decide_next_action function")
        print("\nReady for production use!")

    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
