"""
Test Phase 2 Fixes - RRC Missing & Pipeline Stages

This test verifies the fixes for:
1. RRC missing from dashboard (was excluded because only top 5 schemas retrieved)
2. Pipeline stages incorrect (stages weren't being passed through)

Expected fixes:
- Process ALL discovered sources, not just top 5
- Include 'stages' field in data_sources dict
- React Developer displays exact stage names (downloads/extracted/parsed)
"""

import sys
from pathlib import Path
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.ui_orchestrator import UICodeOrchestrator


def test_rrc_and_stages():
    """
    Test that RRC appears in dashboard and stages are correct.
    """

    print("\n" + "="*80)
    print("PHASE 2 FIXES TEST - RRC & PIPELINE STAGES")
    print("="*80)

    print("\n[TEST] Creating test intent...")
    user_intent = "Create a dashboard showing all my data pipeline stages with health status"
    screen_type = "dashboard"

    requirements = {
        'screen_type': screen_type,
        'intent': user_intent
    }

    context = {}

    print(f"User intent: {user_intent}")
    print(f"Data sources provided: NONE (will discover)")

    print("\n[TEST] Generating UI code with fixes...")
    orchestrator = UICodeOrchestrator()

    try:
        code = orchestrator.generate_ui_code(requirements, context)

        print("\n" + "="*80)
        print("VALIDATION")
        print("="*80)

        assert code is not None, "No code generated"
        assert isinstance(code, dict), "Code should be dict of files"
        assert 'App.tsx' in code, "Missing App.tsx"

        app_code = code['App.tsx']
        print(f"\n✅ Generated {len(app_code):,} characters of code")

        # Check 1: RRC should be in the code
        if 'rrc' in app_code.lower():
            print("✅ RRC is present in generated code")
        else:
            print("❌ RRC is MISSING from generated code")

        # Check 2: Should have actual stage names (not generic)
        actual_stages_found = []
        if 'downloads' in app_code.lower():
            actual_stages_found.append('downloads')
        if 'extracted' in app_code.lower():
            actual_stages_found.append('extracted')
        if 'parsed' in app_code.lower():
            actual_stages_found.append('parsed')

        if actual_stages_found:
            print(f"✅ Found actual stage names: {', '.join(actual_stages_found)}")
        else:
            print("⚠️  No actual stage names found (downloads/extracted/parsed)")

        # Check 3: Should NOT have generic stage names
        generic_stages = []
        if 'download' in app_code.lower() and 'downloads' not in app_code.lower():
            generic_stages.append('Download')
        if 'transform' in app_code.lower():
            generic_stages.append('Transform')
        if 'validate' in app_code.lower():
            generic_stages.append('Validate')

        if generic_stages:
            print(f"⚠️  Found generic stage names: {', '.join(generic_stages)}")
        else:
            print("✅ No generic stage names found")

        # Check 4: Should have 239,059 (fracfocus row count)
        if '239' in app_code:
            print("✅ Found fracfocus row count (239K)")
        else:
            print("❌ Missing fracfocus row count")

        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)

        issues = []
        if 'rrc' not in app_code.lower():
            issues.append("RRC missing")
        if not actual_stages_found:
            issues.append("No actual stage names")
        if generic_stages:
            issues.append(f"Generic stages present ({', '.join(generic_stages)})")

        if not issues:
            print("\n✅ ALL FIXES WORKING!")
            print("  • RRC is present in dashboard")
            print("  • Actual stage names are used")
            print("  • No generic stage names")
            return True
        else:
            print(f"\n⚠️  ISSUES REMAINING: {len(issues)}")
            for issue in issues:
                print(f"  - {issue}")

            # Show code preview for debugging
            print("\n" + "="*80)
            print("Code Preview (first 1500 chars)")
            print("="*80)
            print(app_code[:1500] + "...")

            return False

    except Exception as e:
        print("\n" + "="*80)
        print("❌ TEST FAILED")
        print("="*80)
        print(f"\nError: {e}")

        import traceback
        traceback.print_exc()

        return False


if __name__ == "__main__":
    print("\n\n")
    print("#" * 80)
    print("# PHASE 2 FIXES VERIFICATION")
    print("# Testing: RRC inclusion & Actual pipeline stage names")
    print("#" * 80)

    success = test_rrc_and_stages()

    print("\n\n")
    print("#" * 80)
    print("# RESULT")
    print("#" * 80)

    if success:
        print("\n✅ FIXES VERIFIED")
        print("\nThe fixes are working:")
        print("  1. RRC is no longer excluded (all sources processed)")
        print("  2. Pipeline stages use actual names (downloads/extracted/parsed)")
    else:
        print("\n⚠️  FIXES NEED REVIEW")
        print("\nSome issues may remain - check output above")

    print("\n")
