"""
Test the canonical schema field validator that prevents hallucinated fields.

This validator catches bugs like:
- pipeline.metrics.total_records (should be record_count)
- pipeline.total_files (should be metrics.file_count)
- pipeline.children (doesn't exist)
"""

from src.agents.react_developer import ReactDeveloperAgent


def test_detects_total_records_hallucination():
    """Test that validator catches metrics.total_records"""
    agent = ReactDeveloperAgent(styling_framework="tailwind")

    files_with_error = {
        'App.tsx': '''
export default function App() {
  const { data, loading, error } = usePipelines();

  const totalRecords = filteredPipelines.reduce(
    (sum, p) => sum + (p.metrics?.total_records || 0),  // WRONG!
    0
  );

  return <div>{totalRecords} records</div>;
}
'''
    }

    print("\n" + "="*70)
    print("TEST: Hallucinated Field - metrics.total_records")
    print("="*70)
    print("\nTesting with WRONG field: pipeline.metrics.total_records")
    print("Expected: Should FAIL validation\n")

    try:
        agent._validate_canonical_schema_fields(files_with_error)
        print("FAIL: Validator did not catch hallucinated field!")
        return False
    except ValueError as e:
        print("PASS: Validator correctly detected hallucinated field")
        print(f"   Error: {str(e)[:80]}...")
        return True


def test_detects_multiple_hallucinations():
    """Test that validator catches multiple hallucinated fields"""
    agent = ReactDeveloperAgent(styling_framework="tailwind")

    files_with_errors = {
        'App.tsx': '''
export default function App() {
  const { data, loading, error } = usePipelines();

  // Multiple hallucinations
  const totalFiles = pipeline.total_files;  // WRONG!
  const totalRecords = pipeline.total_records;  // WRONG!
  const children = pipeline.children;  // WRONG!

  return <div>Dashboard</div>;
}
'''
    }

    print("\n" + "="*70)
    print("TEST: Multiple Hallucinated Fields")
    print("="*70)
    print("\nTesting with multiple WRONG fields")
    print("Expected: Should FAIL validation\n")

    try:
        agent._validate_canonical_schema_fields(files_with_errors)
        print("FAIL: Validator did not catch hallucinated fields!")
        return False
    except ValueError as e:
        print("PASS: Validator correctly detected multiple hallucinations")
        print(f"   Error: {str(e)[:80]}...")
        return True


def test_accepts_correct_fields():
    """Test that validator passes with correct canonical fields"""
    agent = ReactDeveloperAgent(styling_framework="tailwind")

    files_correct = {
        'App.tsx': '''
export default function App() {
  const { data, loading, error } = usePipelines();

  // Correct canonical fields
  const totalRecords = filteredPipelines.reduce(
    (sum, p) => sum + (p.metrics?.record_count || 0),  // CORRECT!
    0
  );

  const totalFiles = filteredPipelines.reduce(
    (sum, p) => sum + (p.metrics?.file_count || 0),  // CORRECT!
    0
  );

  return <div>{totalRecords} records, {totalFiles} files</div>;
}
'''
    }

    print("\n" + "="*70)
    print("TEST: Correct Canonical Fields")
    print("="*70)
    print("\nTesting with CORRECT fields")
    print("Expected: Should PASS validation\n")

    try:
        agent._validate_canonical_schema_fields(files_correct)
        print("PASS: Validator accepted correct canonical fields")
        return True
    except ValueError as e:
        print(f"FAIL: Validator rejected correct fields: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "="*70)
    print("CANONICAL SCHEMA FIELD VALIDATOR TESTS")
    print("="*70)

    test1 = test_detects_total_records_hallucination()
    test2 = test_detects_multiple_hallucinations()
    test3 = test_accepts_correct_fields()

    print("\n" + "="*70)
    if test1 and test2 and test3:
        print("ALL TESTS PASSED")
        print("="*70)
        print("\nThe canonical schema validator will now:")
        print("  1. REJECT pipeline.metrics.total_records")
        print("  2. REJECT pipeline.total_files, pipeline.children, etc.")
        print("  3. ACCEPT pipeline.metrics.record_count (correct)")
        print("  4. ACCEPT pipeline.metrics.file_count (correct)")
        print("  5. Prevent '0 records' bugs from hallucinated fields")
    else:
        print("SOME TESTS FAILED")
        print("="*70)

    print("\n")
