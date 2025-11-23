"""
Validation script - Test discovery with different gradient contexts
Run this to validate the findings yourself
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agents.context.discovery_tools_instrumented import InstrumentedDiscoveryTools


def test_scenario(name, gradient_context, test_queries):
    """Test a specific scenario with multiple queries"""
    print(f"\n{'='*80}")
    print(f"SCENARIO: {name}")
    print(f"{'='*80}\n")

    if gradient_context:
        print(f"Gradient context keys: {list(gradient_context.keys())}")
    else:
        print("No gradient context")

    tools = InstrumentedDiscoveryTools(gradient_context=gradient_context)
    session_id = tools.start_session(f"validation_{name.lower().replace(' ', '_')}")

    for query_desc, query, operations in test_queries:
        print(f"\n--- {query_desc} ---")

        try:
            # Find sources
            if 'find' in operations:
                sources = tools.find_data_sources(query, top_k=3)
                print(f"  Found {len(sources)} sources")

                # Get details for first source
                if sources and ('schema' in operations or 'status' in operations):
                    source_name = sources[0]['name']
                    print(f"  Exploring: {source_name}")

                    if 'schema' in operations:
                        schema = tools.get_schema(source_name)
                        if schema:
                            print(f"    ✓ Schema: {len(schema['columns'])} columns, {schema['row_count']:,} rows")

                    if 'status' in operations:
                        status = tools.check_status(source_name)
                        if status:
                            print(f"    ✓ Status: {status['status']}")

                    if 'explore' in operations:
                        structure = tools.explore_directory(source_name)
                        if structure:
                            print(f"    ✓ Structure: {structure['file_count']} files")

        except Exception as e:
            print(f"  ✗ ERROR: {e}")

    # End session and get results
    session = tools.end_session()
    return session


def main():
    print("\n" + "="*80)
    print("DISCOVERY INSTRUMENTATION VALIDATION")
    print("="*80)
    print("\nThis will test discovery with 3 different gradient contexts:")
    print("  1. No context (baseline)")
    print("  2. Topology hints (current gradient context)")
    print("  3. Path coordinates (ChatGPT's suggestion)")
    print("\nResults will be saved to logs/discovery/\n")

    # Define test queries
    test_queries = [
        ("Find chemical data", "chemical data", ['find', 'schema', 'status']),
        ("Find production data", "production wells", ['find', 'status']),
        ("Find completion data", "well completions", ['find']),
    ]

    # Scenario 1: No gradient context
    session1 = test_scenario(
        "No Context",
        gradient_context={},
        test_queries=test_queries
    )

    # Scenario 2: Current gradient context (topology only)
    session2 = test_scenario(
        "Topology Hints",
        gradient_context={
            'structure': 'deeply_nested_directories',
            'max_depth': 4,
            'data_root': 'data/raw',
            'processing_stages': ['downloads', 'extracted', 'parsed']
        },
        test_queries=test_queries
    )

    # Scenario 3: With path coordinates (ChatGPT's suggestion)
    session3 = test_scenario(
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
                },
                'rrc': {
                    'root_path': 'data/raw/rrc',
                    'production': {
                        'downloads': ['production.csv'],
                        'parsed': ['production_processed.parquet']
                    }
                }
            }
        },
        test_queries=test_queries
    )

    # Print comparison
    print("\n" + "="*80)
    print("VALIDATION RESULTS")
    print("="*80)

    def print_comparison(name, session):
        print(f"\n{name}:")
        print(f"  Success rate: {session.success_rate*100:.1f}%")
        print(f"  Total duration: {session.total_duration_ms:.1f}ms")
        print(f"  Avg per operation: {session.avg_duration_ms:.1f}ms")
        print(f"  Failed operations: {session.failed_attempts}")
        print(f"  Navigation errors: {len(session.navigation_errors)}")
        print(f"  Missing hints:")
        print(f"    - Path coordinates: {session.missing_path_hints}")
        print(f"    - Structure hints: {session.missing_structure_hints}")
        print(f"    - File patterns: {session.missing_file_hints}")

    print_comparison("1. No Context", session1)
    print_comparison("2. Topology Hints", session2)
    print_comparison("3. Path Coordinates", session3)

    # Key findings
    print("\n" + "="*80)
    print("KEY FINDINGS")
    print("="*80)

    # Check if path coordinates made a difference
    if session3.success_rate > session1.success_rate:
        print("\n✓ Path coordinates IMPROVED success rate!")
        print(f"  Baseline: {session1.success_rate*100:.1f}%")
        print(f"  With paths: {session3.success_rate*100:.1f}%")
    elif session3.avg_duration_ms < session1.avg_duration_ms * 0.9:
        print("\n✓ Path coordinates IMPROVED performance!")
        print(f"  Baseline: {session1.avg_duration_ms:.1f}ms")
        print(f"  With paths: {session3.avg_duration_ms:.1f}ms")
    elif len(session3.navigation_errors) < len(session1.navigation_errors):
        print("\n✓ Path coordinates REDUCED navigation errors!")
        print(f"  Baseline: {len(session1.navigation_errors)} errors")
        print(f"  With paths: {len(session3.navigation_errors)} errors")
    else:
        print("\n✗ Path coordinates did NOT make a measurable difference")
        print(f"  Success rate: {session1.success_rate*100:.1f}% → {session3.success_rate*100:.1f}%")
        print(f"  Performance: {session1.avg_duration_ms:.1f}ms → {session3.avg_duration_ms:.1f}ms")
        print(f"  Navigation errors: {len(session1.navigation_errors)} → {len(session3.navigation_errors)}")

    # Check what's slow
    print("\n" + "="*80)
    print("PERFORMANCE BREAKDOWN")
    print("="*80)

    print("\nSlowest operations (from 'No Context' baseline):")
    for i, op in enumerate(session1.slowest_operations[:5], 1):
        print(f"  {i}. {op['method']}: {op['query']}")
        print(f"     Duration: {op['duration_ms']:.1f}ms")

    print("\n" + "="*80)
    print(f"\nDetailed logs saved to: logs/discovery/")
    print("Run 'python analyze_discovery_results.py' to see full analysis")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
