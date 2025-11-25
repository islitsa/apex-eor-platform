"""
Test the new discovery tools in RepositoryIndex
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from knowledge.repository_index import RepositoryIndex

def test_discovery_tools():
    print("="*80)
    print("TESTING DISCOVERY TOOLS")
    print("="*80)

    # Initialize indexer
    indexer = RepositoryIndex()

    # Test 1: Query data sources
    print("\n[TEST 1] Query data sources for 'chemical data'")
    results = indexer.query_data_sources("chemical data", top_k=3)
    print(f"Found {len(results)} results")

    # Debug: print first result structure
    if results:
        print(f"  [DEBUG] First result keys: {results[0].keys()}")

    for i, result in enumerate(results, 1):
        # Handle different result formats
        if 'metadata' in result:
            name = result['metadata'].get('name', 'Unknown')
        else:
            name = result.get('title', result.get('id', 'Unknown'))

        score = result.get('score', 0)
        print(f"  {i}. {name} (score: {score:.3f})")

    # Get first source name for remaining tests
    test_source = None
    if results:
        if 'metadata' in results[0]:
            test_source = results[0]['metadata'].get('name')
        else:
            # Extract from title "Data Source: fracfocus"
            title = results[0].get('title', '')
            if 'Data Source:' in title:
                test_source = title.replace('Data Source:', '').strip()

    if not test_source:
        print("\n[ERROR] No data sources found. Cannot continue testing.")
        return

    print(f"\n[Using '{test_source}' for remaining tests]")

    # Test 2: Get directory structure
    print(f"\n[TEST 2] Get directory structure for '{test_source}'")
    structure = indexer.get_directory_structure(test_source)
    if structure:
        print(f"  Name: {structure['name']}")
        print(f"  Files: {structure.get('file_count', 0)}")
        print(f"  Size: {structure.get('total_size_mb', 0):.1f} MB")
        if 'children' in structure:
            print(f"  Top-level items: {len(structure['children'])}")
            for child in structure['children'][:3]:
                print(f"    - {child['name']} ({child['type']})")
    else:
        print("  [WARNING] No structure returned")

    # Test 3: Get schema
    print(f"\n[TEST 3] Get schema for '{test_source}'")
    schema = indexer.get_schema(test_source)
    if schema:
        print(f"  File: {schema['file']}")
        print(f"  Columns: {len(schema['columns'])}")
        print(f"  First 5 columns: {schema['columns'][:5]}")
        print(f"  Row count: {schema['row_count']:,}")
    else:
        print("  [WARNING] No schema returned (might not have parsed data)")

    # Test 4: Get processing status
    print(f"\n[TEST 4] Get processing status for '{test_source}'")
    status = indexer.get_processing_status(test_source)
    if status:
        print(f"  Status: {status['status']}")
        print(f"  Stages: {', '.join(status['stages'])}")
        print(f"  Files by stage:")
        for stage, count in status['files_by_stage'].items():
            print(f"    - {stage}: {count} files")
    else:
        print("  [WARNING] No status returned")

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_discovery_tools()
