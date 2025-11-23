"""
Test that pprint.pformat fix produces Python syntax (True/False) not JSON (true/false)
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from src.agents.hybrid_code_generator import HybridCodeGenerator
from src.utils.context_extractor import PipelineContextExtractor

def test_json_syntax_fix():
    """Test that generated code uses Python syntax (True/False/None)"""
    print("\n" + "="*80)
    print("TEST: JSON Syntax Fix Verification")
    print("="*80)

    # Extract context
    print("\n1. Extracting pipeline context...")
    extractor = PipelineContextExtractor()
    context = extractor.extract_from_metadata()
    print(f"   [OK] Context extracted: {len(context.get('data_sources', {}))} sources")

    # Create generator
    print("\n2. Creating HybridCodeGenerator...")
    generator = HybridCodeGenerator()

    # Generate code (should hit snippet path)
    print("\n3. Generating dashboard code...")
    requirements = {
        'screen_type': 'pipeline_dashboard_navigation',
        'intent': 'Browse pipeline data sources and datasets'
    }

    code = generator.generate(requirements, context)

    print(f"\n4. Analyzing generated code...")
    print(f"   Code length: {len(code):,} chars")

    # Check for JSON syntax (BAD)
    has_json_true = ' true' in code or 'true,' in code or 'true}' in code or '[true' in code
    has_json_false = ' false' in code or 'false,' in code or 'false}' in code or '[false' in code
    has_json_null = ' null' in code or 'null,' in code or 'null}' in code or '[null' in code

    # Check for Python syntax (GOOD)
    has_python_true = ' True' in code or 'True,' in code or 'True}' in code or '[True' in code
    has_python_false = ' False' in code or 'False,' in code or 'False}' in code or '[False' in code
    has_python_none = ' None' in code or 'None,' in code or 'None}' in code or '[None' in code

    print(f"\n5. Syntax Analysis:")
    print(f"   JSON syntax (BAD):")
    print(f"     - 'true' found: {has_json_true}")
    print(f"     - 'false' found: {has_json_false}")
    print(f"     - 'null' found: {has_json_null}")
    print(f"   Python syntax (GOOD):")
    print(f"     - 'True' found: {has_python_true}")
    print(f"     - 'False' found: {has_python_false}")
    print(f"     - 'None' found: {has_python_none}")

    # Show sample of PIPELINE_DATA assignment
    if 'PIPELINE_DATA = ' in code:
        start_idx = code.index('PIPELINE_DATA = ')
        sample = code[start_idx:start_idx + 500]
        print(f"\n6. Sample of PIPELINE_DATA assignment:")
        print(f"   {sample}...")

    # Verdict
    print(f"\n7. Verdict:")
    if has_json_true or has_json_false or has_json_null:
        print("   [FAIL] Code still contains JSON syntax (true/false/null)")
        print("   This will cause NameError when code executes!")
        return False
    elif has_python_true or has_python_false or has_python_none:
        print("   [OK] Code uses Python syntax (True/False/None)")
        print("   Fix successful!")
        return True
    else:
        print("   [INFO] No boolean/null values found in generated code")
        print("   (This might be fine if data doesn't contain these values)")
        return True

if __name__ == "__main__":
    try:
        success = test_json_syntax_fix()
        if success:
            print("\n" + "="*80)
            print("[OK] JSON SYNTAX FIX VERIFIED!")
            print("="*80)
            sys.exit(0)
        else:
            print("\n" + "="*80)
            print("[FAIL] JSON SYNTAX STILL PRESENT!")
            print("="*80)
            sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)