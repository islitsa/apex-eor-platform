"""
Test script to verify discovery finds sources correctly
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agents.context.discovery_tools import DiscoveryTools


def test_find_sources():
    """Test if discovery finds sources with actual data"""

    print("="*80)
    print("DISCOVERY SOURCE TEST")
    print("="*80)

    tools = DiscoveryTools()

    # Test 1: Find all sources
    print("\n[TEST 1] Finding chemical data sources...")
    sources = tools.find_data_sources("chemical data", top_k=10, min_relevance=0.3)

    print(f"\nFound {len(sources)} sources:")
    for i, source in enumerate(sources, 1):
        print(f"\n{i}. {source['name']}")
        print(f"   Relevance: {source['relevance']:.3f}")
        print(f"   ID: {source['id']}")

        # Test 2: Get detailed status for each source
        print(f"\n   Checking status...")
        status = tools.check_status(source['name'])

        if status:
            print(f"   Status: {status['status']}")
            print(f"   Stages: {', '.join(status['stages'])}")
            print(f"   Files by stage:")
            for stage, count in status.get('files_by_stage', {}).items():
                print(f"     - {stage}: {count} files")
        else:
            print(f"   ⚠ No status found")

        # Test 3: Try to get schema
        print(f"\n   Getting schema...")
        schema = tools.get_schema(source['name'])

        if schema:
            print(f"   [OK] Schema found!")
            print(f"     File: {schema['file']}")
            print(f"     Columns: {len(schema['columns'])}")
            print(f"     Rows: {schema['row_count']:,}")
        else:
            print(f"   [FAIL] No schema found")

        # Test 4: Explore directory structure
        print(f"\n   Exploring directory...")
        structure = tools.explore_directory(source['name'])

        if structure:
            print(f"   [OK] Structure found!")
            print(f"     Total files: {structure.get('file_count', 0):,}")
            print(f"     Total size: {structure.get('total_size_mb', 0):.2f} MB")
        else:
            print(f"   [FAIL] No structure found")

    # Test 5: Check what's in the filesystem
    print("\n" + "="*80)
    print("FILESYSTEM CHECK")
    print("="*80)

    data_dir = Path("data/raw")
    if data_dir.exists():
        print(f"\n[OK] Data directory exists: {data_dir}")

        for source_dir in data_dir.iterdir():
            if source_dir.is_dir():
                print(f"\n  Source: {source_dir.name}")

                # Count files
                file_count = sum(1 for _ in source_dir.rglob('*') if _.is_file())
                print(f"    Total files: {file_count}")

                # Check for subdirs
                subdirs = [d.name for d in source_dir.iterdir() if d.is_dir()]
                if subdirs:
                    print(f"    Subdirectories: {', '.join(subdirs[:5])}")

                # Look for parsed data
                parsed_dir = source_dir / 'parsed'
                if not parsed_dir.exists():
                    # Try nested structure
                    parsed_dirs = list(source_dir.rglob('parsed'))
                    if parsed_dirs:
                        parsed_dir = parsed_dirs[0]
                        print(f"    [OK] Found nested parsed dir: {parsed_dir.relative_to(source_dir)}")
                    else:
                        print(f"    [FAIL] No parsed directory found")
                        continue

                if parsed_dir.exists():
                    parsed_files = list(parsed_dir.glob('*'))
                    print(f"    Parsed files: {len(parsed_files)}")
                    if parsed_files:
                        for f in parsed_files[:3]:
                            size_mb = f.stat().st_size / (1024 * 1024)
                            print(f"      - {f.name} ({size_mb:.2f} MB)")
    else:
        print(f"\n[FAIL] Data directory not found: {data_dir}")

    print("\n" + "="*80)
    print("DIAGNOSIS")
    print("="*80)

    if len(sources) == 0:
        print("\n[FAIL] PROBLEM: Discovery found NO sources")
        print("  Possible causes:")
        print("  1. Pinecone index is empty (run indexing)")
        print("  2. Query doesn't match indexed content")
        print("  3. min_relevance threshold too high")
    elif any(tools.get_schema(s['name']) is None for s in sources):
        print("\n[WARN] WARNING: Some sources have no schema")
        print("  Possible causes:")
        print("  1. No parsed files exist")
        print("  2. Parsed files in unexpected location")
        print("  3. File format not supported (need .csv or .parquet)")
    else:
        print("\n[OK] SUCCESS: Discovery is working correctly!")
        print(f"  Found {len(sources)} sources with schemas")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    test_find_sources()
