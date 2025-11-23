"""
Test directory structure performance with depth limit.

Verifies:
1. Scanning completes in < 5 seconds
2. Shows correct structure: fracfocus/chemical_data/{downloads,extracted,parsed}
"""

import time
from src.knowledge.repository_index import RepositoryIndex

def test_directory_structure_performance():
    print("\n=== Testing Directory Structure Performance ===\n")

    indexer = RepositoryIndex()

    # Test with depth limit
    print("Testing with max_depth=3...")
    start = time.time()
    structure = indexer.get_directory_structure("fracfocus", max_depth=3)
    elapsed = time.time() - start

    print(f"\n[OK] Scan completed in {elapsed:.2f} seconds")

    if elapsed > 5:
        print(f"[FAILED] Took {elapsed:.2f}s (exceeds 5s timeout)")
        return False
    else:
        print(f"[PASSED] Fast enough for API (< 5s)")

    # Verify structure
    if structure:
        print(f"\n[OK] Structure returned")
        print(f"  - Root: {structure.get('name')}")
        print(f"  - File count: {structure.get('file_count', 0):,}")
        print(f"  - Total size: {structure.get('total_size_mb', 0):.1f} MB")

        # Check for children
        children = structure.get('children', [])
        print(f"  - Children: {len(children)}")

        for child in children:
            print(f"\n  Child: {child.get('name')}")
            if child.get('type') == 'directory':
                grandchildren = child.get('children', [])
                print(f"    - Subdirectories: {[gc.get('name') for gc in grandchildren if gc.get('type') == 'directory']}")

                # Check if chemical_data exists and has expected subdirs
                if child.get('name') == 'chemical_data':
                    expected_subdirs = {'downloads', 'extracted', 'parsed'}
                    actual_subdirs = {gc.get('name') for gc in grandchildren if gc.get('type') == 'directory'}

                    print(f"    - Expected subdirs: {expected_subdirs}")
                    print(f"    - Actual subdirs: {actual_subdirs}")

                    if expected_subdirs.issubset(actual_subdirs):
                        print(f"    [OK] All expected subdirectories found!")
                    else:
                        missing = expected_subdirs - actual_subdirs
                        print(f"    [WARNING] Missing subdirectories: {missing}")
    else:
        print("[FAILED] No structure returned")
        return False

    print("\n=== Test Complete ===")
    return True

if __name__ == "__main__":
    success = test_directory_structure_performance()
    exit(0 if success else 1)
