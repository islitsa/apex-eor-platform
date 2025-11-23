"""
Test the Phase 1.6 schema validation that prevents data/data.pipelines mismatch
"""

from src.agents.react_developer import ReactDeveloperAgent


def test_schema_validation_catches_error():
    """
    Verify that the validator detects when App.tsx incorrectly uses data instead of data.pipelines
    """
    agent = ReactDeveloperAgent(styling_framework="tailwind")

    # Create mock files with the WRONG schema usage
    files_with_error = {
        'dataHooks.tsx': '''
export interface PipelinesResponse {
  pipelines: Pipeline[];
  summary: {...};
}

export function usePipelines() {
  const [data, setData] = useState<PipelinesResponse | null>(null);
  return { data, loading, error };
}
''',
        'App.tsx': '''
export default function App() {
  const { data, loading, error } = usePipelines();

  const filteredPipelines = useMemo(() => {
    if (!data || !Array.isArray(data)) return [];  // WRONG!

    return data.filter(pipeline => {  // WRONG!
      return pipeline.id === 'rrc';
    });
  }, [data]);

  return <div>{filteredPipelines.length} pipelines</div>;
}
'''
    }

    print("\n" + "="*70)
    print("TEST: Schema Validation (Phase 1.6)")
    print("="*70)
    print("\nTesting with INCORRECT schema usage...")
    print("  App.tsx uses: Array.isArray(data) and data.filter()")
    print("  Expected: Should FAIL validation\n")

    try:
        agent._validate_data_hooks_schema_consistency(files_with_error)
        print("FAIL: Validator did not catch the error!")
        return False
    except ValueError as e:
        print("PASS: Validator correctly detected schema mismatch")
        print(f"   Error: {str(e)[:80]}...")
        return True


def test_schema_validation_passes_correct_code():
    """
    Verify that the validator passes when App.tsx correctly uses data.pipelines
    """
    agent = ReactDeveloperAgent(styling_framework="tailwind")

    # Create mock files with the CORRECT schema usage
    files_correct = {
        'dataHooks.tsx': '''
export interface PipelinesResponse {
  pipelines: Pipeline[];
  summary: {...};
}

export function usePipelines() {
  const [data, setData] = useState<PipelinesResponse | null>(null);
  return { data, loading, error };
}
''',
        'App.tsx': '''
export default function App() {
  const { data, loading, error } = usePipelines();

  const filteredPipelines = useMemo(() => {
    if (!data?.pipelines || !Array.isArray(data.pipelines)) return [];  // CORRECT

    return data.pipelines.filter(pipeline => {  // CORRECT
      return pipeline.id === 'rrc';
    });
  }, [data]);

  return <div>{filteredPipelines.length} pipelines</div>;
}
'''
    }

    print("\n" + "="*70)
    print("TEST: Schema Validation with Correct Code")
    print("="*70)
    print("\nTesting with CORRECT schema usage...")
    print("  App.tsx uses: Array.isArray(data.pipelines) and data.pipelines.filter()")
    print("  Expected: Should PASS validation\n")

    try:
        agent._validate_data_hooks_schema_consistency(files_correct)
        print("PASS: Validator accepted correct code")
        return True
    except ValueError as e:
        print(f"FAIL: Validator rejected correct code: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "="*70)
    print("PHASE 1.6: DATA HOOKS SCHEMA VALIDATION TESTS")
    print("="*70)

    test1 = test_schema_validation_catches_error()
    test2 = test_schema_validation_passes_correct_code()

    print("\n" + "="*70)
    if test1 and test2:
        print("ALL TESTS PASSED")
        print("="*70)
        print("\nThe schema validator will now:")
        print("  1. FAIL generation if App.tsx uses data instead of data.pipelines")
        print("  2. PASS generation if App.tsx correctly uses data.pipelines")
        print("  3. Prevent the '0 records, 0 files' bug from ever happening again")
    else:
        print("SOME TESTS FAILED")
        print("="*70)

    print("\n")
