"""
Quick verification for Phase 1.5: DataDiscoveryTool

This script verifies that the discovery tool works correctly without starting Agent Studio.
"""

from unittest.mock import Mock, patch
from src.agents.tools.discovery_tool import DataDiscoveryTool
from src.agents.tools.filter_tool import DataFilterTool


def test_initialization():
    """Test that tool initializes correctly"""
    print("=" * 80)
    print("TEST 1: Initialization")
    print("=" * 80)

    tool = DataDiscoveryTool()
    if tool.filter_tool is None and tool.trace_collector is None:
        print("[PASS] Tool initialized without dependencies")
    else:
        print("[FAIL] Unexpected initialization state")
        return False

    filter_tool = DataFilterTool()
    trace_collector = Mock()
    tool2 = DataDiscoveryTool(filter_tool=filter_tool, trace_collector=trace_collector)

    if tool2.filter_tool == filter_tool and tool2.trace_collector == trace_collector:
        print("[PASS] Tool initialized with dependencies")
        return True
    else:
        print("[FAIL] Dependencies not set correctly")
        return False


def test_successful_fetch():
    """Test successful API fetch (mocked)"""
    print("\n" + "=" * 80)
    print("TEST 2: Successful API Fetch")
    print("=" * 80)

    with patch('requests.get') as mock_get:
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'pipelines': [
                {'id': 'fracfocus', 'metrics': {'file_count': 39}},
                {'id': 'rrc', 'metrics': {'file_count': 25451}}
            ],
            'summary': {
                'total_records': 100000,
                'total_size': '5 GB'
            }
        }
        mock_get.return_value = mock_response

        tool = DataDiscoveryTool()
        result = tool.fetch_data_context()

        if result['success'] and len(result['pipelines']) == 2:
            print(f"[PASS] Successfully fetched {len(result['pipelines'])} pipelines")
            print(f"       Summary: {result['summary']['total_records']:,} records")
            return True
        else:
            print(f"[FAIL] Expected success=True and 2 pipelines, got: {result}")
            return False


def test_filtering():
    """Test filtering of pipelines"""
    print("\n" + "=" * 80)
    print("TEST 3: Pipeline Filtering")
    print("=" * 80)

    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {
            'pipelines': [
                {'id': 'fracfocus', 'metrics': {}},
                {'id': 'rrc', 'metrics': {}},
                {'id': 'production', 'metrics': {}}
            ],
            'summary': {}
        }
        mock_get.return_value = mock_response

        filter_tool = DataFilterTool()
        tool = DataDiscoveryTool(filter_tool=filter_tool)

        result = tool.fetch_data_context(filter_sources=['rrc', 'production'])

        if result['success'] and len(result['pipelines']) == 2:
            pipeline_ids = [p['id'] for p in result['pipelines']]
            if set(pipeline_ids) == {'rrc', 'production'}:
                print(f"[PASS] Correctly filtered to {pipeline_ids}")
                return True
            else:
                print(f"[FAIL] Expected ['rrc', 'production'], got {pipeline_ids}")
                return False
        else:
            print(f"[FAIL] Filtering failed: {result}")
            return False


def test_error_handling():
    """Test error handling"""
    print("\n" + "=" * 80)
    print("TEST 4: Error Handling")
    print("=" * 80)

    import requests

    with patch('requests.get') as mock_get:
        # Simulate connection error
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        tool = DataDiscoveryTool()
        result = tool.fetch_data_context()

        if not result['success'] and 'Cannot connect to API' in result['error']:
            print("[PASS] Connection error handled correctly")
            print(f"       Error message: {result['error']}")
            return True
        else:
            print(f"[FAIL] Expected connection error handling, got: {result}")
            return False


def test_trace_integration():
    """Test trace collector integration"""
    print("\n" + "=" * 80)
    print("TEST 5: Trace Collector Integration")
    print("=" * 80)

    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {
            'pipelines': [{'id': 'fracfocus', 'metrics': {}}],
            'summary': {}
        }
        mock_get.return_value = mock_response

        trace_collector = Mock()
        tool = DataDiscoveryTool(trace_collector=trace_collector)
        result = tool.fetch_data_context()

        if trace_collector.trace_thinking.called and trace_collector.trace_reasoning.called:
            print("[PASS] Trace collector called correctly")
            print(f"       trace_thinking calls: {trace_collector.trace_thinking.call_count}")
            print(f"       trace_reasoning calls: {trace_collector.trace_reasoning.call_count}")
            return True
        else:
            print("[FAIL] Trace collector not called")
            return False


def main():
    """Run all verification tests"""
    print("\n")
    print("+" + "=" * 78 + "+")
    print("|" + " " * 20 + "DataDiscoveryTool Verification" + " " * 27 + "|")
    print("+" + "=" * 78 + "+")
    print()

    try:
        test1 = test_initialization()
        test2 = test_successful_fetch()
        test3 = test_filtering()
        test4 = test_error_handling()
        test5 = test_trace_integration()

        print("\n" + "=" * 80)
        if test1 and test2 and test3 and test4 and test5:
            print("[PASS] ALL TESTS PASSED")
            print("   DataDiscoveryTool is working correctly!")
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
