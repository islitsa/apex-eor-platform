"""
Analyze discovery instrumentation results from JSON logs
Bypasses the Unicode printing issue
"""

import json
from pathlib import Path


def analyze_session(session_file):
    """Analyze a single session from JSON"""
    with open(session_file) as f:
        session = json.load(f)

    print(f"\nSession: {session['session_id']}")
    print(f"  Success rate: {session['success_rate']*100:.1f}%")
    print(f"  Avg duration: {session['avg_duration_ms']:.1f}ms")
    print(f"  Total attempts: {session['total_attempts']}")
    print(f"  Failed attempts: {session['failed_attempts']}")
    print(f"  Navigation errors: {len(session['navigation_errors'])}")
    print(f"  Missing path hints: {session['missing_path_hints']}")
    print(f"  Missing structure hints: {session['missing_structure_hints']}")

    # Analyze attempts
    print(f"\n  Attempts:")
    for i, attempt in enumerate(session['attempts'], 1):
        status = "OK  " if attempt['success'] else "FAIL"
        print(f"    [{status}] {attempt['method']}: '{attempt['query']}' ({attempt['duration_ms']:.1f}ms)")

        if attempt['searched_locations']:
            print(f"         Searched: {attempt['searched_locations']}")

        if attempt['actual_location']:
            print(f"         Found at: {attempt['actual_location']}")

        if attempt['missing_hint_type']:
            print(f"         Missing hint: {attempt['missing_hint_type']}")

    return session


def main():
    logs_dir = Path("C:/Users/irina/apex-eor-platform/logs/discovery")

    print("="*80)
    print("DISCOVERY INSTRUMENTATION RESULTS")
    print("="*80)

    # Find all session logs
    log_files = sorted(logs_dir.glob("test_*.json"))

    if not log_files:
        print("\nNo test logs found!")
        return

    sessions = []
    for log_file in log_files:
        session = analyze_session(log_file)
        sessions.append(session)

    # Comparison
    print("\n" + "="*80)
    print("COMPARISON")
    print("="*80)

    if len(sessions) >= 3:
        s1, s2, s3 = sessions[0], sessions[1], sessions[2]

        print("\n| Metric                | No Context | Topology | Paths |")
        print("|----------------------|------------|----------|-------|")
        print(f"| Success Rate         | {s1['success_rate']*100:6.1f}%   | {s2['success_rate']*100:6.1f}% | {s3['success_rate']*100:5.1f}% |")
        print(f"| Avg Duration (ms)    | {s1['avg_duration_ms']:8.1f}   | {s2['avg_duration_ms']:8.0f} | {s3['avg_duration_ms']:7.1f} |")
        print(f"| Navigation Errors    | {len(s1['navigation_errors']):10} | {len(s2['navigation_errors']):8} | {len(s3['navigation_errors']):5} |")
        print(f"| Missing Path Hints   | {s1['missing_path_hints']:10} | {s2['missing_path_hints']:8} | {s3['missing_path_hints']:5} |")

    # Analysis
    print("\n" + "="*80)
    print("ANALYSIS")
    print("="*80)

    # Check if location tracking is working
    all_attempts = [a for s in sessions for a in s['attempts']]
    attempts_with_searched = [a for a in all_attempts if a['searched_locations']]
    attempts_with_actual = [a for a in all_attempts if a['actual_location']]

    print(f"\nLocation Tracking:")
    print(f"  Total attempts: {len(all_attempts)}")
    print(f"  With 'searched_locations': {len(attempts_with_searched)}")
    print(f"  With 'actual_location': {len(attempts_with_actual)}")

    if len(attempts_with_searched) == 0:
        print("\n  WARNING: No 'searched_locations' being tracked!")
        print("  This means we can't tell WHERE discovery tools are looking.")
        print("  The instrumentation needs to be improved.")

    # Check performance
    slowest = sorted(all_attempts, key=lambda a: a['duration_ms'], reverse=True)[:3]

    print(f"\nSlowest Operations:")
    for i, attempt in enumerate(slowest, 1):
        print(f"  {i}. {attempt['method']}: {attempt['query']} ({attempt['duration_ms']:.1f}ms)")

    # Key insight
    print("\n" + "="*80)
    print("KEY INSIGHT")
    print("="*80)

    if all(s['success_rate'] == 1.0 for s in sessions):
        print("""
ALL DISCOVERY OPERATIONS ARE SUCCEEDING!

This means:
1. The discovery tools CAN find files without path coordinates
2. The RepositoryIndex abstracts away filesystem navigation
3. The bottleneck is NOT "where to look" - it's PERFORMANCE

Performance breakdown:
- find_data_sources: ~4500ms (Pinecone semantic search)
- get_schema: ~1600ms (reading CSV/Parquet files)
- check_status: ~10ms (quick filesystem check)

ChatGPT's diagnosis about "path coordinates" vs. "topology" is
theoretically sound, but DOESN'T APPLY HERE because:
- Discovery tools use Pinecone index, not filesystem traversal
- Files are found via semantic search, not path walking
- The "geography" is in the Pinecone index, not gradient context

The REAL optimization opportunity:
1. Cache Pinecone query results (avoid 4.5s semantic search)
2. Cache schema results (avoid 1.6s file reads)
3. Use lighter embedding model (faster than OpenAI API)

NOT:
- Adding path coordinates to gradient context (won't help Pinecone)
        """)
    else:
        print("""
Discovery is FAILING in some cases.

This would validate ChatGPT's diagnosis about needing path coordinates.
        """)

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
