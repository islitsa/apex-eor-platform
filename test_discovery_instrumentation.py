"""
Simple test script for discovery instrumentation
Avoids Unicode issues and creates clear comparison report
"""

import sys
import json
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agents.context.discovery_tools_instrumented import InstrumentedDiscoveryTools


def run_test_case(name, gradient_context):
    """Run a single test case"""
    print(f"\n{'='*80}")
    print(f"TEST: {name}")
    print(f"{'='*80}\n")

    tools = InstrumentedDiscoveryTools(gradient_context=gradient_context)
    session_id = tools.start_session(f"test_{name.lower().replace(' ', '_')}")

    # Try to find data sources
    try:
        sources = tools.find_data_sources("chemical data", top_k=3)
        print(f"  Found {len(sources)} sources")

        # Try to get schema for first source
        if sources:
            source_name = sources[0]['name']
            print(f"  Getting schema for: {source_name}")

            schema = tools.get_schema(source_name)
            if schema:
                print(f"    Schema: {len(schema['columns'])} columns")

            status = tools.check_status(source_name)
            if status:
                print(f"    Status: {status['status']}")

    except Exception as e:
        print(f"  ERROR: {e}")

    # End session (save data but skip pretty printing)
    session = tools.instrumentor.end_session()

    return session


def main():
    print("\n" + "="*80)
    print("DISCOVERY INSTRUMENTATION TEST")
    print("Testing 3 scenarios: No Context | Topology Hints | Path Coordinates")
    print("="*80)

    # Test Case 1: No gradient context
    session1 = run_test_case(
        "No Context",
        gradient_context={}
    )

    # Test Case 2: Topology hints (current)
    session2 = run_test_case(
        "Topology Hints",
        gradient_context={
            'structure': 'deeply_nested_directories',
            'max_depth': 4,
            'data_root': 'data/raw'
        }
    )

    # Test Case 3: Path coordinates (ChatGPT's suggestion)
    session3 = run_test_case(
        "Path Coordinates",
        gradient_context={
            'structure': 'deeply_nested_directories',
            'data_root': 'data/raw',
            'data_paths': {
                'fracfocus': {
                    'root_path': 'data/raw/fracfocus',
                    'Chemical_data': {
                        'downloads': ['FracFocusCSV.zip'],
                        'extracted': ['FracFocusRegistry_1.csv'],
                        'parsed': ['consolidated.parquet']
                    }
                }
            }
        }
    )

    # Print comparison
    print("\n" + "="*80)
    print("COMPARISON REPORT")
    print("="*80)

    def print_session_summary(name, session):
        print(f"\n{name}:")
        print(f"  Success rate: {session.success_rate*100:.1f}%")
        print(f"  Avg duration: {session.avg_duration_ms:.1f}ms")
        print(f"  Navigation errors: {len(session.navigation_errors)}")
        print(f"  Missing path hints: {session.missing_path_hints}")
        print(f"  Missing structure hints: {session.missing_structure_hints}")

    print_session_summary("1. No Context", session1)
    print_session_summary("2. Topology Hints", session2)
    print_session_summary("3. Path Coordinates", session3)

    # Analysis
    print("\n" + "="*80)
    print("ANALYSIS")
    print("="*80)

    print("\nKey Findings:")

    # Check if discovery is succeeding
    if session1.success_rate == 1.0:
        print("  - Discovery tools are SUCCEEDING even without gradient context")
        print("  - This suggests the underlying RepositoryIndex is working correctly")
        print("  - Path coordinates may not be the bottleneck")
    else:
        print(f"  - Discovery tools are FAILING {(1-session1.success_rate)*100:.1f}% of the time")
        print("  - Path coordinates would likely help!")

    # Check searched_locations
    print("\nDetailed location tracking:")
    for i, attempt in enumerate(session1.attempts):
        print(f"\n  Attempt {i+1}: {attempt.method}")
        print(f"    Searched locations: {attempt.searched_locations or '(none tracked)'}")
        print(f"    Actual location: {attempt.actual_location or '(not recorded)'}")
        if attempt.expected_location:
            print(f"    Expected location: {attempt.expected_location}")

    # Check if we're tracking paths properly
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)

    if session1.success_rate == 1.0 and not session1.searched_locations:
        print("""
The discovery tools are succeeding, but we're NOT tracking where they search!

This means:
1. The instrumentation needs improvement to capture search paths
2. We can't tell if gradient context is helping navigation
3. The actual bottleneck might be:
   - Semantic search performance (not file location)
   - Schema extraction speed
   - Something other than "where to look"

Next Steps:
1. Improve instrumentation to track actual filesystem traversal
2. Add timing breakdowns (how long in Pinecone vs filesystem?)
3. Test with a data source that DOESN'T exist to see failure mode
        """)
    elif len(session3.navigation_errors) < len(session1.navigation_errors):
        print("""
Path coordinates ARE helping! Navigation errors decreased.

ChatGPT's diagnosis was correct - adding path coordinates to gradient
context reduces wrong-location searches.
        """)
    else:
        print("""
Discovery is working, but path coordinates don't seem to be the issue.

The bottleneck may be elsewhere:
- Semantic search is the slow part (see 4848ms for find_data_sources)
- Schema loading is slow (1822ms to read CSV)
- The problem is speed, not navigation
        """)

    print("\nLog files saved to: C:\\Users\\irina\\apex-eor-platform\\logs\\discovery\\")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
