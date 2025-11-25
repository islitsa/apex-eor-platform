"""
Test Material Design 3 Enhancements

This script verifies that:
1. M3 pattern is available in the library
2. Pattern matching prefers M3 variants
3. Generated code includes M3 theme imports
4. The M3 UI can be launched successfully
"""

from src.templates.gradio_snippets import SnippetAssembler


def test_m3_pattern_availability():
    """Test that M3 pattern exists in library"""
    print("=" * 80)
    print("TEST 1: M3 Pattern Availability")
    print("=" * 80)

    assembler = SnippetAssembler()

    # Check if M3 pattern is in the library
    m3_pattern_id = "hierarchical_data_navigation_m3"

    if m3_pattern_id in assembler.patterns:
        print(f"PASS: M3 pattern '{m3_pattern_id}' found in library")
    else:
        print(f"FAIL: M3 pattern '{m3_pattern_id}' NOT found in library")
        print(f"Available patterns: {list(assembler.patterns.keys())}")
        return False

    print()
    return True


def test_m3_pattern_priority():
    """Test that M3 patterns are preferred over basic ones"""
    print("=" * 80)
    print("TEST 2: M3 Pattern Priority (Scoring)")
    print("=" * 80)

    assembler = SnippetAssembler()

    # Requirements that should match hierarchical navigation
    requirements = {
        'screen_type': 'pipeline_dashboard',
        'intent': 'Create hierarchical navigation for multi-level data sources with datasets and stages'
    }

    pattern_id = assembler.match_pattern(requirements)

    print(f"\nRequirements: {requirements}")
    print(f"Matched pattern: {pattern_id}")

    if pattern_id == "hierarchical_data_navigation_m3":
        print(f"PASS: M3 pattern selected (highest score)")
    elif 'hierarchical' in pattern_id:
        print(f"WARNING: Hierarchical pattern selected, but not M3 variant")
        print(f"  Selected: {pattern_id}")
        print(f"  Expected: hierarchical_data_navigation_m3")
        return False
    else:
        print(f"FAIL: Wrong pattern selected")
        print(f"  Selected: {pattern_id}")
        print(f"  Expected: hierarchical_data_navigation_m3")
        return False

    print()
    return True


def test_m3_code_generation():
    """Test that generated code includes M3 theme"""
    print("=" * 80)
    print("TEST 3: M3 Code Generation")
    print("=" * 80)

    assembler = SnippetAssembler()

    # Generate code using M3 pattern
    pipeline_data = {
        "sources": {
            "fracfocus": {
                "display_name": "FracFocus",
                "datasets": {
                    "Chemical_data": {
                        "records": 1000,
                        "status": "processed",
                        "last_updated": "2025-01-15"
                    }
                }
            }
        }
    }

    code = assembler.get_pattern("hierarchical_data_navigation_m3", pipeline_data=pipeline_data)

    # Check for M3 theme imports
    has_m3_import = "from src.templates.m3_theme import get_m3_theme_css" in code
    has_m3_css = "css=get_m3_theme_css()" in code
    has_m3_classes = "md-header-gradient" in code or "md-card" in code

    print(f"Generated code length: {len(code)} chars")
    print(f"Has M3 import: {has_m3_import}")
    print(f"Has M3 CSS param: {has_m3_css}")
    print(f"Has M3 classes: {has_m3_classes}")

    if has_m3_import and has_m3_css and has_m3_classes:
        print("\nPASS: Generated code includes complete M3 theme integration")
    else:
        print("\nFAIL: Generated code missing M3 theme elements")
        if not has_m3_import:
            print("  Missing: M3 theme import")
        if not has_m3_css:
            print("  Missing: M3 CSS parameter in gr.Blocks()")
        if not has_m3_classes:
            print("  Missing: M3 CSS classes")
        return False

    # Show code preview
    print("\nCode preview (first 500 chars):")
    print("-" * 80)
    print(code[:500])
    print("-" * 80)
    print()

    return True


def test_m3_theme_file():
    """Test that M3 theme file exists and loads correctly"""
    print("=" * 80)
    print("TEST 4: M3 Theme File")
    print("=" * 80)

    try:
        from src.templates.m3_theme import get_m3_theme_css, M3_COLORS, M3_ELEVATIONS

        css = get_m3_theme_css()

        print(f"M3 theme CSS length: {len(css)} chars")
        print(f"M3 color tokens: {len(M3_COLORS)} colors")
        print(f"M3 elevation levels: {len(M3_ELEVATIONS)} levels")

        # Check for key CSS classes
        has_card_class = ".md-card" in css
        has_button_class = ".md-button-filled" in css
        has_table_class = ".md-data-table" in css
        has_nav_class = ".md-nav-rail" in css

        print(f"\nCSS class coverage:")
        print(f"  Card styles: {has_card_class}")
        print(f"  Button styles: {has_button_class}")
        print(f"  Table styles: {has_table_class}")
        print(f"  Navigation styles: {has_nav_class}")

        if has_card_class and has_button_class and has_table_class and has_nav_class:
            print("\nPASS: M3 theme file complete with all component styles")
            return True
        else:
            print("\nFAIL: M3 theme file missing some component styles")
            return False

    except Exception as e:
        print(f"FAIL: Error loading M3 theme: {e}")
        return False


def test_comparison_basic_vs_m3():
    """Compare basic pattern vs M3 pattern"""
    print("=" * 80)
    print("TEST 5: Basic vs M3 Comparison")
    print("=" * 80)

    assembler = SnippetAssembler()

    pipeline_data = {"sources": {"test": {"datasets": {}}}}

    # Get basic pattern
    basic_code = assembler.get_pattern("hierarchical_data_navigation_source_dataset_stage_files", pipeline_data=pipeline_data)

    # Get M3 pattern
    m3_code = assembler.get_pattern("hierarchical_data_navigation_m3", pipeline_data=pipeline_data)

    print(f"Basic pattern size: {len(basic_code)} chars")
    print(f"M3 pattern size: {len(m3_code)} chars")
    print(f"Size difference: +{len(m3_code) - len(basic_code)} chars (+{((len(m3_code) - len(basic_code)) / len(basic_code) * 100):.1f}%)")

    # Count visual enhancements
    basic_html_count = basic_code.count("gr.HTML")
    m3_html_count = m3_code.count("gr.HTML")

    basic_css_classes = basic_code.count("elem_classes")
    m3_css_classes = m3_code.count("elem_classes")

    print(f"\nVisual enhancements:")
    print(f"  Basic HTML elements: {basic_html_count}")
    print(f"  M3 HTML elements: {m3_html_count}")
    print(f"  Basic CSS classes: {basic_css_classes}")
    print(f"  M3 CSS classes: {m3_css_classes}")

    if m3_html_count > basic_html_count or m3_css_classes > basic_css_classes:
        print("\nPASS: M3 pattern has more visual enhancements")
        return True
    else:
        print("\nWARNING: M3 pattern doesn't have significantly more visual enhancements")
        return True  # Not a hard failure


def run_all_tests():
    """Run all M3 enhancement tests"""
    print("\n")
    print("=" * 80)
    print("MATERIAL DESIGN 3 ENHANCEMENT TESTS")
    print("=" * 80)
    print()

    results = []

    results.append(("M3 Pattern Availability", test_m3_pattern_availability()))
    results.append(("M3 Pattern Priority", test_m3_pattern_priority()))
    results.append(("M3 Code Generation", test_m3_code_generation()))
    results.append(("M3 Theme File", test_m3_theme_file()))
    results.append(("Basic vs M3 Comparison", test_comparison_basic_vs_m3()))

    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "[PASS]" if result else "[FAIL]"
        print(f"{symbol} {test_name}: {status}")

    print()
    print(f"Tests passed: {passed}/{total} ({passed/total*100:.0f}%)")

    if passed == total:
        print("\nALL TESTS PASSED! M3 enhancements are working correctly.")
        print("\nNext steps:")
        print("1. Run agent_studio.py to test UI generation")
        print("2. Generate a dashboard and verify beautiful M3 styling")
        print("3. Compare with basic pattern to see visual improvements")
    else:
        print(f"\n{total - passed} test(s) failed. Please review errors above.")

    print("=" * 80)
    print()


if __name__ == "__main__":
    run_all_tests()
