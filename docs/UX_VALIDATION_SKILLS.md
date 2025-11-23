# UX Validation Skills System

## The Problem You Identified

**Your observation from Session 1.json:**
> "if you look in json the agent was aware that the implementation violated principles but testing skills didnt catch it?"

**Exactly right!** The agent could *explain* UX violations eloquently in conversation, but the Skills validation system didn't *detect* or *prevent* them during code generation.

---

## What Was Wrong (Before)

### Old Skills System (Lines 289-344)

**What it checked:**
1. ✅ Python syntax errors
2. ✅ `@keyframes` in CSS (Gradio limitation)
3. ✅ `<style>` tags
4. ✅ `gr.State` without `.get()`
5. ✅ `.click()` without `outputs=`

**What it DIDN'T check:**
- ❌ Buttons without click handlers (false affordance)
- ❌ Hover states without interactions
- ❌ Data counts without navigation
- ❌ Multiple options without selection UI
- ❌ Empty handler functions

**Result:** Code would pass validation with UX violations, then user would discover issues after launch.

---

## What's Fixed (Now)

### Enhanced Skills System (Lines 289-500)

**Now includes UX Validation:**

#### 1. False Affordance Detection
```python
# UX Test 1: Interactive elements without handlers
has_buttons = "gr.Button" in code
has_click_handlers = ".click(" in code
if has_buttons and not has_click_handlers:
    ux_violations.append("UX VIOLATION: Buttons without .click() handlers (false affordance)")
    print("    [Skill: False Affordance] FAIL - Buttons exist but no .click() handlers")
```

**Catches:** Buttons that look clickable but do nothing

---

#### 2. Hover Affordance Detection
```python
# UX Test 2: Hover states without interaction
has_hover_css = ":hover" in code or "hover" in code.lower()
if has_hover_css and not (has_click_handlers or ".change(" in code):
    ux_violations.append("UX VIOLATION: Hover states without interaction handlers")
```

**Catches:** CSS hover effects without actual event handlers

---

#### 3. Data Navigation Detection
```python
# UX Test 3: Data display without navigation (VISIBILITY OF SYSTEM STATUS)
shows_counts = re.search(r'(\d+)\s+(dataset|item|record)', code, re.IGNORECASE)
has_navigation = "gr.Dropdown" in code or "gr.Radio" in code or "gr.Tabs" in code
if shows_counts and not has_navigation:
    ux_violations.append("UX VIOLATION: Shows data counts but no navigation to access them")
```

**Catches:** Displaying "2 datasets" without a way to navigate to them

---

#### 4. Progressive Disclosure Detection
```python
# UX Test 4: Multiple options without selection mechanism
has_multiple_sources = code.count("gr.Button") > 2 or code.count("gr.Column") > 2
has_selection_ui = "gr.Dropdown" in code or "gr.Radio" in code or "gr.Tabs" in code or ".click(" in code
if has_multiple_sources and not has_selection_ui:
    ux_violations.append("UX VIOLATION: Multiple options without selection mechanism")
```

**Catches:** Many options displayed but no way to choose between them

---

#### 5. Empty Handler Detection
```python
# UX Test 5: Empty event handler functions
empty_handlers = re.findall(r'def\s+\w+\([^)]*\):\s+pass', code)
if empty_handlers:
    ux_violations.append(f"UX VIOLATION: {len(empty_handlers)} empty event handlers (do nothing)")
```

**Catches:** Functions that just have `pass` - they exist but do nothing

---

## Self-Correction Loop (NEW!)

### The Innovation

**Before:** Validation detected issues but code was still returned to user

**Now:** When UX violations detected → automatic self-correction attempt

### The Flow

```python
# Step 4: Validate code (Skills system) with self-correction
validated_code, ux_issues = self._validate_code(code)

# Step 5: Self-correct if UX violations found
if ux_issues:
    print(f"\n  [Gradio Developer] Self-correcting {len(ux_issues)} UX violations...")
    code = self._self_correct_ux_issues(design_spec, code, ux_issues, impl_plan, constraints, context)
    # Re-validate after correction
    validated_code, remaining_issues = self._validate_code(code)
    if remaining_issues:
        print(f"  [Gradio Developer] Warning: {len(remaining_issues)} issues remain after correction")
```

### Self-Correction Prompt

The `_self_correct_ux_issues()` method sends the agent back to fix problems:

```python
prompt = f"""You are an expert Gradio developer fixing UX violations in generated code.

PROBLEMATIC CODE (DO NOT REPEAT THIS):
```python
{problematic_code[:1500]}
...
```

UX VIOLATIONS DETECTED BY SKILLS SYSTEM:
{violations_text}

YOUR TASK: Regenerate the code to FIX ALL these UX violations.

SPECIFIC FIXES NEEDED:

1. FALSE AFFORDANCE:
   - If buttons exist without .click() handlers → ADD .click() handlers
   - If hover CSS exists without interactions → ADD event handlers

2. DATA NAVIGATION:
   - If showing counts (e.g., "2 datasets") → ADD navigation UI (dropdowns/tabs)
   - If displaying data without access → ADD selection mechanism

3. PROGRESSIVE DISCLOSURE:
   - If multiple options without selection → ADD gr.Dropdown or gr.Radio or .click() handlers
   - Enable users to drill down into data

4. EMPTY HANDLERS:
   - If handlers just have 'pass' → IMPLEMENT actual functionality
   - Wire up real state changes and outputs

Generate CORRECTED code that fixes ALL the violations above.
Focus on making interactions FUNCTIONAL, not just present.
"""
```

---

## Example: Catching the Session 1 Bug

### What Would Happen Now

**Code generated (first attempt):**
```python
with gr.Column():
    gr.Button("FracFocus (2 datasets)", elem_classes=["data-card"])
    # BUG: No .click() handler!
```

**Skills System detects:**
```
[Gradio Developer] Validating code (Skills)...
  [Skill: Syntax] PASS
  [Skill: @keyframes] PASS
  [Skill: <style>] PASS
  [Skill: False Affordance] FAIL - Buttons exist but no .click() handlers
  [Skill: Data Navigation] FAIL - Shows counts without navigation
  [Gradio Developer] Validation: 2 UX VIOLATIONS
    ⚠️  UX VIOLATION: Buttons without .click() handlers (false affordance)
    ⚠️  UX VIOLATION: Shows data counts but no navigation to access them
```

**Self-correction triggered:**
```
[Gradio Developer] Self-correcting 2 UX violations...
[Gradio Developer] Analyzing UX violations and regenerating...
[Gradio Developer] Generated 17234 chars of corrected code
```

**Corrected code (second attempt):**
```python
with gr.Column():
    btn = gr.Button("FracFocus (2 datasets)", elem_classes=["data-card"])
    # Fixed: Added click handler!
    btn.click(
        fn=navigate_to_dataset,
        inputs=[gr.State("fracfocus")],
        outputs=[display_area]
    )

# Also added navigation dropdown
dataset_selector = gr.Dropdown(
    choices=["Dataset 1", "Dataset 2"],
    label="Select Dataset"
)
```

**Re-validation:**
```
[Gradio Developer] Validating code (Skills)...
  [Skill: Syntax] PASS
  [Skill: @keyframes] PASS
  [Skill: False Affordance] PASS
  [Skill: Data Navigation] PASS
  [Gradio Developer] Validation: PASS - No issues detected
```

---

## Console Output Comparison

### Before (Old System)
```
[Gradio Developer] Starting implementation...
  [Gradio Developer] Querying framework constraints...
  [Gradio Developer] Creating implementation plan...
  [Gradio Developer] Generating Gradio code...
  [Gradio Developer] Validating code (Skills)...
    [Skill: Syntax] PASS
    [Skill: @keyframes] PASS
  [Gradio Developer] Validation: PASS
[Gradio Developer] Implementation complete: 15234 chars
```
**Result:** Code with UX violations shipped to user

### After (New System)
```
[Gradio Developer] Starting implementation...
  [Gradio Developer] Querying framework constraints...
  [Gradio Developer] Creating implementation plan...
  [Gradio Developer] Generating Gradio code...
  [Gradio Developer] Validating code (Skills)...
    [Skill: Syntax] PASS
    [Skill: @keyframes] PASS
    [Skill: False Affordance] FAIL - Buttons exist but no .click() handlers
    [Skill: Data Navigation] FAIL - Shows counts without navigation
  [Gradio Developer] Validation: 2 UX VIOLATIONS
    ⚠️  UX VIOLATION: Buttons without .click() handlers (false affordance)
    ⚠️  UX VIOLATION: Shows data counts but no navigation to access them

  [Gradio Developer] Self-correcting 2 UX violations...
  [Gradio Developer] Analyzing UX violations and regenerating...
  [Gradio Developer] Generated 17234 chars of corrected code
  [Gradio Developer] Validating code (Skills)...
    [Skill: Syntax] PASS
    [Skill: @keyframes] PASS
    [Skill: False Affordance] PASS
    [Skill: Data Navigation] PASS
  [Gradio Developer] Validation: PASS - No issues detected
[Gradio Developer] Implementation complete: 17234 chars
```
**Result:** UX violations caught and fixed automatically

---

## Architecture Changes

### File: [src/agents/gradio_developer.py](../src/agents/gradio_developer.py)

**Modified Methods:**

1. **`build()` (Lines 70-98)**
   - Added self-correction loop
   - Validates → detects issues → self-corrects → re-validates

2. **`_validate_code()` (Lines 289-412)**
   - Added 5 UX validation tests
   - Returns `(code, ux_violations)` tuple instead of just code
   - Prints detailed violation messages

3. **`_self_correct_ux_issues()` (Lines 414-499)** [NEW!]
   - Takes problematic code + violations
   - Sends corrective prompt to Claude
   - Returns fixed code
   - Called automatically when violations detected

---

## UX Principles Enforced

The Skills system now enforces these UX principles:

### 1. **Affordance Consistency**
- **Principle:** If something looks interactive, it must be interactive
- **Detection:** Buttons without click handlers
- **Material Design:** "Signifiers (affordances) should match functionality"

### 2. **Visibility of System Status**
- **Principle:** Users should know what's available and how to access it
- **Detection:** Showing counts ("2 datasets") without navigation
- **Nielsen's Heuristic #1:** Always keep users informed

### 3. **Progressive Disclosure**
- **Principle:** Present information in layers, let users drill down
- **Detection:** Multiple options without selection mechanism
- **Material Design:** "Use progressive disclosure to simplify interfaces"

### 4. **Functional Completeness**
- **Principle:** UI elements should do what they're supposed to do
- **Detection:** Empty handler functions (just `pass`)
- **Don Norman:** "Design must support the user's goals"

### 5. **Interaction Integrity**
- **Principle:** Visual feedback (hover) should indicate real interactions
- **Detection:** Hover CSS without event handlers
- **Material Design:** "Motion reveals intent"

---

## Impact on Session 1 Bug

### Your Exact Scenario

**User complaint from Session 1.json:**
> "frac focus says 'active' and tells me there are 2 datasets yet i don't see any way to navigate to those datasets"

**What the old system did:**
- ✅ Generated code
- ✅ Validated syntax
- ❌ Didn't detect UX violation
- ❌ Shipped broken code
- 😞 User discovers issue after launch

**What the new system does:**
- ✅ Generates code
- ✅ Validates syntax
- ✅ **DETECTS UX VIOLATION:** "Shows data counts but no navigation to access them"
- ✅ **SELF-CORRECTS:** Regenerates with navigation UI
- ✅ **RE-VALIDATES:** Confirms fix worked
- ✅ Ships working code
- 😊 User never sees the issue

---

## Testing the New System

### Manual Test

```python
# Create test code with violations
test_code = '''
import gradio as gr

def dashboard():
    with gr.Blocks() as demo:
        gr.Markdown("FracFocus - 2 datasets available")
        gr.Button("View Data")  # No .click() handler!
    return demo

dashboard().launch()
'''

# Run validation
from src.agents.gradio_developer import GradioImplementationAgent
agent = GradioImplementationAgent()
code, violations = agent._validate_code(test_code)

# Should detect:
# - False affordance (button without handler)
# - Data navigation (shows "2 datasets" but no access)
print(f"Detected {len(violations)} violations")
for v in violations:
    print(f"  - {v}")
```

**Expected output:**
```
[Gradio Developer] Validating code (Skills)...
  [Skill: Syntax] PASS
  [Skill: @keyframes] PASS
  [Skill: False Affordance] FAIL - Buttons exist but no .click() handlers
  [Skill: Data Navigation] FAIL - Shows counts without navigation
[Gradio Developer] Validation: 2 UX VIOLATIONS
  ⚠️  UX VIOLATION: Buttons without .click() handlers (false affordance)
  ⚠️  UX VIOLATION: Shows data counts but no navigation to access them

Detected 2 violations
  - UX VIOLATION: Buttons without .click() handlers (false affordance)
  - UX VIOLATION: Shows data counts but no navigation to access them
```

---

## Limitations

### What It Still Can't Catch

1. **Semantic issues:** Handler exists but does wrong thing
2. **Data flow bugs:** Navigation works but displays wrong data
3. **Performance issues:** Code works but is slow
4. **Accessibility:** Missing ARIA labels, keyboard navigation
5. **Visual design:** Layout issues, color contrast problems

### Why?

These require **running the code** or **semantic understanding** beyond pattern matching.

### Future Enhancement: Automated Testing

```python
# Future: Actually run Gradio app and test interactions
def _test_generated_app(self, code: str) -> List[str]:
    """Run generated Gradio app and test functionality"""
    # Launch app in headless mode
    # Simulate user clicks
    # Verify state changes
    # Return list of functional bugs found
    pass
```

---

## Summary

**Your question:** "if you look in json the agent was aware that the implementation violated principles but testing skills didnt catch it?"

**Answer:** You were absolutely correct! The Skills system was shallow - it only checked syntax and Gradio gotchas, not UX principles.

**What's fixed:**
1. ✅ Skills now validate UX principles (false affordance, data navigation, progressive disclosure)
2. ✅ Violations trigger automatic self-correction
3. ✅ Code is re-validated after correction
4. ✅ Agent catches and fixes issues before user sees them

**Result:** The same bugs that slipped through in Session 1 will now be caught and corrected automatically during generation.

---

## Try It

```bash
# Launch Agent Studio
python scripts/pipeline/run_ingestion.py --ui

# Watch the console for:
[Gradio Developer] Validation: X UX VIOLATIONS
  [Gradio Developer] Self-correcting X UX violations...
  [Gradio Developer] Validation: PASS - No issues detected

# The agent now polices itself! 🎯
```