"""
Test that generated_ui.py launches without errors
"""
import sys
import importlib.util

def test_generated_ui():
    print("=" * 80)
    print("TEST: Generated UI Launch Verification")
    print("=" * 80)

    try:
        # Load the generated_ui module
        spec = importlib.util.spec_from_file_location("generated_ui", "generated_ui.py")
        module = importlib.util.module_from_spec(spec)

        print("\n[1/4] Loading generated_ui.py module...")
        spec.loader.exec_module(module)
        print("PASS: Module loaded successfully")

        print("\n[2/4] Checking create_dashboard function exists...")
        assert hasattr(module, 'create_dashboard'), "Missing create_dashboard function"
        print("PASS: create_dashboard function found")

        print("\n[3/4] Checking PIPELINE_DATA structure...")
        assert hasattr(module, 'PIPELINE_DATA'), "Missing PIPELINE_DATA"
        assert isinstance(module.PIPELINE_DATA, dict), "PIPELINE_DATA should be a dict"
        assert 'sources' in module.PIPELINE_DATA, "PIPELINE_DATA missing 'sources' key"
        print(f"PASS: PIPELINE_DATA valid with {len(module.PIPELINE_DATA['sources'])} sources")

        print("\n[4/4] Creating dashboard instance...")
        demo = module.create_dashboard()
        print("PASS: Dashboard created successfully")

        print("\n" + "=" * 80)
        print("ALL TESTS PASSED!")
        print("=" * 80)
        print("\nThe generated UI is ready to launch.")
        print("To launch: python generated_ui.py")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\nFAIL: Error during testing")
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_generated_ui()
    sys.exit(0 if success else 1)
