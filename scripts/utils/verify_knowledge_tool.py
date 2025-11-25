"""
Standalone verification script for KnowledgeTool (Phase 1.6)

Quick smoke tests to verify knowledge retrieval works correctly
without running full test suite.
"""

from unittest.mock import Mock
from src.agents.tools.knowledge_tool import KnowledgeTool


def test_initialization():
    """Test 1: Initialization"""
    print("=" * 80)
    print("TEST 1: Initialization")
    print("=" * 80)

    tool = KnowledgeTool()

    if tool.design_kb is None and tool.gradient_system is None and tool.trace_collector is None:
        print("[PASS] Tool initialized correctly with None dependencies")
        return True
    else:
        print(f"[FAIL] Unexpected initialization state")
        return False


def test_knowledge_retrieval():
    """Test 2: Knowledge Retrieval (mocked)"""
    print("\n" + "=" * 80)
    print("TEST 2: Knowledge Retrieval")
    print("=" * 80)

    # Mock design_kb
    design_kb = Mock()
    design_kb.query.side_effect = [
        [{'pattern': 'master-detail'}],       # master_detail
        [{'pattern': 'progressive'}],          # progressive_disclosure
        [{'pattern': 'card-grid'}],            # card_grid
        [{'principle': 'typography'}],         # typography
        [{'principle': 'colors'}],             # colors
        [{'principle': 'spacing'}],            # spacing
        [{'constraint': 'css1'}, {'constraint': 'css2'}],  # css
        [{'constraint': 'state'}],             # state
        [{'constraint': 'events'}]             # events
    ]

    tool = KnowledgeTool(design_kb=design_kb)
    result = tool.retrieve_all_knowledge()

    # Verify structure
    if ('ux_patterns' in result and
        'design_principles' in result and
        'gradio_constraints' in result):

        # Verify UX patterns
        if (len(result['ux_patterns']) == 3 and
            'master_detail' in result['ux_patterns'] and
            'progressive_disclosure' in result['ux_patterns'] and
            'card_grid' in result['ux_patterns']):

            # Verify design principles
            if (len(result['design_principles']) == 3 and
                'typography' in result['design_principles'] and
                'colors' in result['design_principles'] and
                'spacing' in result['design_principles']):

                # Verify Gradio constraints
                if (len(result['gradio_constraints']) == 3 and
                    'css' in result['gradio_constraints'] and
                    'state' in result['gradio_constraints'] and
                    'events' in result['gradio_constraints']):

                    print(f"[PASS] Retrieved all knowledge:")
                    print(f"       - UX Patterns: {len(result['ux_patterns'])}")
                    print(f"       - Design Principles: {len(result['design_principles'])}")
                    print(f"       - Gradio Constraints: {len(result['gradio_constraints'])}")
                    return True

    print(f"[FAIL] Knowledge retrieval incomplete")
    print(f"       Result: {result}")
    return False


def test_domain_signal_extraction():
    """Test 3: Domain Signal Extraction"""
    print("\n" + "=" * 80)
    print("TEST 3: Domain Signal Extraction")
    print("=" * 80)

    tool = KnowledgeTool()

    # Test petroleum domain
    data_context = {
        'success': True,
        'pipelines': [
            {'display_name': 'FracFocus Chemical Disclosure', 'files': {}},
            {'display_name': 'RRC Production Data', 'files': {}}
        ]
    }

    signals = tool.extract_domain_signals(data_context)

    if signals['domain'] == 'petroleum_energy':
        print(f"[PASS] Correctly detected petroleum domain")
        print(f"       Domain: {signals['domain']}")
        print(f"       Keywords: {signals['keywords'][:5]}")
        print(f"       Data Types: {signals['data_types']}")
        return True
    else:
        print(f"[FAIL] Expected petroleum_energy, got {signals['domain']}")
        return False


def test_structure_detection():
    """Test 4: Structure Complexity Detection"""
    print("\n" + "=" * 80)
    print("TEST 4: Structure Complexity Detection")
    print("=" * 80)

    tool = KnowledgeTool()

    # Test deeply nested structure
    data_context = {
        'success': True,
        'pipelines': [
            {
                'display_name': 'Test Pipeline',
                'files': {
                    'subdirs': {
                        'level1': {
                            'files': ['file1.csv'] * 5,
                            'subdirs': {
                                'level2': {
                                    'files': ['file2.csv'] * 5,
                                    'subdirs': {
                                        'level3': {
                                            'files': ['file3.csv'] * 5
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        ]
    }

    signals = tool.extract_domain_signals(data_context)

    if (signals['structure'] == 'deeply_nested_directories' and
        signals['metrics']['max_depth'] == 3 and
        signals['metrics']['total_files'] >= 10):

        print(f"[PASS] Correctly detected deeply nested structure")
        print(f"       Structure: {signals['structure']}")
        print(f"       Max Depth: {signals['metrics']['max_depth']}")
        print(f"       Total Files: {signals['metrics']['total_files']}")
        return True
    else:
        print(f"[FAIL] Structure detection incorrect")
        print(f"       Got: {signals}")
        return False


def test_gradient_boosting():
    """Test 5: Gradient Boosting Integration"""
    print("\n" + "=" * 80)
    print("TEST 5: Gradient Boosting Integration")
    print("=" * 80)

    # Mock dependencies
    design_kb = Mock()
    design_kb.query.return_value = []

    gradient_system = Mock()
    trace_collector = Mock()

    tool = KnowledgeTool(
        design_kb=design_kb,
        gradient_system=gradient_system,
        trace_collector=trace_collector
    )

    data_context = {
        'success': True,
        'pipelines': [
            {
                'display_name': 'RRC Production',
                'files': {
                    'subdirs': {
                        'downloads': {
                            'files': ['file1.csv'] * 5,
                            'subdirs': {
                                'extracted': {
                                    'files': ['file2.csv'] * 5,
                                    'subdirs': {
                                        'parsed': {
                                            'files': ['file3.csv'] * 5
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        ]
    }

    result = tool.retrieve_all_knowledge(
        data_context=data_context,
        enable_gradient=True
    )

    # Verify gradient_context was added
    if ('gradient_context' in result and
        'domain_signals' in result['gradient_context'] and
        'boost_hierarchical_navigation' in result['gradient_context']):

        gc = result['gradient_context']
        print(f"[PASS] Gradient boosting applied successfully")
        print(f"       Domain: {gc['domain_signals']['domain']}")
        print(f"       Boost Hierarchical Nav: {gc['boost_hierarchical_navigation']}")
        print(f"       Boost Tree Views: {gc['boost_tree_views']}")
        print(f"       Boost Data Drill-Down: {gc['boost_data_drill_down']}")

        # Verify traces were emitted
        if trace_collector.trace_thinking.called and trace_collector.trace_reasoning.called:
            print(f"       Traces emitted: YES")
            return True
        else:
            print(f"[FAIL] Traces not emitted")
            return False
    else:
        print(f"[FAIL] Gradient context not applied")
        print(f"       Result keys: {result.keys()}")
        return False


def main():
    """Run all verification tests"""
    print("\n")
    print("+" + "=" * 78 + "+")
    print("|" + " " * 19 + "KnowledgeTool Verification (Phase 1.6)" + " " * 20 + "|")
    print("+" + "=" * 78 + "+")
    print()

    try:
        results = []

        results.append(test_initialization())
        results.append(test_knowledge_retrieval())
        results.append(test_domain_signal_extraction())
        results.append(test_structure_detection())
        results.append(test_gradient_boosting())

        print("\n" + "=" * 80)
        if all(results):
            print("[PASS] ALL TESTS PASSED")
            print("   KnowledgeTool is working correctly!")
            print("   Ready for Agent Studio integration.")
        else:
            failed_count = len([r for r in results if not r])
            print(f"[FAIL] {failed_count}/{len(results)} TESTS FAILED")
            print("   Review output above for details.")
        print("=" * 80)

    except Exception as e:
        print(f"\n[FAIL] ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
