"""
Tests for DataDiscoveryTool - Phase 1.5

These tests verify that the centralized data discovery tool behaves correctly
and handles all edge cases for API communication.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.agents.tools.discovery_tool import DataDiscoveryTool
from src.agents.tools.filter_tool import DataFilterTool
import requests


class TestDataDiscoveryToolBasics:
    """Test basic functionality"""

    def test_initialization(self):
        """Should initialize with optional dependencies"""
        tool = DataDiscoveryTool()
        assert tool.filter_tool is None
        assert tool.trace_collector is None

    def test_initialization_with_dependencies(self):
        """Should initialize with filter_tool and trace_collector"""
        filter_tool = Mock()
        trace_collector = Mock()

        tool = DataDiscoveryTool(
            filter_tool=filter_tool,
            trace_collector=trace_collector
        )

        assert tool.filter_tool == filter_tool
        assert tool.trace_collector == trace_collector


class TestSuccessfulAPIFetch:
    """Test successful API data fetching"""

    @patch('requests.get')
    def test_basic_api_fetch(self, mock_get):
        """Should successfully fetch data from API"""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'pipelines': [
                {'id': 'fracfocus', 'metrics': {'file_count': 39}},
                {'id': 'rrc', 'metrics': {'file_count': 25451}}
            ],
            'summary': {
                'total_records': 10000,
                'total_size': '1 GB'
            }
        }
        mock_get.return_value = mock_response

        tool = DataDiscoveryTool()
        result = tool.fetch_data_context()

        assert result['success'] is True
        assert len(result['pipelines']) == 2
        assert result['summary']['total_records'] == 10000
        assert result['error'] is None

    @patch('requests.get')
    def test_api_fetch_with_trace_collector(self, mock_get):
        """Should emit traces when trace_collector is available"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'pipelines': [],
            'summary': {}
        }
        mock_get.return_value = mock_response

        trace_collector = Mock()
        tool = DataDiscoveryTool(trace_collector=trace_collector)
        result = tool.fetch_data_context()

        # Should call trace_thinking and trace_reasoning
        assert trace_collector.trace_thinking.called
        assert trace_collector.trace_reasoning.called


class TestAPIFiltering:
    """Test filtering of API results"""

    @patch('requests.get')
    def test_filter_pipelines_by_sources(self, mock_get):
        """Should filter pipelines when filter_sources is provided"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'pipelines': [
                {'id': 'fracfocus', 'metrics': {}},
                {'id': 'rrc', 'metrics': {}},
                {'id': 'usgs', 'metrics': {}}
            ],
            'summary': {}
        }
        mock_get.return_value = mock_response

        filter_tool = DataFilterTool()
        tool = DataDiscoveryTool(filter_tool=filter_tool)

        result = tool.fetch_data_context(filter_sources=['rrc'])

        assert result['success'] is True
        assert len(result['pipelines']) == 1
        assert result['pipelines'][0]['id'] == 'rrc'

    @patch('requests.get')
    def test_no_filtering_when_filter_sources_none(self, mock_get):
        """Should return all pipelines when filter_sources is None"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'pipelines': [
                {'id': 'fracfocus', 'metrics': {}},
                {'id': 'rrc', 'metrics': {}}
            ],
            'summary': {}
        }
        mock_get.return_value = mock_response

        filter_tool = DataFilterTool()
        tool = DataDiscoveryTool(filter_tool=filter_tool)

        result = tool.fetch_data_context(filter_sources=None)

        assert len(result['pipelines']) == 2

    @patch('requests.get')
    def test_warning_when_filter_sources_but_no_tool(self, mock_get):
        """Should handle filter_sources without filter_tool gracefully"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'pipelines': [
                {'id': 'fracfocus', 'metrics': {}},
                {'id': 'rrc', 'metrics': {}}
            ],
            'summary': {}
        }
        mock_get.return_value = mock_response

        tool = DataDiscoveryTool()  # No filter_tool
        result = tool.fetch_data_context(filter_sources=['rrc'])

        # Should still succeed, just not filter
        assert result['success'] is True
        assert len(result['pipelines']) == 2  # Not filtered


class TestAPIErrors:
    """Test error handling"""

    @patch('requests.get')
    def test_connection_error(self, mock_get):
        """Should handle connection errors gracefully"""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        tool = DataDiscoveryTool()
        result = tool.fetch_data_context()

        assert result['success'] is False
        assert 'Cannot connect to API' in result['error']
        assert result['pipelines'] == []

    @patch('requests.get')
    def test_timeout_error(self, mock_get):
        """Should handle timeout errors"""
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        tool = DataDiscoveryTool()
        result = tool.fetch_data_context()

        assert result['success'] is False
        assert result['error'] is not None
        assert result['pipelines'] == []

    @patch('requests.get')
    def test_http_error(self, mock_get):
        """Should handle HTTP errors (4xx, 5xx)"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
        mock_get.return_value = mock_response

        tool = DataDiscoveryTool()
        result = tool.fetch_data_context()

        assert result['success'] is False
        assert result['error'] is not None

    @patch('requests.get')
    def test_invalid_json(self, mock_get):
        """Should handle invalid JSON response"""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        tool = DataDiscoveryTool()
        result = tool.fetch_data_context()

        assert result['success'] is False
        assert result['error'] is not None

    @patch('requests.get')
    def test_error_with_trace_collector(self, mock_get):
        """Should emit error traces"""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        trace_collector = Mock()
        tool = DataDiscoveryTool(trace_collector=trace_collector)
        result = tool.fetch_data_context()

        assert result['success'] is False
        # Should have called trace_thinking for the error
        assert trace_collector.trace_thinking.called


class TestPipelineFormatting:
    """Test pipeline breakdown formatting"""

    def test_format_multi_location_structure(self):
        """Should format new multi-location structure correctly"""
        tool = DataDiscoveryTool()
        pipelines = [{
            'id': 'fracfocus',
            'display_name': 'FracFocus',
            'files': {
                'locations': {
                    'raw': {
                        'file_count': 10,
                        'size': '1 GB',
                        'file_types': {'.csv': 8, '.json': 2},
                        'row_count': 1000
                    },
                    'interim': {
                        'file_count': 5,
                        'size': '500 MB',
                        'row_count': 900
                    }
                },
                'available_in': ['raw', 'interim']
            },
            'metrics': {'file_count': 15, 'data_size': '1.5 GB'}
        }]

        result = tool._format_pipeline_breakdown(pipelines)

        assert 'FracFocus' in result
        assert 'raw' in result
        assert 'interim' in result
        assert '10 files' in result
        assert '1,000 records' in result

    def test_format_legacy_structure(self):
        """Should format legacy pipeline structure"""
        tool = DataDiscoveryTool()
        pipelines = [{
            'id': 'rrc',
            'display_name': 'RRC',
            'files': {},
            'metrics': {'file_count': 100, 'data_size': '2 GB'}
        }]

        result = tool._format_pipeline_breakdown(pipelines)

        assert 'RRC' in result
        assert '100 files' in result
        assert '2 GB' in result


class TestAPIEndpoint:
    """Test API endpoint configuration"""

    @patch('requests.get')
    def test_custom_api_url(self, mock_get):
        """Should use custom API URL"""
        mock_response = Mock()
        mock_response.json.return_value = {'pipelines': [], 'summary': {}}
        mock_get.return_value = mock_response

        tool = DataDiscoveryTool()
        tool.fetch_data_context(api_url="http://custom:9000")

        mock_get.assert_called_once()
        call_url = mock_get.call_args[0][0]
        assert call_url == "http://custom:9000/api/pipelines"

    @patch('requests.get')
    def test_default_api_url(self, mock_get):
        """Should use default localhost:8000"""
        mock_response = Mock()
        mock_response.json.return_value = {'pipelines': [], 'summary': {}}
        mock_get.return_value = mock_response

        tool = DataDiscoveryTool()
        tool.fetch_data_context()

        call_url = mock_get.call_args[0][0]
        assert call_url == "http://localhost:8000/api/pipelines"


class TestIntegration:
    """Integration tests combining multiple features"""

    @patch('requests.get')
    def test_full_workflow_with_filtering(self, mock_get):
        """Test complete workflow: fetch + filter + trace"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'pipelines': [
                {'id': 'fracfocus', 'metrics': {'file_count': 39}},
                {'id': 'rrc', 'metrics': {'file_count': 25451}},
                {'id': 'production', 'metrics': {'file_count': 100}}
            ],
            'summary': {
                'total_records': 100000,
                'total_size': '5 GB'
            }
        }
        mock_get.return_value = mock_response

        filter_tool = DataFilterTool()
        trace_collector = Mock()
        tool = DataDiscoveryTool(
            filter_tool=filter_tool,
            trace_collector=trace_collector
        )

        result = tool.fetch_data_context(filter_sources=['rrc', 'production'])

        # Verify filtering worked
        assert result['success'] is True
        assert len(result['pipelines']) == 2
        pipeline_ids = [p['id'] for p in result['pipelines']]
        assert set(pipeline_ids) == {'rrc', 'production'}

        # Verify traces were emitted
        assert trace_collector.trace_thinking.called
        assert trace_collector.trace_reasoning.called
