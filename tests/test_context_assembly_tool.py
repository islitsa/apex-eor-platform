"""
Test Context Assembly Tool - Phase 3 Step 2
"""
from src.agents.tools.context_assembly_tool import ContextAssemblyTool
from src.agents.context.protocol import TaskType, OutputFormat


def test_build_session_context():
    """Test session context building"""
    print("Testing build_session_context...")

    tool = ContextAssemblyTool()

    # Test with filtered data_context
    requirements = {
        'intent': 'Show fracfocus data',
        'screen_type': 'dashboard'
    }

    data_context = {
        'success': True,
        'pipelines': [
            {
                'id': 'fracfocus',
                'display_name': 'FracFocus',
                'metrics': {
                    'record_count': 100000
                }
            },
            {
                'id': 'rrc',
                'display_name': 'Railroad Commission',
                'metrics': {
                    'record_count': 50000
                }
            }
        ]
    }

    knowledge = {}

    session_ctx = tool.build_session_context(requirements, data_context, knowledge)

    # Verify session context structure
    assert session_ctx.session_id is not None
    assert len(session_ctx.session_id) > 0
    assert session_ctx.discovery.sources == ['fracfocus', 'rrc']
    assert session_ctx.discovery.record_counts['fracfocus'] == 100000
    assert session_ctx.discovery.record_counts['rrc'] == 50000
    assert session_ctx.intent.original_query == 'Show fracfocus data'
    assert session_ctx.intent.scope == ['fracfocus', 'rrc']
    assert session_ctx.intent.task_type == TaskType.DASHBOARD
    assert session_ctx.intent.output_format == OutputFormat.REACT

    print("  [PASS] Session context built correctly from data_context")


def test_fallback_to_requirements():
    """Test fallback when data_context is empty"""
    print("\nTesting fallback to requirements...")

    tool = ContextAssemblyTool()

    requirements = {
        'intent': 'Show production data',
        'screen_type': 'analysis',
        'data_sources': {
            'production': {'row_count': 75000},
            'wells': {'row_count': 25000}
        }
    }

    data_context = {
        'success': False,
        'error': 'API unavailable'
    }

    knowledge = {}

    session_ctx = tool.build_session_context(requirements, data_context, knowledge)

    # Verify fallback to requirements
    assert session_ctx.discovery.sources == ['production', 'wells']
    assert session_ctx.discovery.record_counts['production'] == 75000
    assert session_ctx.discovery.record_counts['wells'] == 25000
    assert session_ctx.intent.task_type == TaskType.ANALYSIS

    print("  [PASS] Fallback to requirements works correctly")


def test_infer_task_type():
    """Test task type inference"""
    print("\nTesting infer_task_type...")

    tool = ContextAssemblyTool()

    assert tool.infer_task_type('dashboard') == TaskType.DASHBOARD
    assert tool.infer_task_type('data_dashboard') == TaskType.DASHBOARD
    assert tool.infer_task_type('analysis_view') == TaskType.ANALYSIS
    assert tool.infer_task_type('report_page') == TaskType.REPORT
    assert tool.infer_task_type('unknown') == TaskType.DASHBOARD  # Default

    print("  [PASS] Task type inference works correctly")


def test_update_execution_context():
    """Test execution context updates"""
    print("\nTesting update_execution_context...")

    tool = ContextAssemblyTool()

    # Build initial context
    requirements = {
        'intent': 'Test',
        'screen_type': 'dashboard',
        'data_sources': {'test': {'row_count': 100}}
    }
    data_context = {'success': False}
    knowledge = {}

    session_ctx = tool.build_session_context(requirements, data_context, knowledge)

    # Initially trace_decisions should be False
    assert session_ctx.execution.trace_decisions == False

    # Update execution context
    updated_ctx = tool.update_execution_context(session_ctx, trace_decisions=True)

    assert updated_ctx.execution.trace_decisions == True

    print("  [PASS] Execution context update works correctly")


def test_prepare_builder_context():
    """Test builder context preparation (Section B extraction)"""
    print("\nTesting prepare_builder_context...")

    from src.agents.tools.filter_tool import DataFilterTool

    tool = ContextAssemblyTool()
    filter_tool = DataFilterTool()

    requirements = {
        'intent': 'Show me pipeline data',
        'user_feedback': 'Make it more colorful'
    }

    context = {
        'data_sources': {
            'fracfocus': {'datasets': 5},
            'rrc': {'datasets': 3},
            'usgs': {'datasets': 2}
        }
    }

    data_context = {
        'success': True,
        'pipelines': [
            {'id': 'fracfocus', 'display_name': 'FracFocus'},
            {'id': 'rrc', 'display_name': 'RRC'}
            # Note: usgs is filtered out
        ]
    }

    # Test builder context preparation
    enhanced_context = tool.prepare_builder_context(
        requirements=requirements,
        context=context,
        data_context=data_context,
        filter_tool=filter_tool
    )

    # Check user_prompt added
    assert 'user_prompt' in enhanced_context
    assert enhanced_context['user_prompt'] == 'Show me pipeline data'

    # Check user_feedback added
    assert 'user_feedback' in enhanced_context
    assert enhanced_context['user_feedback'] == 'Make it more colorful'

    # Check data_sources filtered to match pipelines
    assert 'data_sources' in enhanced_context
    assert len(enhanced_context['data_sources']) == 2  # Only fracfocus and rrc
    assert 'fracfocus' in enhanced_context['data_sources']
    assert 'rrc' in enhanced_context['data_sources']
    assert 'usgs' not in enhanced_context['data_sources']  # Filtered out

    print("  [PASS] Builder context prepared correctly")
    print("  [PASS] user_prompt and user_feedback added")
    print("  [PASS] data_sources filtered to match pipelines")


if __name__ == "__main__":
    print("="*60)
    print("CONTEXT ASSEMBLY TOOL TESTS")
    print("="*60)

    try:
        test_build_session_context()
        test_fallback_to_requirements()
        test_infer_task_type()
        test_update_execution_context()
        test_prepare_builder_context()

        print("\n" + "="*60)
        print("ALL TESTS PASSED!")
        print("="*60)
        print("\nContextAssemblyTool is working correctly!")
        print("Section B extraction (prepare_builder_context) tested and verified!")
        print("Ready to proceed with KnowledgeAssemblyTool")

    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
