# How Agents Learn From Feedback

## The Question
**User asked:** "how are they going to learn from feedback?"

This is a critical question about the agent system's ability to iterate and improve.

## The Answer

Agents learn through a **session-based memory system** that captures:
1. ✅ Previous code attempts
2. ✅ User feedback on those attempts
3. ✅ What components/patterns were used
4. ✅ Iterative context across regenerations

---

## Learning Architecture

### Memory Storage (What Gets Remembered)

Each time an agent generates code, the system stores:

```python
memory_entry = {
    "screen_type": "dashboard_navigation",
    "intent": "Navigate through data pipeline",
    "code_length": 15234,
    "constraints_applied": ['css', 'state', 'events'],
    "code_summary": "gr.Button, gr.Dropdown, .click() handler",  # What was used
    "full_code": "import gradio as gr...",  # First 2000 chars of actual code
    "user_feedback": "fix the navigation - make cards clickable"  # What user said
}
```

**Key insight:** The agent doesn't just track metadata - it stores **actual code snippets** and **exact user complaints**.

### Memory Retrieval (How It's Used)

When regenerating, agents see a formatted history:

```
PREVIOUS IMPLEMENTATIONS IN THIS SESSION:
============================================================

Initial version: dashboard_navigation
   Components used: gr.Button, gr.Markdown, gr.Row, gr.Column
   Code length: 15234 chars

Version 2: dashboard_navigation
   Components used: gr.Button, gr.Dropdown, gr.Markdown, .click() handler
   Code length: 16789 chars
   ⚠️  USER SAID: "fix the navigation - make cards clickable"
   This version was created in response to that feedback
   Code snippet (first 500 chars):
   --------------------------------------------------
   import gradio as gr

   def dashboard():
       with gr.Blocks() as demo:
           with gr.Row():
               for source in data_sources:
                   with gr.Column():
                       btn = gr.Button(source)
                       # BUG: No .click() handler attached!
   --------------------------------------------------

Version 3: dashboard_navigation
   Components used: gr.Button, gr.Dropdown, .click() handler, gr.State
   Code length: 18234 chars
   ⚠️  USER SAID: "add dropdown menus for navigation"
   This version was created in response to that feedback
   Code snippet (first 500 chars):
   --------------------------------------------------
   import gradio as gr

   def dashboard():
       with gr.Blocks() as demo:
           # Added dropdown navigation
           dataset_selector = gr.Dropdown(
               choices=list(datasets.keys()),
               label="Select Dataset"
           )
   --------------------------------------------------

============================================================
LEARNING FROM HISTORY:
- Review previous versions and what feedback they received
- If user complained about something, DON'T repeat that mistake
- Build incrementally on what worked
- Address the specific issues mentioned in feedback
============================================================
```

**Key insight:** Each regeneration includes context about **what failed before** and **why**.

---

## Learning Flow (Step-by-Step)

### Iteration 1: Initial Generation
```
User: [Starts system]
    ↓
UX Designer: Designs initial dashboard
    ↓
Gradio Developer: Implements code
    ↓
Memory Stores:
  - Code: "gr.Button cards, no click handlers"
  - Feedback: None
  - Components: gr.Button, gr.Markdown
```

### Iteration 2: User Gives Feedback
```
User: "fix the navigation - make cards clickable"
    ↓
Agent Studio: Detects 'fix' keyword
    ↓
Creates requirements with user_feedback field
    ↓
UX Designer receives:
  IMPORTANT - USER FEEDBACK: "fix the navigation - make cards clickable"
    ↓
Gradio Developer receives:
  CRITICAL - USER FEEDBACK: "fix the navigation - make cards clickable"
  PREVIOUS IMPLEMENTATIONS:
    - Version 1 had gr.Button but no .click() handlers
    ↓
Gradio Developer generates:
  - Adds .click() handlers to all buttons
  - Wires interactions properly
    ↓
Memory Stores:
  - Code: "gr.Button with .click() handlers"
  - Feedback: "fix the navigation - make cards clickable"
  - Components: gr.Button, .click() handler
  - Previous attempt: Shows version 1 code snippet
```

### Iteration 3: More Feedback
```
User: "add dropdown menus for navigation"
    ↓
Gradio Developer receives:
  CRITICAL - USER FEEDBACK: "add dropdown menus for navigation"
  PREVIOUS IMPLEMENTATIONS:
    - Version 1: Buttons without handlers
      USER SAID: None
    - Version 2: Buttons with click handlers
      USER SAID: "fix the navigation - make cards clickable"
    ↓
Gradio Developer analyzes:
  - Version 1 failed: no interactions
  - Version 2 fixed: added click handlers
  - Version 3 needs: dropdown navigation pattern
    ↓
Generates code with gr.Dropdown + .change() handlers
    ↓
Memory Stores:
  - Code: "gr.Dropdown with .change() handlers"
  - Feedback: "add dropdown menus for navigation"
  - Components: gr.Dropdown, .change() handler
  - History: Shows versions 1-2 with their feedback
```

---

## Technical Implementation

### 1. Storing Code & Feedback
**File:** [src/agents/gradio_developer.py:346-366](../src/agents/gradio_developer.py#L346-L366)

```python
def _add_to_memory(self, design_spec: DesignSpec, code: str,
                   constraints: Dict, user_feedback: str = None):
    """Add implementation to memory for session continuity"""
    code_summary = self._extract_code_summary(code)

    memory_entry = {
        "screen_type": design_spec.screen_type,
        "intent": design_spec.intent,
        "code_summary": code_summary,  # What components were used
        "full_code": code[:2000],       # Actual code snippet
        "user_feedback": user_feedback, # What user complained about
    }
    self.implementation_history.append(memory_entry)
```

### 2. Extracting Patterns
**File:** [src/agents/gradio_developer.py:368-381](../src/agents/gradio_developer.py#L368-L381)

```python
def _extract_code_summary(self, code: str) -> str:
    """Extract key Gradio components and patterns from code"""
    components_found = []

    # Detect what was used
    gradio_components = ['gr.Button', 'gr.Dropdown', 'gr.Textbox', ...]
    for comp in gradio_components:
        if comp in code:
            components_found.append(comp)

    # Detect interaction patterns
    if '.click(' in code:
        components_found.append('.click() handler')
    if '.change(' in code:
        components_found.append('.change() handler')

    return ', '.join(components_found)
```

### 3. Showing History to Agent
**File:** [src/agents/gradio_developer.py:388-420](../src/agents/gradio_developer.py#L388-L420)

```python
def _get_memory_context(self) -> str:
    """Format implementation history for including in prompts"""
    lines = ["PREVIOUS IMPLEMENTATIONS IN THIS SESSION:"]

    for i, entry in enumerate(self.implementation_history, 1):
        version_label = "Initial version" if i == 1 else f"Version {i}"
        lines.append(f"{version_label}: {entry['screen_type']}")
        lines.append(f"   Components used: {entry['code_summary']}")

        # Show what user complained about
        if entry.get('user_feedback'):
            lines.append(f"   ⚠️  USER SAID: \"{entry['user_feedback']}\"")
            lines.append(f"   This version was created in response to that feedback")

        # Show snippet of actual code
        if 'full_code' in entry:
            lines.append(f"   Code snippet:")
            lines.append(entry['full_code'][:500])

    lines.append("LEARNING FROM HISTORY:")
    lines.append("- If user complained about something, DON'T repeat that mistake")
    lines.append("- Build incrementally on what worked")

    return "\n".join(lines)
```

---

## What Makes This "Learning"?

### ✅ Pattern Recognition
- Agent sees: "Version 1 had gr.Button without .click() → user complained"
- Agent learns: "Buttons need click handlers"

### ✅ Incremental Improvement
- Version 1: Static cards (no interaction)
- Version 2: Clickable cards (responds to "make clickable")
- Version 3: Dropdown navigation (responds to "add dropdowns")
- Each version **builds on** previous versions instead of starting fresh

### ✅ Mistake Avoidance
```
LEARNING FROM HISTORY:
- Review previous versions and what feedback they received
- If user complained about something, DON'T repeat that mistake
- Build incrementally on what worked
- Address the specific issues mentioned in feedback
```

### ✅ Context Accumulation
- Generation 1: No context
- Generation 2: Sees generation 1 + user feedback
- Generation 3: Sees generations 1-2 + all feedback history
- Each regeneration has **richer context** than the previous

---

## Example Learning Scenario

### Problem: Cards Not Clickable

**Generation 1:**
```python
# Code generated
with gr.Column():
    gr.Button("FracFocus", elem_classes=["data-card"])
    # BUG: No click handler!
```

**User feedback:** "when i hover over fracfocus card it appears to be clickable, when i click - nothing happens. why?"

**Generation 2 sees:**
```
PREVIOUS IMPLEMENTATIONS:
Initial version: dashboard_navigation
   Components used: gr.Button, gr.Markdown
   Code snippet:
   --------------------------------------------------
   with gr.Column():
       gr.Button("FracFocus", elem_classes=["data-card"])
       # No .click() handler attached
   --------------------------------------------------

CRITICAL - USER FEEDBACK:
"when i hover over fracfocus card it appears to be clickable, when i click - nothing happens"

LEARNING INSTRUCTIONS:
- Previous version created buttons without click handlers
- User explicitly complained they don't work
- DON'T repeat this mistake
- Add proper .click() handlers
```

**Generation 2 produces:**
```python
# Code generated (with learning applied)
with gr.Column():
    btn = gr.Button("FracFocus", elem_classes=["data-card"])
    btn.click(
        fn=navigate_to_dataset,
        inputs=[gr.State("fracfocus")],
        outputs=[display_area]
    )
    # Fixed: Now has click handler!
```

---

## Limitations & Future Enhancements

### Current Limitations

1. **Session-only memory**
   - Memory resets when Agent Studio closes
   - No cross-session learning
   - Solution: Persist memory to file or database

2. **Limited code storage**
   - Only stores first 2000 chars of code
   - Complex implementations may lose context
   - Solution: Store full code with compression or use embeddings

3. **No automated testing**
   - Agent can't verify if fix actually worked
   - Relies on user to test and report back
   - Solution: Add automated Gradio app testing

### Future Enhancements

1. **Persistent Knowledge Base**
   ```python
   # Store successful patterns in Pinecone
   successful_pattern = {
       "problem": "cards not clickable",
       "solution": "gr.Button with .click() handler",
       "code_snippet": "btn.click(fn=..., inputs=..., outputs=...)"
   }
   pinecone_index.upsert(successful_pattern)
   ```

2. **Cross-Session Learning**
   ```python
   # Query past sessions for similar problems
   similar_issues = pinecone_index.query(
       "cards not clickable hover state",
       top_k=3
   )
   # Apply solutions from past sessions
   ```

3. **Automated Verification**
   ```python
   # Test generated code automatically
   test_result = run_gradio_tests(generated_code)
   if test_result.failed:
       memory_entry['test_failure'] = test_result.error
       # Regenerate with test failure context
   ```

---

## Summary

**Q: How do agents learn from feedback?**

**A:** Through a sophisticated memory system that:

1. **Captures** previous code attempts and user feedback
2. **Stores** what components were used and what failed
3. **Retrieves** this history during regeneration
4. **Incorporates** lessons learned into new prompts
5. **Iterates** with increasingly rich context

The agent doesn't just get told "fix it" - it sees:
- What code it generated before
- What the user complained about
- What components it tried
- What patterns worked/failed

This creates a **learning loop** where each iteration is informed by all previous attempts, leading to continuous improvement until the user is satisfied.

---

## Try It Yourself

```bash
# Start Agent Studio
python scripts/pipeline/run_ingestion.py --ui

# Watch the learning loop in action:
# 1. System generates initial dashboard
# 2. You give feedback: "fix the navigation"
# 3. Check the console - you'll see:
#    [Gradio Developer] Added to memory (2 implementations) (responding to: 'fix the navigation'...)
# 4. The agent sees its previous code + your feedback
# 5. It generates improved code addressing your concerns
# 6. Repeat until satisfied!
```

Each iteration shows:
```
PREVIOUS IMPLEMENTATIONS IN THIS SESSION:
  Initial version: [shows what was tried]
  Version 2: [shows what you asked for]
    ⚠️  USER SAID: "fix the navigation"
  Version 3: [incorporates all previous learning]
    ⚠️  USER SAID: "add dropdowns"
```

**This is iterative learning in action!** 🧠