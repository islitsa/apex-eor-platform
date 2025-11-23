"""
Tests for KnowledgeTool - Phase 1.6

These tests verify that the centralized knowledge retrieval tool behaves correctly
and handles all edge cases for Pinecone queries.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.agents.tools.knowledge_tool import KnowledgeTool


class TestKnowledgeToolBasics:
    """Test basic functionality"""

    def test_initialization(self):
        """Should initialize with optional dependencies"""
        tool = KnowledgeTool()
        assert tool.design_kb is None
        assert tool.gradient_system is None
        assert tool.trace_collector is None

    def test_initialization_with_dependencies(self):
        """Should initialize with design_kb, gradient_system, and trace_collector"""
        design_kb = Mock()
        gradient_system = Mock()
        trace_collector = Mock()

        tool = KnowledgeTool(
            design_kb=design_kb,
            gradient_system=gradient_system,
            trace_collector=trace_collector
        )

        assert tool.design_kb == design_kb
        assert tool.gradient_system == gradient_system
        assert tool.trace_collector == trace_collector


class TestKnowledgeRetrieval:
    """Test knowledge retrieval from Pinecone"""

    def test_retrieve_knowledge_without_design_kb(self):
        """Should return empty knowledge when design_kb is None"""
        tool = KnowledgeTool()
        result = tool.retrieve_all_knowledge()

        assert result == {
            'ux_patterns': {},
            'design_principles': {},
            'gradio_constraints': {}
        }

    def test_retrieve_ux_patterns(self):
        """Should query and retrieve UX patterns"""
        design_kb = Mock()
        design_kb.query.side_effect = [
            [{'pattern': 'master-detail'}],  # master_detail
            [{'pattern': 'progressive'}],     # progressive_disclosure
            [{'pattern': 'card-grid'}],       # card_grid
            [{'principle': 'typography'}],    # typography
            [{'principle': 'colors'}],        # colors
            [{'principle': 'spacing'}],       # spacing
            [{'constraint': 'css'}],          # css
            [{'constraint': 'state'}],        # state
            [{'constraint': 'events'}]        # events
        ]

        tool = KnowledgeTool(design_kb=design_kb)
        result = tool.retrieve_all_knowledge()

        # Verify UX patterns were retrieved
        assert 'master_detail' in result['ux_patterns']
        assert result['ux_patterns']['master_detail'] == {'pattern': 'master-detail'}

        assert 'progressive_disclosure' in result['ux_patterns']
        assert result['ux_patterns']['progressive_disclosure'] == {'pattern': 'progressive'}

        assert 'card_grid' in result['ux_patterns']
        assert result['ux_patterns']['card_grid'] == {'pattern': 'card-grid'}

    def test_retrieve_design_principles(self):
        """Should query and retrieve design principles"""
        design_kb = Mock()
        design_kb.query.side_effect = [
            [],  # master_detail (empty)
            [],  # progressive_disclosure (empty)
            [],  # card_grid (empty)
            [{'principle': 'typography'}],  # typography
            [{'principle': 'colors'}],      # colors
            [{'principle': 'spacing'}],     # spacing
            [],  # css (empty)
            [],  # state (empty)
            []   # events (empty)
        ]

        tool = KnowledgeTool(design_kb=design_kb)
        result = tool.retrieve_all_knowledge()

        # Verify design principles were retrieved
        assert 'typography' in result['design_principles']
        assert 'colors' in result['design_principles']
        assert 'spacing' in result['design_principles']

    def test_retrieve_gradio_constraints(self):
        """Should query and retrieve Gradio constraints"""
        design_kb = Mock()
        design_kb.query.side_effect = [
            [],  # master_detail
            [],  # progressive_disclosure
            [],  # card_grid
            [],  # typography
            [],  # colors
            [],  # spacing
            [{'constraint': 'css1'}, {'constraint': 'css2'}],  # css (top_k=3, returns list)
            [{'constraint': 'state1'}],                        # state
            [{'constraint': 'events1'}]                        # events
        ]

        tool = KnowledgeTool(design_kb=design_kb)
        result = tool.retrieve_all_knowledge()

        # Verify Gradio constraints were retrieved
        assert 'css' in result['gradio_constraints']
        assert 'state' in result['gradio_constraints']
        assert 'events' in result['gradio_constraints']

    def test_query_counts(self):
        """Should make exactly 9 queries total"""
        design_kb = Mock()
        design_kb.query.return_value = []

        tool = KnowledgeTool(design_kb=design_kb)
        tool.retrieve_all_knowledge()

        # Should query 9 times:
        # - 3 UX patterns
        # - 3 Design principles
        # - 3 Gradio constraints
        assert design_kb.query.call_count == 9

    def test_trace_emission(self):
        """Should not emit traces when trace_collector is None"""
        design_kb = Mock()
        design_kb.query.return_value = []

        tool = KnowledgeTool(design_kb=design_kb)
        result = tool.retrieve_all_knowledge()

        # Should succeed without trace_collector
        assert result is not None


class TestDomainSignalExtraction:
    """Test domain signal extraction for gradient boosting"""

    def test_extract_domain_signals_petroleum(self):
        """Should detect petroleum domain from pipeline names"""
        tool = KnowledgeTool()

        data_context = {
            'success': True,
            'pipelines': [
                {'display_name': 'FracFocus', 'files': {}},
                {'display_name': 'RRC Well Data', 'files': {}}
            ]
        }

        signals = tool.extract_domain_signals(data_context)

        assert signals['domain'] == 'petroleum_energy'
        assert 'fracfocus' in signals['keywords']

    def test_extract_domain_signals_healthcare(self):
        """Should detect healthcare domain"""
        tool = KnowledgeTool()

        data_context = {
            'success': True,
            'pipelines': [
                {'display_name': 'Patient Records', 'files': {}},
                {'display_name': 'Medical Data', 'files': {}}
            ]
        }

        signals = tool.extract_domain_signals(data_context)

        assert signals['domain'] == 'healthcare'

    def test_extract_domain_signals_financial(self):
        """Should detect financial domain"""
        tool = KnowledgeTool()

        data_context = {
            'success': True,
            'pipelines': [
                {'display_name': 'Transaction History', 'files': {}},
                {'display_name': 'Payment Data', 'files': {}}
            ]
        }

        signals = tool.extract_domain_signals(data_context)

        assert signals['domain'] == 'financial'

    def test_extract_domain_signals_generic(self):
        """Should default to generic domain"""
        tool = KnowledgeTool()

        data_context = {
            'success': True,
            'pipelines': [
                {'display_name': 'Random Data', 'files': {}}
            ]
        }

        signals = tool.extract_domain_signals(data_context)

        assert signals['domain'] == 'generic'

    def test_extract_domain_signals_empty_data(self):
        """Should handle empty data gracefully"""
        tool = KnowledgeTool()

        data_context = {
            'success': False,
            'pipelines': []
        }

        signals = tool.extract_domain_signals(data_context)

        assert signals['domain'] == 'generic'
        assert signals['keywords'] == []
        assert signals['structure'] == 'flat'
        assert signals['data_types'] == []

    def test_extract_structure_flat(self):
        """Should detect flat structure"""
        tool = KnowledgeTool()

        data_context = {
            'success': True,
            'pipelines': [
                {
                    'display_name': 'Test',
                    'files': {}  # No subdirs
                }
            ]
        }

        signals = tool.extract_domain_signals(data_context)

        assert signals['structure'] == 'flat'
        assert signals['metrics']['max_depth'] == 0

    def test_extract_structure_nested(self):
        """Should detect nested directory structure"""
        tool = KnowledgeTool()

        data_context = {
            'success': True,
            'pipelines': [
                {
                    'display_name': 'Test',
                    'files': {
                        'subdirs': {
                            'level1': {
                                'files': ['file1.csv', 'file2.csv'],
                                'subdirs': {
                                    'level2': {
                                        'files': ['file3.csv']
                                    }
                                }
                            }
                        }
                    }
                }
            ]
        }

        signals = tool.extract_domain_signals(data_context)

        assert signals['structure'] == 'nested_directories'
        assert signals['metrics']['max_depth'] == 2

    def test_extract_structure_deeply_nested(self):
        """Should detect deeply nested directory structure"""
        tool = KnowledgeTool()

        data_context = {
            'success': True,
            'pipelines': [
                {
                    'display_name': 'Test',
                    'files': {
                        'subdirs': {
                            'level1': {
                                'files': ['file1.csv'] * 5,
                                'subdirs': {
                                    'level2': {
                                        'files': ['file2.csv'] * 3,
                                        'subdirs': {
                                            'level3': {
                                                'files': ['file3.csv'] * 4
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

        assert signals['structure'] == 'deeply_nested_directories'
        assert signals['metrics']['max_depth'] == 3
        assert signals['metrics']['total_files'] >= 10

    def test_extract_data_types_chemical(self):
        """Should detect chemical data type"""
        tool = KnowledgeTool()

        data_context = {
            'success': True,
            'pipelines': [
                {'display_name': 'Chemical Disclosure', 'files': {}}
            ]
        }

        signals = tool.extract_domain_signals(data_context)

        assert 'chemical_data' in signals['data_types']

    def test_extract_data_types_operational(self):
        """Should detect operational data type"""
        tool = KnowledgeTool()

        data_context = {
            'success': True,
            'pipelines': [
                {'display_name': 'Production Data', 'files': {}},
                {'display_name': 'Completion Records', 'files': {}}
            ]
        }

        signals = tool.extract_domain_signals(data_context)

        assert 'operational_data' in signals['data_types']


class TestGradientBoosting:
    """Test gradient context boosting"""

    def test_gradient_boosting_enabled(self):
        """Should apply gradient boosting when enabled"""
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
                    'display_name': 'FracFocus',
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

        # Should have gradient_context
        assert 'gradient_context' in result
        assert 'domain_signals' in result['gradient_context']
        assert result['gradient_context']['domain_signals']['domain'] == 'petroleum_energy'

        # Should boost hierarchical navigation for deeply nested structure
        assert result['gradient_context']['boost_hierarchical_navigation'] is True
        assert result['gradient_context']['boost_tree_views'] is True

    def test_gradient_boosting_disabled(self):
        """Should not apply gradient boosting when disabled"""
        design_kb = Mock()
        design_kb.query.return_value = []

        tool = KnowledgeTool(design_kb=design_kb)

        data_context = {'success': True, 'pipelines': []}

        result = tool.retrieve_all_knowledge(
            data_context=data_context,
            enable_gradient=False
        )

        # Should not have gradient_context
        assert 'gradient_context' not in result

    def test_gradient_boosting_error_handling(self):
        """Should gracefully handle errors in gradient boosting"""
        design_kb = Mock()
        design_kb.query.return_value = []

        gradient_system = Mock()

        tool = KnowledgeTool(
            design_kb=design_kb,
            gradient_system=gradient_system
        )

        # Provide malformed data_context to trigger error
        data_context = None  # This will cause extract_domain_signals to fail

        result = tool.retrieve_all_knowledge(
            data_context=data_context,
            enable_gradient=True
        )

        # Should still return knowledge without gradient_context
        assert 'ux_patterns' in result
        assert 'gradient_context' not in result

    def test_trace_emission_with_gradient(self):
        """Should emit traces during gradient boosting"""
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
                {'display_name': 'FracFocus', 'files': {}}
            ]
        }

        result = tool.retrieve_all_knowledge(
            data_context=data_context,
            enable_gradient=True
        )

        # Should have called trace_thinking and trace_reasoning
        assert trace_collector.trace_thinking.called
        assert trace_collector.trace_reasoning.called


class TestIntegration:
    """Integration tests combining multiple features"""

    def test_full_workflow(self):
        """Test complete workflow: retrieve + gradient boost + trace"""
        design_kb = Mock()
        design_kb.query.side_effect = [
            [{'pattern': 'master-detail'}],
            [{'pattern': 'progressive'}],
            [{'pattern': 'card-grid'}],
            [{'principle': 'typography'}],
            [{'principle': 'colors'}],
            [{'principle': 'spacing'}],
            [{'constraint': 'css'}],
            [{'constraint': 'state'}],
            [{'constraint': 'events'}]
        ]

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
                    'display_name': 'RRC Production Data',
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

        result = tool.retrieve_all_knowledge(
            data_context=data_context,
            enable_gradient=True
        )

        # Verify all knowledge types retrieved
        assert len(result['ux_patterns']) == 3
        assert len(result['design_principles']) == 3
        assert len(result['gradio_constraints']) == 3

        # Verify gradient context applied
        assert 'gradient_context' in result
        gc = result['gradient_context']
        assert gc['domain_signals']['domain'] == 'petroleum_energy'
        assert gc['domain_signals']['structure'] == 'deeply_nested_directories'
        assert gc['boost_hierarchical_navigation'] is True
        assert gc['boost_tree_views'] is True
        assert gc['boost_data_drill_down'] is True

        # Verify traces emitted
        assert trace_collector.trace_thinking.called
        assert trace_collector.trace_reasoning.called
