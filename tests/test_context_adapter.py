"""
Tests for Context Adapter

Verifies that the adapter correctly bridges discovery and pipeline contexts.
"""

import pytest
from src.agents.context.adapter import ContextAdapter


class TestContextAdapter:
    """Test suite for ContextAdapter"""

    def test_discovery_context_gets_directory_structure(self):
        """Test that discovery context gets synthetic directory_structure"""
        discovery_context = {
            'data_sources': {
                'fracfocus': {
                    'name': 'fracfocus',
                    'row_count': 13907094,
                    'file_count': 2,
                    'description': 'FRACFOCUS data (2 files)',
                    'discovered': True,
                    'location': 'data/interim/fracfocus'
                }
            },
            'summary': {
                'total_sources': 1,
                'total_records': 13907094
            }
        }

        adapted = ContextAdapter.discovery_to_pipeline(discovery_context)

        # Check that directory_structure was added
        assert 'directory_structure' in adapted['data_sources']['fracfocus']

        # Check that it has files array
        dir_structure = adapted['data_sources']['fracfocus']['directory_structure']
        assert 'files' in dir_structure
        assert 'subdirs' in dir_structure

        # Check that file count matches
        assert len(dir_structure['files']) == 2

        # Check that original fields are preserved
        assert adapted['data_sources']['fracfocus']['row_count'] == 13907094
        assert adapted['data_sources']['fracfocus']['file_count'] == 2

        # Check adaptation metadata
        assert adapted['data_sources']['fracfocus']['_adapted'] == True

    def test_pipeline_context_passes_through(self):
        """Test that pipeline context with directory_structure is unchanged"""
        pipeline_context = {
            'data_sources': {
                'fracfocus': {
                    'name': 'fracfocus',
                    'row_count': 13907094,
                    'directory_structure': {
                        'subdirs': {
                            'parsed': {
                                'files': [
                                    {'name': 'data.parquet', 'size_bytes': 1234567890}
                                ]
                            }
                        }
                    }
                }
            }
        }

        adapted = ContextAdapter.discovery_to_pipeline(pipeline_context)

        # Check that directory_structure is unchanged
        assert adapted['data_sources']['fracfocus']['directory_structure'] == \
               pipeline_context['data_sources']['fracfocus']['directory_structure']

        # Should NOT have adaptation metadata
        assert '_adapted' not in adapted['data_sources']['fracfocus']

    def test_multiple_sources_adapted_correctly(self):
        """Test that multiple sources are all adapted"""
        discovery_context = {
            'data_sources': {
                'fracfocus': {
                    'row_count': 13907094,
                    'file_count': 2,
                    'location': 'data/interim/fracfocus'
                },
                'rrc': {
                    'row_count': 79637354,
                    'file_count': 12,
                    'location': 'data/interim/rrc'
                }
            }
        }

        adapted = ContextAdapter.discovery_to_pipeline(discovery_context)

        # Both sources should have directory_structure
        assert 'directory_structure' in adapted['data_sources']['fracfocus']
        assert 'directory_structure' in adapted['data_sources']['rrc']

        # File counts should match
        assert len(adapted['data_sources']['fracfocus']['directory_structure']['files']) == 2
        assert len(adapted['data_sources']['rrc']['directory_structure']['files']) == 12

    def test_mixed_context_handles_both(self):
        """Test context with both discovery and pipeline sources"""
        mixed_context = {
            'data_sources': {
                'fracfocus': {
                    'row_count': 13907094,
                    'file_count': 2,
                    'location': 'data/interim/fracfocus'
                },
                'rrc': {
                    'row_count': 79637354,
                    'directory_structure': {
                        'subdirs': {
                            'parsed': {
                                'files': [{'name': 'data.parquet', 'size_bytes': 999}]
                            }
                        }
                    }
                }
            }
        }

        adapted = ContextAdapter.discovery_to_pipeline(mixed_context)

        # fracfocus should be adapted
        assert 'directory_structure' in adapted['data_sources']['fracfocus']
        assert adapted['data_sources']['fracfocus']['_adapted'] == True

        # rrc should pass through unchanged
        assert adapted['data_sources']['rrc']['directory_structure']['subdirs']['parsed']['files'][0]['size_bytes'] == 999
        assert '_adapted' not in adapted['data_sources']['rrc']

    def test_empty_context_handled(self):
        """Test that empty context doesn't crash"""
        empty_context = {
            'data_sources': {}
        }

        adapted = ContextAdapter.discovery_to_pipeline(empty_context)

        assert adapted['data_sources'] == {}

    def test_missing_file_count_defaults_to_zero(self):
        """Test that missing file_count creates empty files array"""
        discovery_context = {
            'data_sources': {
                'test_source': {
                    'row_count': 1000,
                    # No file_count!
                }
            }
        }

        adapted = ContextAdapter.discovery_to_pipeline(discovery_context)

        # Should NOT add directory_structure if file_count is missing
        # (this is not discovery context, just incomplete data)
        assert 'directory_structure' not in adapted['data_sources']['test_source']

    def test_summary_passes_through(self):
        """Test that non-data_sources keys pass through unchanged"""
        discovery_context = {
            'data_sources': {
                'fracfocus': {
                    'row_count': 13907094,
                    'file_count': 2,
                }
            },
            'summary': {
                'total_sources': 1,
                'total_records': 13907094,
                'discovery_method': 'real_data_discovery'
            },
            'initial_prompt': 'Create a dashboard'
        }

        adapted = ContextAdapter.discovery_to_pipeline(discovery_context)

        # Check that other keys are preserved
        assert adapted['summary'] == discovery_context['summary']
        assert adapted['initial_prompt'] == discovery_context['initial_prompt']

    def test_is_discovery_context_true(self):
        """Test detection of discovery context"""
        discovery_source = {
            'row_count': 13907094,
            'file_count': 2,
            'location': 'data/interim/fracfocus'
        }

        assert ContextAdapter.is_discovery_context(discovery_source) == True

    def test_is_discovery_context_false(self):
        """Test detection of non-discovery context"""
        pipeline_source = {
            'row_count': 13907094,
            'directory_structure': {
                'subdirs': {}
            }
        }

        assert ContextAdapter.is_discovery_context(pipeline_source) == False

    def test_is_pipeline_context_true(self):
        """Test detection of pipeline context"""
        pipeline_source = {
            'directory_structure': {
                'subdirs': {}
            }
        }

        assert ContextAdapter.is_pipeline_context(pipeline_source) == True

    def test_is_pipeline_context_false(self):
        """Test detection of non-pipeline context"""
        discovery_source = {
            'row_count': 13907094,
            'file_count': 2
        }

        assert ContextAdapter.is_pipeline_context(discovery_source) == False

    def test_synthetic_file_names(self):
        """Test that synthetic files have reasonable names"""
        discovery_context = {
            'data_sources': {
                'test': {
                    'file_count': 3,
                    'location': '/nonexistent/path'  # Will trigger synthetic files
                }
            }
        }

        adapted = ContextAdapter.discovery_to_pipeline(discovery_context)

        files = adapted['data_sources']['test']['directory_structure']['files']
        assert len(files) == 3

        # Check file naming
        assert files[0]['name'] == 'file_0.parquet'
        assert files[1]['name'] == 'file_1.parquet'
        assert files[2]['name'] == 'file_2.parquet'

        # Size should be 0 for synthetic files
        assert all(f['size_bytes'] == 0 for f in files)

    def test_adapter_version_in_metadata(self):
        """Test that adapter version is recorded"""
        discovery_context = {
            'data_sources': {
                'test': {
                    'file_count': 1
                }
            }
        }

        adapted = ContextAdapter.discovery_to_pipeline(discovery_context)

        assert adapted['data_sources']['test']['_adapter_version'] == '1.0'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
