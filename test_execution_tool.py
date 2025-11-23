"""
Test Execution Tool - Phase 3 Step 4
"""
from src.agents.tools.execution_tool import ExecutionTool, EvaluationResult, OrchestratorState
from src.agents.ux_designer import DesignSpec


class MockUXDesigner:
    """Mock UX Designer for testing"""

    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.call_count = 0

    def with_context(self, session_ctx):
        """Mock context binding"""
        return self

    def execute(self):
        """Mock protocol execution"""
        self.call_count += 1

        if self.should_fail and self.call_count == 1:
            raise Exception("Mock UX protocol failure")

        return {
            'screen_type': 'dashboard',
            'intent': 'Test intent',
            'components': ['header', 'data_table'],
            'interactions': ['click'],
            'patterns': ['master_detail'],
            'styling': {},
            'data_sources': {'test': {'row_count': 100}}
        }

    def design(self, requirements, design_knowledge):
        """Mock legacy design method"""
        return DesignSpec(
            screen_type='dashboard',
            intent='Legacy design',
            components=['header'],
            interactions=[],
            patterns=[],
            styling={},
            data_sources={'test': {'row_count': 100}}
        )


class MockReactDeveloper:
    """Mock React Developer for testing"""

    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.call_count = 0

    def with_context(self, session_ctx):
        """Mock context binding"""
        return self

    def execute(self):
        """Mock protocol execution"""
        self.call_count += 1

        if self.should_fail and self.call_count == 1:
            raise Exception("Mock React protocol failure")

        return {
            'App.tsx': 'import React from "react"\nexport default function App() { return <div>Test</div> }'
        }

    def build(self, design_spec, enhanced_context):
        """Mock legacy build method"""
        return {
            'App.tsx': 'import React from "react"\nexport default function App() { return <div>Legacy</div> }'
        }


class MockSessionContext:
    """Mock SessionContext for testing"""
    pass


def mock_evaluate_ux(design_spec, data_context):
    """Mock UX evaluation function"""
    if not design_spec or not hasattr(design_spec, 'components'):
        return EvaluationResult(
            satisfactory=False,
            issues=['No design spec'],
            can_retry=True,
            suggested_action='retry_ux_protocol'
        )

    if not design_spec.components:
        return EvaluationResult(
            satisfactory=False,
            issues=['No components'],
            can_retry=True,
            suggested_action='retry_ux_protocol'
        )

    return EvaluationResult(
        satisfactory=True,
        issues=[],
        can_retry=True,
        suggested_action=None
    )


def mock_evaluate_react(react_files):
    """Mock React evaluation function"""
    if not react_files:
        return EvaluationResult(
            satisfactory=False,
            issues=['No React files'],
            can_retry=True,
            suggested_action='retry_react_protocol'
        )

    return EvaluationResult(
        satisfactory=True,
        issues=[],
        can_retry=True,
        suggested_action=None
    )


def mock_decide(state, ux_eval=None, react_eval=None, last_error=None):
    """Mock decision function"""
    if state == OrchestratorState.ERROR:
        if last_error and 'ux' in last_error.lower():
            return 'fallback_to_ux_legacy'
        elif last_error and 'react' in last_error.lower():
            return 'fallback_to_react_legacy'
        return 'abort_due_to_errors'

    if ux_eval and not ux_eval.satisfactory:
        return ux_eval.suggested_action or 'retry_ux_protocol'

    if react_eval and not react_eval.satisfactory:
        return react_eval.suggested_action or 'retry_react_protocol'

    return 'proceed_to_completion'


def test_execute_ux_success():
    """Test successful UX execution"""
    print("Testing execute_ux_with_retry (success case)...")

    tool = ExecutionTool()
    ux_designer = MockUXDesigner(should_fail=False)
    session_ctx = MockSessionContext()
    design_knowledge = {}
    requirements = {}
    data_context = {'success': True, 'pipelines': []}

    design_spec, last_error = tool.execute_ux_with_retry(
        ux_designer=ux_designer,
        session_ctx=session_ctx,
        design_knowledge=design_knowledge,
        requirements=requirements,
        data_context=data_context,
        evaluate_fn=mock_evaluate_ux,
        decide_fn=mock_decide
    )

    assert design_spec is not None
    assert hasattr(design_spec, 'components')
    assert len(design_spec.components) > 0
    assert last_error is None
    assert ux_designer.call_count == 1  # Should succeed on first try

    print("  [PASS] Successful UX execution works correctly")


def test_execute_ux_with_fallback():
    """Test UX execution with fallback to legacy"""
    print("\nTesting execute_ux_with_retry (fallback case)...")

    tool = ExecutionTool()
    ux_designer = MockUXDesigner(should_fail=True)
    session_ctx = MockSessionContext()
    design_knowledge = {}
    requirements = {}
    data_context = {'success': True, 'pipelines': []}

    design_spec, last_error = tool.execute_ux_with_retry(
        ux_designer=ux_designer,
        session_ctx=session_ctx,
        design_knowledge=design_knowledge,
        requirements=requirements,
        data_context=data_context,
        evaluate_fn=mock_evaluate_ux,
        decide_fn=mock_decide
    )

    assert design_spec is not None
    assert design_spec.intent == 'Legacy design'  # Should use legacy fallback
    assert last_error is None  # Error should be cleared after successful fallback

    print("  [PASS] UX fallback to legacy works correctly")


def test_execute_react_success():
    """Test successful React execution"""
    print("\nTesting execute_react_with_retry (success case)...")

    tool = ExecutionTool()
    react_developer = MockReactDeveloper(should_fail=False)
    session_ctx = MockSessionContext()
    design_spec = DesignSpec(
        screen_type='dashboard',
        intent='Test',
        components=['header'],
        interactions=[],
        patterns=[],
        styling={},
        data_sources={}
    )
    enhanced_context = {}

    react_files, last_error = tool.execute_react_with_retry(
        react_developer=react_developer,
        session_ctx=session_ctx,
        design_spec=design_spec,
        enhanced_context=enhanced_context,
        evaluate_fn=mock_evaluate_react,
        decide_fn=mock_decide
    )

    assert react_files is not None
    assert 'App.tsx' in react_files
    assert 'Test' in react_files['App.tsx']
    assert last_error is None
    assert react_developer.call_count == 1  # Should succeed on first try

    print("  [PASS] Successful React execution works correctly")


def test_execute_react_with_fallback():
    """Test React execution with fallback to legacy"""
    print("\nTesting execute_react_with_retry (fallback case)...")

    tool = ExecutionTool()
    react_developer = MockReactDeveloper(should_fail=True)
    session_ctx = MockSessionContext()
    design_spec = DesignSpec(
        screen_type='dashboard',
        intent='Test',
        components=['header'],
        interactions=[],
        patterns=[],
        styling={},
        data_sources={}
    )
    enhanced_context = {}

    react_files, last_error = tool.execute_react_with_retry(
        react_developer=react_developer,
        session_ctx=session_ctx,
        design_spec=design_spec,
        enhanced_context=enhanced_context,
        evaluate_fn=mock_evaluate_react,
        decide_fn=mock_decide
    )

    assert react_files is not None
    assert 'App.tsx' in react_files
    assert 'Legacy' in react_files['App.tsx']  # Should use legacy fallback

    print("  [PASS] React fallback to legacy works correctly")


def test_max_iterations():
    """Test that max iterations are respected"""
    print("\nTesting max iterations bounds...")

    tool = ExecutionTool()

    # Verify constants
    assert tool.MAX_UX_ITERATIONS == 3
    assert tool.MAX_REACT_ATTEMPTS == 2

    print("  [PASS] Max iteration constants are correct")


if __name__ == "__main__":
    print("="*60)
    print("EXECUTION TOOL TESTS")
    print("="*60)

    try:
        test_execute_ux_success()
        test_execute_ux_with_fallback()
        test_execute_react_success()
        test_execute_react_with_fallback()
        test_max_iterations()

        print("\n" + "="*60)
        print("ALL TESTS PASSED!")
        print("="*60)
        print("\nExecutionTool is working correctly!")
        print("Ready to update orchestrator to use all extracted tools")

    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
