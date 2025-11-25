"""
Test Pattern Matching Fix - Verify Hierarchical Patterns Are Selected

This script tests that the specificity-based pattern matching correctly
selects hierarchical patterns over simple patterns when appropriate.
"""

from src.templates.gradio_snippets import SnippetAssembler


def test_pattern_matching():
    assembler = SnippetAssembler()

    print("=" * 80)
    print("PATTERN MATCHING FIX TEST")
    print("=" * 80)
    print()

    # Test Case 1: Hierarchical navigation (should select hierarchical pattern)
    print("Test Case 1: Hierarchical Data Navigation")
    print("-" * 80)
    requirements1 = {
        'screen_type': 'pipeline_dashboard',
        'intent': 'Create hierarchical navigation for multi-level data sources with datasets and stages'
    }
    pattern1 = assembler.match_pattern(requirements1)
    print(f"Requirements: {requirements1}")
    print(f"Expected: hierarchical_data_navigation_source_dataset_stage_files")
    print(f"Actual:   {pattern1}")
    if 'hierarchical' in pattern1:
        print("PASS: Hierarchical pattern selected")
    else:
        print("FAIL: Should have selected hierarchical pattern")
    print()

    # Test Case 2: Simple pipeline (should select simple pattern)
    print("Test Case 2: Simple Pipeline Navigation")
    print("-" * 80)
    requirements2 = {
        'screen_type': 'pipeline',
        'intent': 'Basic navigation between data sources'
    }
    pattern2 = assembler.match_pattern(requirements2)
    print(f"Requirements: {requirements2}")
    print(f"Expected: pipeline_navigation")
    print(f"Actual:   {pattern2}")
    if pattern2 == 'pipeline_navigation':
        print("PASS: Simple pipeline pattern selected")
    else:
        print("FAIL: Should have selected simple pipeline_navigation")
    print()

    # Test Case 3: Folder navigation (should select folder navigation pattern)
    print("Test Case 3: Folder Navigation")
    print("-" * 80)
    requirements3 = {
        'screen_type': 'file_browser',
        'intent': 'Folder navigation with breadcrumbs'
    }
    pattern3 = assembler.match_pattern(requirements3)
    print(f"Requirements: {requirements3}")
    print(f"Expected: Pattern with 'folder' or 'breadcrumb'")
    print(f"Actual:   {pattern3}")
    if 'folder' in pattern3.lower() or 'breadcrumb' in pattern3.lower():
        print("PASS: Folder/breadcrumb pattern selected")
    else:
        print("FAIL: Should have selected folder/breadcrumb pattern")
    print()

    # Test Case 4: Verify hierarchical pattern is in PATTERNS dict
    print("Test Case 4: Hierarchical Patterns Available")
    print("-" * 80)
    hierarchical_patterns = [p for p in assembler.patterns.keys() if 'hierarchical' in p.lower()]
    print(f"Hierarchical patterns in library: {hierarchical_patterns}")
    if len(hierarchical_patterns) >= 2:
        print("PASS: Hierarchical patterns are available in PATTERNS")
    else:
        print("FAIL: Hierarchical patterns missing from PATTERNS")
    print()

    # Test Case 5: Show all available patterns
    print("Test Case 5: All Available Patterns")
    print("-" * 80)
    all_patterns = list(assembler.patterns.keys())
    print(f"Total patterns available: {len(all_patterns)}")
    for i, pattern in enumerate(all_patterns, 1):
        print(f"  {i}. {pattern}")
    print()

    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_pattern_matching()
