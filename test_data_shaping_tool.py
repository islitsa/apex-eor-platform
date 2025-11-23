"""
Test Data Shaping Tool - Phase 3 Step 1
"""
from src.agents.tools.data_shaping_tool import DataShapingTool


def test_format_pipeline_for_display():
    """Test pipeline formatting"""
    print("Testing format_pipeline_for_display...")

    tool = DataShapingTool()

    # Test 1: Multi-location structure
    pipeline = {
        'id': 'fracfocus',
        'display_name': 'FracFocus',
        'files': {
            'locations': {
                'raw': {
                    'file_count': 10,
                    'size': '1.5 GB',
                    'file_types': {'.csv': 8, '.zip': 2},
                    'row_count': 100000
                },
                'processed': {
                    'file_count': 5,
                    'size': '500 MB',
                    'file_types': {'.parquet': 5},
                    'row_count': 100000
                }
            },
            'available_in': ['raw', 'processed']
        }
    }

    result = tool.format_pipeline_for_display(pipeline)
    assert 'FracFocus' in result
    assert 'raw' in result
    assert 'processed' in result
    assert '10 files' in result
    print("  [PASS] Multi-location structure formatted correctly")

    # Test 2: Legacy subdirs structure
    pipeline_legacy = {
        'id': 'rrc',
        'display_name': 'Railroad Commission',
        'files': {
            'subdirs': {
                'downloads': {
                    'files': [
                        {'size_bytes': 1000000},
                        {'size_bytes': 2000000}
                    ]
                },
                'parsed': {
                    'files': [
                        {'size_bytes': 500000}
                    ]
                }
            }
        }
    }

    result = tool.format_pipeline_for_display(pipeline_legacy)
    assert 'Railroad Commission' in result
    assert 'downloads' in result
    assert 'parsed' in result
    print("  [PASS] Legacy subdirs structure formatted correctly")


def test_format_size():
    """Test size formatting"""
    print("\nTesting format_size...")

    tool = DataShapingTool()

    assert tool.format_size(500) == "500 B"
    assert tool.format_size(5000) == "5.0 KB"
    assert tool.format_size(5000000) == "5.0 MB"
    assert tool.format_size(5000000000) == "5.0 GB"

    print("  [PASS] Size formatting works correctly")


def test_normalize_pipelines():
    """Test pipeline normalization"""
    print("\nTesting normalize_pipelines...")

    tool = DataShapingTool()

    # Test with incomplete pipeline data
    pipelines = [
        {
            'id': 'fracfocus',
            'display_name': 'FracFocus'
            # Missing metrics, files, status
        },
        {
            'id': 'rrc',
            'files': {
                'locations': {
                    'raw': {'file_count': 10, 'row_count': 1000}
                }
            }
            # Missing display_name
        }
    ]

    normalized = tool.normalize_pipelines(pipelines)

    # Check first pipeline
    assert normalized[0]['id'] == 'fracfocus'
    assert normalized[0]['display_name'] == 'FracFocus'
    assert 'metrics' in normalized[0]
    assert 'file_count' in normalized[0]['metrics']

    # Check second pipeline
    assert normalized[1]['id'] == 'rrc'
    assert normalized[1]['display_name'] == 'rrc'  # Falls back to id
    assert normalized[1]['metrics']['file_count'] == 10
    assert normalized[1]['metrics']['record_count'] == 1000

    print("  [PASS] Pipeline normalization works correctly")


def test_compute_summary_metrics():
    """Test summary metrics computation"""
    print("\nTesting compute_summary_metrics...")

    tool = DataShapingTool()

    pipelines = [
        {
            'id': 'fracfocus',
            'metrics': {
                'record_count': 100000,
                'file_count': 10,
                'data_size': '1.5 GB'
            }
        },
        {
            'id': 'rrc',
            'metrics': {
                'record_count': 50000,
                'file_count': 5,
                'data_size': '500 MB'
            }
        }
    ]

    summary = tool.compute_summary_metrics(pipelines)

    assert summary['total_records'] == 150000
    assert summary['total_files'] == 15
    assert summary['datasets_available'] == 2

    print("  [PASS] Summary metrics computed correctly")


def test_extract_record_counts():
    """Test record count extraction"""
    print("\nTesting extract_record_counts...")

    tool = DataShapingTool()

    pipelines = [
        {
            'id': 'fracfocus',
            'metrics': {'record_count': 100000}
        },
        {
            'id': 'rrc',
            'metrics': {'record_count': 50000}
        }
    ]

    record_counts = tool.extract_record_counts(pipelines)

    assert record_counts['fracfocus'] == 100000
    assert record_counts['rrc'] == 50000

    print("  [PASS] Record counts extracted correctly")


def test_extract_sources_list():
    """Test source list extraction"""
    print("\nTesting extract_sources_list...")

    tool = DataShapingTool()

    pipelines = [
        {'id': 'fracfocus'},
        {'id': 'rrc'},
        {'id': 'production'}
    ]

    sources = tool.extract_sources_list(pipelines)

    assert sources == ['fracfocus', 'rrc', 'production']

    print("  [PASS] Sources list extracted correctly")


if __name__ == "__main__":
    print("="*60)
    print("DATA SHAPING TOOL TESTS")
    print("="*60)

    try:
        test_format_pipeline_for_display()
        test_format_size()
        test_normalize_pipelines()
        test_compute_summary_metrics()
        test_extract_record_counts()
        test_extract_sources_list()

        print("\n" + "="*60)
        print("ALL TESTS PASSED!")
        print("="*60)
        print("\nDataShapingTool is working correctly!")
        print("Ready to proceed with ContextAssemblyTool")

    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
