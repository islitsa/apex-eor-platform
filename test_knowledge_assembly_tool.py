"""
Test Knowledge Assembly Tool - Phase 3 Step 3
"""


class MockKnowledgeTool:
    """Mock KnowledgeTool for testing"""

    def retrieve_all_knowledge(self, data_context=None, enable_gradient=False):
        """Mock knowledge retrieval"""
        knowledge = {
            'ux_patterns': {
                'master_detail': {'name': 'Master-Detail'},
                'progressive_disclosure': {'name': 'Progressive Disclosure'}
            },
            'design_principles': {
                'typography': {'name': 'Material Typography'},
                'colors': {'name': 'Material Colors'}
            },
            'gradio_constraints': {
                'css': [{'name': 'CSS Limitations'}],
                'state': [{'name': 'State Management'}]
            }
        }

        # Add gradient context if enabled
        if enable_gradient and data_context:
            knowledge['gradient_context'] = {
                'domain_signals': {'domain': 'petroleum_energy'},
                'boost_hierarchical_navigation': True
            }

        return knowledge


def test_retrieve_and_assemble_knowledge():
    """Test knowledge retrieval and assembly"""
    print("Testing retrieve_and_assemble_knowledge...")

    from src.agents.tools.knowledge_assembly_tool import KnowledgeAssemblyTool

    mock_kt = MockKnowledgeTool()
    tool = KnowledgeAssemblyTool(knowledge_tool=mock_kt)

    data_context = {
        'success': True,
        'pipelines': [{'id': 'fracfocus'}]
    }

    # Test without gradient
    knowledge = tool.retrieve_and_assemble_knowledge(
        data_context=data_context,
        enable_gradient=False
    )

    assert 'ux_patterns' in knowledge
    assert 'design_principles' in knowledge
    assert 'gradio_constraints' in knowledge
    assert 'master_detail' in knowledge['ux_patterns']

    print("  [PASS] Knowledge retrieved and assembled correctly")

    # Test with gradient
    knowledge_grad = tool.retrieve_and_assemble_knowledge(
        data_context=data_context,
        enable_gradient=True
    )

    assert 'gradient_context' in knowledge_grad
    assert knowledge_grad['gradient_context']['boost_hierarchical_navigation'] == True

    print("  [PASS] Gradient context included when enabled")


def test_knowledge_caching():
    """Test knowledge caching"""
    print("\nTesting knowledge caching...")

    from src.agents.tools.knowledge_assembly_tool import KnowledgeAssemblyTool

    mock_kt = MockKnowledgeTool()
    tool = KnowledgeAssemblyTool(knowledge_tool=mock_kt)

    data_context = {'success': True, 'pipelines': []}

    # First retrieval
    assert tool.has_cached_knowledge() == False
    knowledge1 = tool.retrieve_and_assemble_knowledge(data_context)
    assert tool.has_cached_knowledge() == True

    # Second retrieval with cache
    knowledge2 = tool.retrieve_and_assemble_knowledge(data_context, use_cache=True)
    assert knowledge1 == knowledge2

    print("  [PASS] Knowledge caching works correctly")

    # Clear cache
    tool.clear_cache()
    assert tool.has_cached_knowledge() == False

    print("  [PASS] Cache clearing works correctly")


def test_assemble_ux_knowledge():
    """Test UX-specific knowledge assembly"""
    print("\nTesting assemble_ux_knowledge...")

    from src.agents.tools.knowledge_assembly_tool import KnowledgeAssemblyTool

    mock_kt = MockKnowledgeTool()
    tool = KnowledgeAssemblyTool(knowledge_tool=mock_kt)

    knowledge = {
        'ux_patterns': {'master_detail': {'name': 'Master-Detail'}},
        'design_principles': {'typography': {'name': 'Material Typography'}},
        'gradio_constraints': {'css': [{'name': 'CSS'}]},
        'gradient_context': {'boost_tree_views': True}
    }

    data_context = {'success': True, 'pipelines': []}

    ux_knowledge = tool.assemble_ux_knowledge(knowledge, data_context)

    # UX knowledge should include patterns, principles, data, and gradient
    assert 'ux_patterns' in ux_knowledge
    assert 'design_principles' in ux_knowledge
    assert 'data_context' in ux_knowledge
    assert 'gradient_context' in ux_knowledge

    # Should NOT include gradio_constraints
    assert 'gradio_constraints' not in ux_knowledge

    print("  [PASS] UX knowledge assembled correctly")


def test_assemble_react_knowledge():
    """Test React-specific knowledge assembly"""
    print("\nTesting assemble_react_knowledge...")

    from src.agents.tools.knowledge_assembly_tool import KnowledgeAssemblyTool

    mock_kt = MockKnowledgeTool()
    tool = KnowledgeAssemblyTool(knowledge_tool=mock_kt)

    knowledge = {
        'ux_patterns': {'master_detail': {'name': 'Master-Detail'}},
        'design_principles': {'typography': {'name': 'Material Typography'}},
        'gradio_constraints': {'css': [{'name': 'CSS'}]},
        'gradient_context': {'boost_tree_views': True}
    }

    data_context = {'success': True, 'pipelines': []}
    enhanced_context = {'user_prompt': 'Test prompt'}

    react_knowledge = tool.assemble_react_knowledge(
        knowledge,
        data_context,
        enhanced_context
    )

    # React knowledge should include principles, constraints, data, and gradient
    assert 'knowledge' in react_knowledge
    assert 'design_principles' in react_knowledge['knowledge']
    assert 'gradio_constraints' in react_knowledge['knowledge']
    assert 'data_context' in react_knowledge
    assert 'gradient_context' in react_knowledge
    assert 'user_prompt' in react_knowledge  # From enhanced_context

    # Should NOT include ux_patterns in knowledge bundle
    assert 'ux_patterns' not in react_knowledge['knowledge']

    print("  [PASS] React knowledge assembled correctly")


def test_empty_knowledge():
    """Test handling when no knowledge_tool provided"""
    print("\nTesting empty knowledge fallback...")

    from src.agents.tools.knowledge_assembly_tool import KnowledgeAssemblyTool

    # No knowledge_tool provided
    tool = KnowledgeAssemblyTool(knowledge_tool=None)

    data_context = {'success': True, 'pipelines': []}
    knowledge = tool.retrieve_and_assemble_knowledge(data_context)

    # Should return empty knowledge structure
    assert knowledge['ux_patterns'] == {}
    assert knowledge['design_principles'] == {}
    assert knowledge['gradio_constraints'] == {}

    print("  [PASS] Empty knowledge fallback works correctly")


if __name__ == "__main__":
    print("="*60)
    print("KNOWLEDGE ASSEMBLY TOOL TESTS")
    print("="*60)

    try:
        test_retrieve_and_assemble_knowledge()
        test_knowledge_caching()
        test_assemble_ux_knowledge()
        test_assemble_react_knowledge()
        test_empty_knowledge()

        print("\n" + "="*60)
        print("ALL TESTS PASSED!")
        print("="*60)
        print("\nKnowledgeAssemblyTool is working correctly!")
        print("Ready to proceed with ExecutionTool")

    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
