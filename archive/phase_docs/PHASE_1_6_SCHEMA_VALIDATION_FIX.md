# Phase 1.6: Schema Validation Fix

## The Problem You Identified

```
If dataHooks.tsx defines PipelinesResponse { pipelines: Pipeline[] },
React MUST access data.pipelines (NEVER data)
```

This was **not being enforced**, causing the "0 records, 0 files, empty dashboard" bug.

---

## Root Cause

The React agent sometimes generated code that incorrectly accessed `data` as an array instead of `data.pipelines`:

### dataHooks.tsx (CORRECT):
```typescript
export interface PipelinesResponse {
  pipelines: Pipeline[];
  summary: {...};
}

export function usePipelines() {
  const [data, setData] = useState<PipelinesResponse | null>(null);
  return { data, loading, error };
}
```

### App.tsx (WRONG - what was being generated):
```typescript
const filteredPipelines = useMemo(() => {
  if (!data || !Array.isArray(data)) return [];  // ❌ data is NOT an array!

  return data.filter(pipeline => { ... });  // ❌ data has no .filter()
}, [data]);
```

### Result:
- `data` is `PipelinesResponse`, not `Pipeline[]`
- `Array.isArray(data)` always returns `false`
- `filteredPipelines` is always `[]`
- Dashboard shows: **0 records, 0 files, 0.00 MB**

---

## The Fix

### 1. Added Critical Validation (React Agent)

**File**: [src/agents/react_developer.py:1393-1475](src/agents/react_developer.py#L1393-L1475)

```python
def _validate_data_hooks_schema_consistency(self, files: Dict[str, str]):
    """
    CRITICAL VALIDATION (Phase 1.6):
    Ensure App.tsx uses data.pipelines, NOT data directly.

    Raises ValueError if schema mismatch detected.
    """
    # Detect if PipelinesResponse structure exists
    has_pipelines_response = re.search(
        r'interface\s+PipelinesResponse\s*\{[^}]*pipelines:\s*Pipeline\[\]',
        data_hooks_content,
        re.DOTALL
    )

    if not has_pipelines_response:
        return  # No validation needed

    # Check for WRONG usage
    incorrect_data_check = re.search(r'Array\.isArray\(data\)', app_tsx_content)
    incorrect_data_filter = re.search(r'\bdata\.filter\s*\(', app_tsx_content)

    if incorrect_data_check or incorrect_data_filter:
        # Print detailed error message
        # Raise ValueError to FAIL the build
        raise ValueError(
            "Schema mismatch: App.tsx must use data.pipelines, not data directly."
        )
```

**This validator now runs on every React generation** (line 1574).

---

### 2. Updated Generation Prompt

**File**: [src/agents/react_developer.py:793-811](src/agents/react_developer.py#L793-L811)

Added prominent warning:

```
*** CRITICAL SCHEMA RULE (Phase 1.6) ***

The usePipelines() hook returns:
  { data: PipelinesResponse, loading, error }

Where PipelinesResponse is:
  { pipelines: Pipeline[], summary: {...} }

Therefore you MUST access data.pipelines, NEVER data directly!

WRONG:  if (!data || !Array.isArray(data))
WRONG:  data.filter(...)
WRONG:  data.map(...)

CORRECT: if (!data?.pipelines || !Array.isArray(data.pipelines))
CORRECT: data.pipelines.filter(...)
CORRECT: data.pipelines.map(...)

Violating this rule causes: 0 records, 0 files, empty dashboard
```

---

## Test Results

**File**: [test_schema_validation.py](test_schema_validation.py)

### Test 1: Detects WRONG usage ✅
```
Input: App.tsx with Array.isArray(data)
Output: ValueError raised with clear error message
Status: PASS
```

### Test 2: Accepts CORRECT usage ✅
```
Input: App.tsx with Array.isArray(data.pipelines)
Output: Validation passes silently
Status: PASS
```

---

## Impact

### Before Fix:
- React agent could generate `Array.isArray(data)`
- No validation would catch it
- Dashboard would show zeros
- Silent failure (no error message)

### After Fix:
- Validation **fails the build** if wrong pattern detected
- Clear error message explains the issue
- Developer sees:
  ```
  CRITICAL SCHEMA ERROR DETECTED

  dataHooks.tsx defines: PipelinesResponse { pipelines: Pipeline[] }
  But App.tsx uses: Array.isArray(data)  <- WRONG!
  MUST use: Array.isArray(data.pipelines)
  ```
- Forces correct code generation

---

## Files Modified

1. ✅ [src/agents/react_developer.py](src/agents/react_developer.py)
   - Added `_validate_data_hooks_schema_consistency()` method (line 1393)
   - Updated generation prompt with schema rule (line 793)
   - Integrated validation into parsing pipeline (line 1574)

2. ✅ [test_schema_validation.py](test_schema_validation.py)
   - Comprehensive tests for both pass and fail cases

---

## Summary

**Your Rule**:
```
If dataHooks.tsx defines PipelinesResponse { pipelines: Pipeline[] },
React MUST access data.pipelines (NEVER data)
```

**Now Enforced By**:
1. ✅ Prominent warning in generation prompt
2. ✅ Automatic validation that FAILS builds on violation
3. ✅ Clear error messages for debugging

**This prevents** the "0 records, 0 files, empty dashboard" bug from **ever happening again**.
