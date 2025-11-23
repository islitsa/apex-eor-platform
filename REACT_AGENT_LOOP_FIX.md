# React Agent Loop Bug Fix

**Date:** 2025-11-22
**Issue:** React Agent stuck in infinite loop, regenerating files after already generating them

---

## Problem Summary

The React Agent was getting stuck in a loop where it would:
1. Generate 18 files successfully
2. Detect "Missing .tsx extensions in imports" issue
3. Plan next action: `generate_initial_implementation` (WRONG!)
4. Reasoning: "No React files have been generated yet" (FALSE!)
5. Loop back to step 1

The agent was regenerating everything instead of fixing the import errors.

---

## Root Cause Analysis

### Issue #1: Evaluation Results Not Persisted

**Location:** `src/agents/react_developer.py:1598-1650` (run method)

**Problem:**
```python
for step in range(max_steps):
    # 1. Plan
    plan = self._plan_next_action(shared_memory)

    # 2. Execute
    result = self._execute_skill(plan, shared_memory)

    # 3. Evaluate
    evaluation = self._evaluate_implementation(shared_memory)
    # ❌ evaluation results were NOT saved to shared_memory!

    # Next iteration: planner can't see what issues were found
```

**Impact:** Each planning cycle had no memory of what was evaluated in previous steps.

---

### Issue #2: Planning Prompt Lacked Evaluation Context

**Location:** `src/agents/react_developer.py:1652-1713` (_plan_next_action method)

**Problem:**
```python
prompt = f"""
CURRENT STATE:
- React Files Generated: {react_files_count}  # Only count!
- Implementation Conflicts: {conflicts_count}
- React Status: {shared_memory.react_status}
# ❌ No information about previous evaluation results
"""
```

**Impact:** The LLM couldn't see that the previous step detected issues, so it would default to regeneration.

---

### Issue #3: Incomplete Planning Guidance

**Location:** `src/agents/react_developer.py:1676-1679`

**Problem:**
```python
# Original guidance:
If no React files exist yet, use "generate_initial_implementation".
If conflicts detected, use "resolve_conflicts".
If type errors exist, use "fix_type_errors".
If implementation is complete, use "finish".
# ❌ No guidance for import errors!
```

**Impact:** When import errors were detected, the LLM didn't know which skill to use, so it fell back to regeneration.

---

### Issue #4: Wrong next_action for Import Errors

**Location:** `src/agents/react_developer.py:1945-1953` (_evaluate_implementation method)

**Problem:**
```python
if validation_issues:
    return ReactEvaluationResult(
        next_action="fix_type_errors" if "type" in str(validation_issues).lower() else "optimize_code",
        # ❌ For import errors, it suggested "optimize_code" which is wrong!
    )
```

**Impact:** The evaluation suggested the wrong skill, contributing to confusion.

---

## The Fix

### Fix #1: Persist Evaluation Results

**File:** `src/agents/react_developer.py:1631-1638`

```python
# BUGFIX: Save evaluation to shared_memory so next iteration can see it
shared_memory.react_evaluations.append({
    "step": step + 1,
    "satisfactory": evaluation.satisfactory,
    "issues": evaluation.issues,
    "next_action": evaluation.next_action,
    "reasoning": evaluation.reasoning
})
```

**Impact:** ✅ Planning cycles now have full context from previous evaluations.

---

### Fix #2: Include Evaluation Context in Planning

**File:** `src/agents/react_developer.py:1667-1677`

```python
# BUGFIX: Include previous evaluation results in planning context
previous_evaluation = ""
if shared_memory.react_evaluations:
    last_eval = shared_memory.react_evaluations[-1]
    previous_evaluation = f"""
PREVIOUS STEP EVALUATION:
- Satisfactory: {last_eval['satisfactory']}
- Issues Found: {', '.join(last_eval['issues']) if last_eval['issues'] else 'None'}
- Suggested Next Action: {last_eval['next_action']}
- Reasoning: {last_eval['reasoning']}
"""
```

**Impact:** ✅ LLM can now see what happened in previous step and make informed decisions.

---

### Fix #3: Better Planning Guidance

**File:** `src/agents/react_developer.py:1696-1702`

```python
DECISION LOGIC (in order of priority):
1. If React files count is 0, use "generate_initial_implementation"
2. If import errors exist (missing .tsx/.ts extensions), use "fix_import_errors"  # ✅ ADDED!
3. If type errors exist, use "fix_type_errors"
4. If conflicts detected, use "resolve_conflicts"
5. If previous evaluation suggested a next action, strongly consider using it  # ✅ ADDED!
6. If implementation is complete with no issues, use "finish"
```

**Impact:** ✅ LLM now knows exactly which skill to use for each issue type.

---

### Fix #4: Smart next_action Detection

**File:** `src/agents/react_developer.py:1972-1986`

```python
# BUGFIX: Properly determine next_action based on issue type
issues_str = str(validation_issues).lower()

if "import" in issues_str or "extension" in issues_str or ".tsx" in issues_str:
    next_action = "fix_import_errors"  # ✅ CORRECT!
    reasoning_prefix = "Import errors detected"
elif "type" in issues_str or "typescript" in issues_str:
    next_action = "fix_type_errors"
elif "mock" in issues_str or "placeholder" in issues_str:
    next_action = "regenerate_component"
else:
    next_action = "optimize_code"
```

**Impact:** ✅ Evaluation now suggests the correct next action for each issue type.

---

## Expected Behavior After Fix

### Before Fix (Broken):
```
[React Agent] Step 1/3
[React Agent] Planned: generate_initial_implementation
[React Agent] Executing: generate_initial_implementation
[React Developer] Generated 18 files
[React Agent] Evaluation: NEEDS WORK
[React Agent] Issues: Missing .tsx extensions in imports

[React Agent] Step 2/3
[React Agent] Planned: generate_initial_implementation  # ❌ WRONG!
[React Agent] Reasoning: No React files have been generated yet  # ❌ FALSE!
[React Agent] Executing: generate_initial_implementation
(Infinite loop...)
```

### After Fix (Correct):
```
[React Agent] Step 1/3
[React Agent] Planned: generate_initial_implementation
[React Agent] Executing: generate_initial_implementation
[React Developer] Generated 18 files
[React Agent] Evaluation: NEEDS WORK
[React Agent] Issues: Missing .tsx extensions in imports

[React Agent] Step 2/3
[React Agent] Planned: fix_import_errors  # ✅ CORRECT!
[React Agent] Reasoning: Previous evaluation detected import errors  # ✅ CORRECT!
[React Agent] Executing: fix_import_errors
[React Agent] Fixed 5 import statements  # ✅ PROGRESS!

[React Agent] Step 3/3
[React Agent] Planned: finish
[React Agent] Evaluation: SATISFACTORY
[React Agent] Implementation complete after 3 step(s)!  # ✅ SUCCESS!
```

---

## Testing

To verify the fix works, run Agent Studio and watch the console output:

1. Generate a UI in Agent Studio
2. Look for the sequence:
   - Step 1: `generate_initial_implementation` (generates files)
   - Step 2: `fix_import_errors` (fixes imports, NOT regenerate!)
   - Step 3: `finish` (done!)

If you see `generate_initial_implementation` in Step 2, the bug is still present.

---

## Files Modified

1. **src/agents/react_developer.py**
   - Line 1631-1638: Save evaluation to shared_memory
   - Line 1667-1677: Include previous evaluation in planning prompt
   - Line 1696-1702: Better planning guidance with import error handling
   - Line 1972-1986: Smart next_action detection logic

---

## Impact

- ✅ **Eliminates infinite loops** in React Agent autonomous mode
- ✅ **Reduces token waste** by not regenerating unnecessarily
- ✅ **Faster generation** - fixes issues incrementally instead of regenerating
- ✅ **Better debugging** - evaluation history is now stored in shared_memory

---

**Status:** ✅ **FIXED** - React Agent now properly fixes issues incrementally instead of looping

---

## Update: Second Bug Fixed (2025-11-22)

After testing the first fix, we discovered the `fix_import_errors` skill wasn't actually fixing imports - it had a too-narrow regex pattern.

### The Second Issue

**Location:** `src/agents/react_developer.py:2148-2181` (_skill_fix_import_errors)

**Problem:**
```python
# Original regex - ONLY fixed './components/...' imports
fixed_content = re.sub(
    r"from '\./components/([^'\.]+)'",  # Too specific!
    r"from './components/\1.tsx'",
    content
)
```

This only matched imports from `./components/` and missed:
- `from './App'` (root-level imports)
- `from './types'` (type definition imports)
- `from './utils/helper'` (nested paths outside components/)

### The Fix

**File:** `src/agents/react_developer.py:2166-2187`

```python
# Pattern 1: Fix './components/Foo' → './components/Foo.tsx'
content = re.sub(
    r"from '(\./(?:components|utils|hooks|lib)/[^'\.]+)'",
    r"from '\1.tsx'",
    content
)

# Pattern 2: Fix './App' → './App.tsx' (root-level TSX files - capitalized)
content = re.sub(
    r"from '(\./[A-Z][^/'\.]*)'\s*$",
    r"from '\1.tsx'",
    content,
    flags=re.MULTILINE
)

# Pattern 3: Fix './types' → './types.ts' (lowercase files like types, utils)
content = re.sub(
    r"from '(\./[a-z][^/'\.]*)'\s*$",
    r"from '\1.ts'",
    content,
    flags=re.MULTILINE
)
```

Now it handles:
- ✅ Component folder imports: `./components/Foo` → `./components/Foo.tsx`
- ✅ Root-level components: `./App` → `./App.tsx`
- ✅ Type files: `./types` → `./types.ts`
- ✅ Nested paths: `./utils/helper` → `./utils/helper.tsx`

### Expected Behavior After Second Fix

```
Step 1: generate_initial_implementation → 18 files generated
Step 2: fix_import_errors → Actually fixes imports! ✅
Step 3: finish → Done! ✅
```

---

## Update: Third Bug Fixed (2025-11-22)

After testing Fix #2, we discovered the regex was **double-adding extensions** - imports were becoming `.tsx.tsx` instead of `.tsx`.

### The Third Issue

**Location:** `src/agents/react_developer.py:2196` (_skill_fix_import_errors)

**Problem:**
```python
# Regex was matching imports that ALREADY had extensions!
content = re.sub(
    r'''from\s+['"](\.\/[^'"]+)['"](?![^'"]*\.(tsx?|jsx?|json|css))''',
    fix_import,
    content
)
```

**Symptoms:**
```
Failed to resolve import "./App.tsx.tsx" from "src/main.tsx"
import App from "./App.tsx.tsx";
                   ^^^^^^^^^^^^
```

**Root Cause:**
The negative lookahead `(?![^'"]*\.(tsx?|jsx?|json|css))` checked AFTER the closing quote, so it didn't prevent matching imports that already had extensions like `from './App.tsx'`. The pattern would still match and add another `.tsx`, creating `.tsx.tsx`.

### The Fix

**File:** `src/agents/react_developer.py:2196`

```python
# CRITICAL FIX: Use negative lookbehind to prevent double extensions
content = re.sub(
    r'''from\s+['"](\.\/[^'"]+?)(?<!\.tsx)(?<!\.ts)(?<!\.jsx)(?<!\.js)(?<!\.json)(?<!\.css)['"]''',
    fix_import,
    content
)
```

**How it works:**
- `(?<!\.tsx)` - Negative lookbehind: Don't match if path already ends with `.tsx`
- `(?<!\.ts)` - Don't match if already ends with `.ts`
- Same for `.jsx`, `.js`, `.json`, `.css`
- The `+?` (non-greedy) ensures we capture the minimal path before checking extensions

**What changed:**
- ❌ OLD: `(?![^'"]*\.tsx)` - Looked AHEAD after quote (too late!)
- ✅ NEW: `(?<!\.tsx)` - Looks BEHIND at end of path (prevents double-add!)

### Expected Behavior After Third Fix

```
Step 1: generate_initial_implementation → 17 files generated
Step 2: fix_import_errors → Fixes imports WITHOUT doubling extensions! ✅
         - './App' → './App.tsx' ✅
         - './App.tsx' → './App.tsx' (no change - already has extension!) ✅
Step 3: finish → Vite build succeeds! ✅
```

---

**Status:** ✅ **FULLY FIXED** - All three bugs resolved (planning loop, import fixing, double extensions)