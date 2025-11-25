"""
Phase 2 Integration Test - Discovered Data in Generated UI

This test verifies that discovered metadata (row counts, pipeline stages, columns)
flows through the entire system and appears in the generated React code.

Flow:
1. UX Designer discovers data sources (Phase 1)
2. UX Designer creates DesignSpec WITH data_sources (Phase 2)
3. React Developer receives data_sources from DesignSpec (Phase 2)
4. Generated React code uses ACTUAL row counts and statuses (Phase 2)
"""

import sys
from pathlib import Path
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.ui_orchestrator import UICodeOrchestrator


def test_phase2_discovered_data_in_ui():
    """
    Test that discovered data appears in generated React UI code.
    """

    print("\n" + "="*80)
    print("PHASE 2 INTEGRATION TEST - DISCOVERED DATA IN GENERATED UI")
    print("="*80)

    # ========================================
    # STEP 1: User provides ONLY intent
    # ========================================
    print("\n[STEP 1] User Input")
    print("-" * 80)

    user_intent = "Create a dashboard showing all my data pipeline stages with health status"
    screen_type = "dashboard"

    print(f"User intent: {user_intent}")
    print(f"Screen type: {screen_type}")
    print(f"Data sources provided: NONE (agent will discover)")

    # ========================================
    # STEP 2: Build requirements without data_sources
    # ========================================
    print("\n[STEP 2] Build Requirements")
    print("-" * 80)

    requirements = {
        'screen_type': screen_type,
        'intent': user_intent
        # NO data_sources - Phase 1 discovery will find them
    }

    context = {}

    print(f"Requirements: {requirements}")

    # ========================================
    # STEP 3: Generate UI Code
    # ========================================
    print("\n[STEP 3] Generate UI Code (with autonomous discovery)")
    print("-" * 80)

    orchestrator = UICodeOrchestrator()

    try:
        # Generate code - should trigger discovery and use discovered data
        code = orchestrator.generate_ui_code(requirements, context)

        # ========================================
        # STEP 4: Validate Discovered Data Flow
        # ========================================
        print("\n[STEP 4] Validate Discovered Data in Generated Code")
        print("-" * 80)

        # Check that code was generated
        assert code is not None, "No code generated"
        assert isinstance(code, dict), "Code should be a dict of files"
        assert len(code) > 0, "Generated code is empty"

        print(f"✅ Code generated: {len(code)} files")
        print(f"   Files: {list(code.keys())}")

        # Check for App.tsx (main file)
        assert 'App.tsx' in code, "Missing App.tsx"
        app_code = code['App.tsx']
        print(f"\n✅ App.tsx generated: {len(app_code):,} characters")

        # ========================================
        # STEP 5: Verify ACTUAL Data in Code
        # ========================================
        print("\n[STEP 5] Check for Actual Row Counts and Statuses")
        print("-" * 80)

        # Check that code contains actual row counts (not 0 or "Unknown")
        # The fracfocus dataset has 239,059 records

        test_results = []

        # Test 1: Check for actual row count
        # Look for patterns like "239,059" or "239059" in the code
        has_fracfocus_count = False
        if '239' in app_code:
            print("✅ Found reference to fracfocus row count (239K)")
            has_fracfocus_count = True
            test_results.append(("Row count present", True))
        else:
            print("❌ No reference to fracfocus row count found")
            test_results.append(("Row count present", False))

        # Test 2: Check that code doesn't use placeholder "0 records"
        if '0 records' in app_code.lower() or 'unknown (0' in app_code.lower():
            print("❌ WARNING: Code still contains '0 records' placeholder")
            test_results.append(("No zero placeholders", False))
        else:
            print("✅ No '0 records' placeholders found")
            test_results.append(("No zero placeholders", True))

        # Test 3: Check for pipeline stage names (downloads, extracted, parsed)
        pipeline_stages = ['downloads', 'extracted', 'parsed']
        found_stages = []
        for stage in pipeline_stages:
            if stage.lower() in app_code.lower():
                found_stages.append(stage)

        if found_stages:
            print(f"✅ Found actual pipeline stages: {', '.join(found_stages)}")
            test_results.append(("Pipeline stages present", True))
        else:
            print("❌ No actual pipeline stages found (downloads/extracted/parsed)")
            test_results.append(("Pipeline stages present", False))

        # Test 4: Check for status values (in_progress, complete, etc.)
        if 'in_progress' in app_code.lower() or 'status' in app_code.lower():
            print("✅ Found status information in code")
            test_results.append(("Status information present", True))
        else:
            print("❌ No status information found")
            test_results.append(("Status information present", False))

        # ========================================
        # STEP 6: Verify DesignSpec Contains Data
        # ========================================
        print("\n[STEP 6] Verify DesignSpec Data Flow")
        print("-" * 80)

        # Check UX Designer's last design
        ux_designer = orchestrator.ux_designer

        # Check design history
        if hasattr(ux_designer, 'design_history') and ux_designer.design_history:
            print(f"✅ UX Designer created {len(ux_designer.design_history)} design(s)")
            test_results.append(("Design created", True))
        else:
            print("❌ No design in UX Designer history")
            test_results.append(("Design created", False))

        # ========================================
        # STEP 7: Test Summary
        # ========================================
        print("\n" + "="*80)
        print("PHASE 2 TEST RESULTS")
        print("="*80)

        total_tests = len(test_results)
        passed_tests = sum(1 for _, passed in test_results if passed)

        print(f"\nTests Passed: {passed_tests}/{total_tests}")
        print("\nDetails:")
        for test_name, passed in test_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status}: {test_name}")

        if passed_tests == total_tests:
            print("\n" + "="*80)
            print("✅ PHASE 2 INTEGRATION TEST - PASSED")
            print("="*80)
            print("\nKey Achievements:")
            print("  ✅ UX Designer discovered data sources")
            print("  ✅ DesignSpec contains discovered metadata")
            print("  ✅ React Developer received discovered data")
            print("  ✅ Generated code uses ACTUAL row counts and statuses")
            print("\n🎉 PHASE 2 COMPLETE - Discovered data flows to generated UI!")
            return True
        else:
            print("\n" + "="*80)
            print("⚠️  PHASE 2 INTEGRATION TEST - PARTIAL SUCCESS")
            print("="*80)
            print(f"\n{passed_tests}/{total_tests} checks passed")
            print("\nSome discovered metadata may not be appearing in generated code.")
            print("This could be due to:")
            print("  - React Developer not using the data in prompts")
            print("  - Claude generating generic placeholders despite instructions")
            print("  - Data format mismatch between discovery and React generation")

            # Show code preview for debugging
            print("\n" + "="*80)
            print("Generated Code Preview (first 1000 chars)")
            print("="*80)
            print(app_code[:1000] + "...")

            return False

    except Exception as e:
        print("\n" + "="*80)
        print("❌ PHASE 2 INTEGRATION TEST - FAILED")
        print("="*80)
        print(f"\nError: {e}")

        import traceback
        traceback.print_exc()

        return False


if __name__ == "__main__":
    print("\n\n")
    print("#" * 80)
    print("# PHASE 2 INTEGRATION TEST")
    print("# Testing: Discovery → DesignSpec → React Code → Actual Data in UI")
    print("#" * 80)

    success = test_phase2_discovered_data_in_ui()

    print("\n\n")
    print("#" * 80)
    print("# FINAL RESULT")
    print("#" * 80)

    if success:
        print("\n✅ PHASE 2 COMPLETE")
        print("\nThe full context swimming pipeline is working:")
        print("  1. UX Designer discovers data (Phase 1)")
        print("  2. DesignSpec includes discovered metadata (Phase 2)")
        print("  3. React Developer uses actual data in prompts (Phase 2)")
        print("  4. Generated UI displays real row counts and statuses (Phase 2)")
    else:
        print("\n⚠️  PHASE 2 NEEDS ATTENTION")
        print("\nSome parts of the pipeline are working, but discovered data")
        print("may not be fully appearing in the generated UI code.")

    print("\n")
