# Phase 3A: Next Steps for Completion

**Status**: Backend complete, need to integrate with React Developer

## Files Already Created

1. ✅ **Backend API**: [src/api/data_service.py](src/api/data_service.py)
2. ✅ **React Hooks**: [src/templates/data_hooks.tsx](src/templates/data_hooks.tsx)
3. ✅ **API Test**: [test_phase3a_api.py](test_phase3a_api.py)

## What's Left (< 1 hour of work)

### Step 1: Add Method to React Developer (20 min)

**File**: [src/agents/react_developer.py](src/agents/react_developer.py)

Add this method after `__init__`:

```python
def _load_data_hooks_template(self) -> str:
    """Load the data hooks template from templates directory"""
    template_path = Path(__file__).parent.parent / "templates" / "data_hooks.tsx"
    if template_path.exists():
        return template_path.read_text()
    return ""  # Fallback if template not found
```

### Step 2: Update `_parse_generated_files()` (15 min)

**File**: [src/agents/react_developer.py](src/agents/react_developer.py)
**Method**: `_parse_generated_files()` (around line 450)

After parsing all files from Claude's response, add:

```python
# Phase 3A: Always include data hooks for real data fetching
data_hooks_content = self._load_data_hooks_template()
if data_hooks_content:
    files['dataHooks.tsx'] = data_hooks_content
    print(f"  [React Developer] Added dataHooks.tsx ({len(data_hooks_content)} chars)")
```

###Step 3: Update `_create_react_prompt()` (15 min)

**File**: [src/agents/react_developer.py](src/agents/react_developer.py)
**Method**: `_create_react_prompt()` (around line 280-320)

Add this section BEFORE "TECHNICAL REQUIREMENTS":

```python
PHASE 3A - REAL DATA FETCHING (CRITICAL):

The application MUST fetch real data from the backend API at http://localhost:8000

You have access to data-fetching hooks in dataHooks.tsx (already provided):
- useDataSources() → List all sources
- useDataSourceInfo(source) → Get metadata (row count, columns, schema)
- useDataSource(source, options) → Fetch data with pagination
- useDataQuery(request) → Advanced queries with filters

CRITICAL RULES FOR DATA FETCHING:
1. NEVER hardcode data like `const data = [...]` or `const mockData = [...]`
2. ALWAYS use hooks: `const {{{{ data, loading, error }}}} = useDataSource('fracfocus')`
3. ALWAYS handle loading: `if (loading) return <div>Loading...</div>`
4. ALWAYS handle errors: `if (error) return <div>Error: {{{{error}}}}</div>`
5. Use EXACT source names from DATA SOURCES section above
6. Import hooks: `import {{{{ useDataSource }}}} from './dataHooks'`

Example of CORRECT data fetching:
```tsx
import {{{{ useDataSource }}}} from './dataHooks';

export default function Dashboard() {{{{
  const {{{{ data, total, loading, error }}}} = useDataSource('fracfocus', {{{{
    limit: 100
  }}}});

  if (loading) return <div className="p-4">Loading data...</div>;
  if (error) return <div className="p-4 text-red-500">Error: {{{{error}}}}</div>;

  return (
    <div>
      <h1>FracFocus Data ({{{{total.toLocaleString()}}}} total records)</h1>
      {{{{data.map((row, i) => (
        <div key={{{{i}}}}>{{{{/* Display row data */}}}}</div>
      ))}}}}
    </div>
  );
}}}}
```

Example of WRONG (hardcoded) approach - DO NOT DO THIS:
```tsx
// ❌ WRONG - Don't hardcode data!
const data = [
  {{{{ source: 'fracfocus', records: 239059 }}}}
];
```
```

Note: The `{{{{` and `}}}}` are escaped braces for the f-string.

### Step 4: Test End-to-End (10 min)

1. Start backend API:
```bash
python -m uvicorn src.api.data_service:app --port 8000 --reload
```

2. Generate dashboard in Agent Studio:
```
"Create a dashboard showing fracfocus chemical data with charts"
```

3. Verify generated code:
   - Has `dataHooks.tsx` file
   - App.tsx imports `useDataSource`
   - No hardcoded data arrays
   - Has loading/error handling

4. Run dashboard:
```bash
cd generated_react_dashboard
npm install
npm run dev
```

5. Check browser shows REAL data (239,059 records)

## Quick Reference

**Files to Modify**:
- [src/agents/react_developer.py](src/agents/react_developer.py)
  - Line ~70: Add `_load_data_hooks_template()` method
  - Line ~450: Update `_parse_generated_files()` to include dataHooks.tsx
  - Line ~310: Update `_create_react_prompt()` with Phase 3A instructions

**Test Command**:
```bash
# Terminal 1: Backend
python -m uvicorn src.api.data_service:app --port 8000 --reload

# Terminal 2: Generate and test dashboard
# Use Agent Studio to create dashboard
```

## Expected Outcome

**Before Phase 3A**:
```tsx
const data = [{ source: 'fracfocus', records: 239059 }];  // Useless
```

**After Phase 3A**:
```tsx
const { data, loading } = useDataSource('fracfocus');  // Works!
// Displays real 239K rows from backend API
```

---

**Total Time**: ~1 hour
**Complexity**: Low (just integrating existing pieces)
**Impact**: HIGH - Transforms generated dashboards from demos to working applications
