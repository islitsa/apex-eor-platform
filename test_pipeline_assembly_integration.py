"""
Test Pipeline Assembly Integration

This test validates that the PipelineAssemblyTool works correctly
and integrates properly with the orchestrator workflow.
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.agents.tools.pipeline_assembly_tool import PipelineAssemblyTool


def test_pipeline_assembly_basic():
    """Test basic pipeline assembly with mock data_context."""
    print("\n" + "="*80)
    print("TEST 1: Basic Pipeline Assembly")
    print("="*80)

    # Create mock data_context (simulating DataDiscoveryTool output)
    data_context = {
        'data_sources': {
            'Chemical_data': {
                'name': 'Chemical Data',
                'file_count': 150,
                'row_count': 50000,
                'total_size_bytes': 1024 * 1024 * 500,  # 500 MB
                'location': 'data/raw/Chemical_data',
                'file_list': [
                    {'name': 'chemicals.csv', 'size_bytes': 1024 * 1024 * 100},
                    {'name': 'metadata.json', 'size_bytes': 1024 * 50}
                ]
            },
            'RRC': {
                'name': 'Railroad Commission',
                'file_count': 200,
                'row_count': 100000,
                'total_size_bytes': 1024 * 1024 * 1000,  # 1 GB
                'location': 'data/raw/RRC',
                'file_list': [
                    {'name': 'wells.csv', 'size_bytes': 1024 * 1024 * 500},
                    {'name': 'production.csv', 'size_bytes': 1024 * 1024 * 500}
                ]
            }
        },
        'summary': {
            'total_sources': 2,
            'total_files': 350,
            'total_records': 150000,
            'total_size_bytes': 1024 * 1024 * 1500
        }
    }

    # Initialize PipelineAssemblyTool
    tool = PipelineAssemblyTool(data_root="data/raw")

    # Assemble pipelines
    pipelines = tool.assemble_pipelines(data_context)

    # Validate results
    print("\n[Validation]")
    print(f"  Pipelines created: {len(pipelines)}")
    assert len(pipelines) == 2, f"Expected 2 pipelines, got {len(pipelines)}"

    for pipeline in pipelines:
        print(f"\n  Pipeline: {pipeline['display_name']}")
        print(f"    ID: {pipeline['id']}")
        print(f"    Status: {pipeline['status']}")
        print(f"    Metrics:")
        print(f"      - file_count: {pipeline['metrics']['file_count']}")
        print(f"      - record_count: {pipeline['metrics']['record_count']}")
        print(f"      - data_size: {pipeline['metrics']['data_size']}")
        print(f"    Stages: {len(pipeline['stages'])}")
        for stage in pipeline['stages']:
            print(f"      - {stage['name']}: {stage['status']} ({stage['file_count']} files)")
        print(f"    Files: {len(pipeline['files'])}")

        # Validate schema
        assert 'id' in pipeline
        assert 'name' in pipeline
        assert 'display_name' in pipeline
        assert 'status' in pipeline
        assert 'metrics' in pipeline
        assert 'stages' in pipeline
        assert 'files' in pipeline

        # Validate metrics use canonical fields
        assert 'file_count' in pipeline['metrics']
        assert 'record_count' in pipeline['metrics']
        assert 'data_size' in pipeline['metrics']

        # Validate no forbidden fields
        assert 'total_records' not in pipeline['metrics']
        assert 'total_files' not in pipeline['metrics']
        assert 'children' not in pipeline
        assert 'subdirectories' not in pipeline

    print("\n[OK] All schema validations passed!")


def test_pipeline_assembly_with_context_update():
    """Test that update_data_context_with_pipelines works correctly."""
    print("\n" + "="*80)
    print("TEST 2: Pipeline Assembly with Context Update")
    print("="*80)

    # Mock data_context
    data_context = {
        'data_sources': {
            'test_source': {
                'name': 'Test Source',
                'file_count': 10,
                'row_count': 1000,
                'total_size_bytes': 1024 * 100,
                'location': 'data/raw/test_source',
                'file_list': []
            }
        }
    }

    # Initialize tool
    tool = PipelineAssemblyTool(data_root="data/raw")

    # Assemble pipelines
    pipelines = tool.assemble_pipelines(data_context)

    # Update context
    updated_context = tool.update_data_context_with_pipelines(data_context, pipelines)

    # Validate
    print("\n[Validation]")
    assert 'pipelines' in updated_context, "Missing 'pipelines' key in updated context"
    assert len(updated_context['pipelines']) == 1, "Expected 1 pipeline in updated context"
    assert updated_context['pipelines'][0]['id'] == 'test_source'

    print(f"  [OK] Updated context contains {len(updated_context['pipelines'])} pipeline(s)")
    print(f"  [OK] Pipeline ID: {updated_context['pipelines'][0]['id']}")

    print("\n[OK] Context update validation passed!")


def test_schema_enforcement():
    """Test that schema validation catches forbidden fields."""
    print("\n" + "="*80)
    print("TEST 3: Schema Enforcement")
    print("="*80)

    tool = PipelineAssemblyTool()

    # Valid pipeline
    valid_pipeline = {
        'id': 'test',
        'name': 'test',
        'display_name': 'Test',
        'status': 'active',
        'metrics': {
            'file_count': 10,
            'record_count': 1000,  # CANONICAL
            'data_size': 1024
        },
        'stages': [
            {
                'name': 'downloads',
                'file_count': 5,
                'total_size_bytes': 512,
                'status': 'complete'
            }
        ],
        'files': []
    }

    # Should pass validation
    try:
        tool._validate_pipeline_schema(valid_pipeline)
        print("  [OK] Valid pipeline passed validation")
    except Exception as e:
        print(f"  [FAIL] Valid pipeline failed validation: {e}")
        raise

    # Invalid pipeline with forbidden field
    invalid_pipeline = valid_pipeline.copy()
    invalid_pipeline['metrics']['total_records'] = 1000  # FORBIDDEN

    # Should fail validation
    try:
        tool._validate_pipeline_schema(invalid_pipeline)
        print("  [FAIL] Invalid pipeline passed validation (should have failed!)")
        raise AssertionError("Validation should have caught forbidden field")
    except ValueError as e:
        print(f"  [OK] Invalid pipeline correctly rejected: {e}")

    print("\n[OK] Schema enforcement validation passed!")


def main():
    """Run all integration tests."""
    print("\n" + "="*80)
    print("PIPELINE ASSEMBLY INTEGRATION TESTS")
    print("="*80)

    try:
        test_pipeline_assembly_basic()
        test_pipeline_assembly_with_context_update()
        test_schema_enforcement()

        print("\n" + "="*80)
        print("ALL TESTS PASSED [OK]")
        print("="*80)
        print("\n[Summary]")
        print("  PipelineAssemblyTool is working correctly")
        print("  Schema validation is enforcing canonical fields")
        print("  Context update is propagating pipelines correctly")
        print("\n[Next Steps]")
        print("  1. Initialize PipelineAssemblyTool in UI Orchestrator")
        print("  2. Test with real filesystem data")
        print("  3. Run full generation workflow")
        print("  4. Validate React code uses canonical fields")

    except Exception as e:
        print("\n" + "="*80)
        print("TESTS FAILED [X]")
        print("="*80)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
