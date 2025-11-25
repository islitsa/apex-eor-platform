"""
Test schema discovery on RRC data (which has parsed files)
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from knowledge.repository_index import RepositoryIndex

def test_rrc_schema():
    print("="*80)
    print("TESTING SCHEMA DISCOVERY ON RRC DATA")
    print("="*80)

    indexer = RepositoryIndex()

    # Test with rrc (has parsed data)
    print("\n[TEST] Get schema for 'rrc'")
    schema = indexer.get_schema("rrc")

    if schema:
        print(f"\n  ✅ Schema retrieved successfully!")
        print(f"  Source: {schema['source']}")
        print(f"  File: {schema['file']}")
        print(f"  Columns: {len(schema['columns'])}")
        print(f"  Row count: {schema['row_count']:,}")
        print(f"\n  First 10 columns:")
        for i, col in enumerate(schema['columns'][:10], 1):
            dtype = schema['dtypes'].get(col, 'unknown')
            print(f"    {i}. {col}: {dtype}")

        print(f"\n  Sample data (first row):")
        if schema['sample']:
            first_row = schema['sample'][0]
            for key, value in list(first_row.items())[:5]:
                print(f"    - {key}: {value}")
    else:
        print("\n  ❌ No schema returned")

    print("\n" + "="*80)

if __name__ == "__main__":
    test_rrc_schema()
