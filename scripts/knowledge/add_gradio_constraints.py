"""
Add Gradio Framework Constraints to Pinecone Knowledge Base

This addresses the knowledge gap where the agent knows UX patterns
but doesn't know framework-specific limitations.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.knowledge.design_kb_pinecone import DesignKnowledgeBasePinecone

def add_gradio_knowledge():
    kb = DesignKnowledgeBasePinecone()

    print("Adding Gradio framework constraints to knowledge base...\n")

    # 1. CSS Limitations (CRITICAL)
    kb.add_guideline(
        guideline_id='gradio-css-limitations',
        title='Gradio CSS Limitations - No @keyframes in gr.HTML',
        content='''
CRITICAL GRADIO CONSTRAINT: CSS @keyframes Forbidden in gr.HTML

PROBLEM:
- gr.HTML() content doesn't support <style> tags with @keyframes
- Python f-strings parse "0%" and "100%" as syntax errors
- This is a KNOWN Gradio issue, not a bug

WRONG APPROACH:
```python
html = f\"\"\"
<style>
  @keyframes spin {{
    0% {{ transform: rotate(0deg); }}  # BREAKS PYTHON!
    100% {{ transform: rotate(360deg); }}
  }}
</style>
<div style="animation: spin 1s;">Loading</div>
\"\"\"
```

CORRECT APPROACH - Use Unicode Spinners:
```python
html = f\"\"\"
<div style="display: flex; align-items: center;">
  <span style="font-size: 20px; margin-right: 8px;">🔄</span>
  <span>Loading...</span>
</div>
\"\"\"
```

ANIMATION ALTERNATIVES:
- Unicode: ⏳ ⌛ 🔄 ⟳ ⏱️ ⏰ 💫 ✨ 🌀 🔁
- Text-based: "Loading..." "Processing..." "Please wait..."
- Static progress bars with colors and percentages

RULE: NEVER use @keyframes in gr.HTML() code generation.
''',
        category='framework',
        metadata={'framework': 'gradio', 'priority': 'critical', 'type': 'constraint'}
    )

    # 2. gr.Blocks CSS Parameter Limitation
    kb.add_guideline(
        guideline_id='gradio-blocks-css-limitation',
        title='Gradio gr.Blocks CSS Parameter - Limited Scope',
        content='''
GRADIO CONSTRAINT: gr.Blocks(css=...) Only Applies to Gradio Components

THE ISSUE:
```python
demo = gr.Blocks(css="div { color: red; }") as demo:
    gr.HTML("<div>This won't be red!</div>")  # CSS doesn't apply!
    gr.Button("This might be affected")       # Only Gradio components get CSS
```

WHY:
- gr.Blocks CSS applies ONLY to Gradio's own components
- gr.HTML() content is injected dynamically at runtime
- Dynamic HTML doesn't inherit the CSS from gr.Blocks

SOLUTION: Use Inline Styles in gr.HTML
```python
demo = gr.Blocks() as demo:
    gr.HTML("""
        <div style="color: red; padding: 16px;">
            All styling MUST be inline
        </div>
    """)
```

RULE: All styling in gr.HTML() must be inline style="..." attributes.
RULE: Cannot use CSS classes, external stylesheets, or <style> tags.
''',
        category='framework',
        metadata={'framework': 'gradio', 'priority': 'high', 'type': 'constraint'}
    )

    # 3. Event Handling Pattern
    kb.add_guideline(
        guideline_id='gradio-event-handling-pattern',
        title='Gradio Event Handling - .click() Pattern',
        content='''
GRADIO PATTERN: Event Handling with .click()

CORRECT PATTERN:
```python
with gr.Blocks() as demo:
    input_text = gr.Textbox()
    output_text = gr.Textbox()
    submit_btn = gr.Button("Submit")

    # Event handler function
    def handle_submit(text):
        return f"Processed: {text}"

    # Wire up the event
    submit_btn.click(
        fn=handle_submit,
        inputs=input_text,
        outputs=output_text
    )
```

COMMON MISTAKES:
1. Forgetting outputs= parameter (nothing updates)
2. Using onclick="" in HTML (doesn't work with gr.HTML)
3. Defining handlers outside gr.Blocks context

RULE: All event handlers must be wired with .click() INSIDE gr.Blocks context.
RULE: Always specify both inputs= and outputs= parameters.
''',
        category='framework',
        metadata={'framework': 'gradio', 'priority': 'medium', 'type': 'pattern'}
    )

    # 4. gr.State Usage Pattern
    kb.add_guideline(
        guideline_id='gradio-state-pattern',
        title='Gradio gr.State - Stateful Navigation Pattern',
        content='''
GRADIO PATTERN: Using gr.State for Stateful Interactions

CORRECT PATTERN:
```python
with gr.Blocks() as demo:
    nav_state = gr.State({"current_path": [], "view": "home"})

    def navigate(state, item):
        # ALWAYS use .get() for safety
        current_path = state.get("current_path", [])
        current_path.append(item)
        state["current_path"] = current_path
        return state  # Must return updated state

    btn.click(
        fn=navigate,
        inputs=[nav_state, gr.Textbox()],
        outputs=nav_state  # State must be in outputs!
    )
```

COMMON MISTAKES:
1. Using state["key"] without .get() → KeyError
2. Not returning state from handler
3. Not including state in outputs=

RULE: Always use state.get("key", default) for safe access.
RULE: State must be in both inputs= AND outputs= of event handler.
''',
        category='framework',
        metadata={'framework': 'gradio', 'priority': 'medium', 'type': 'pattern'}
    )

    # 5. Python f-string Constraints
    kb.add_guideline(
        guideline_id='gradio-fstring-constraints',
        title='Python f-strings in Gradio HTML - Escaping Rules',
        content='''
GRADIO CONSTRAINT: Python f-string Escaping in gr.HTML

THE ISSUE: CSS and JavaScript in f-strings can break Python parsing

PROBLEMATIC PATTERNS:
1. CSS percentages: "width: 50%" → Python sees 50% as invalid
2. CSS @keyframes: "0% { }" → Python syntax error
3. JavaScript template literals: `${var}` → Conflicts with f-string
4. Curly braces in CSS: "{{ }}" → Needs escaping

SAFE PATTERNS:
```python
# Escape curly braces in CSS
html = f"""
<div style="background: rgb({{r}}, {{g}}, {{b}});">
    Content
</div>
"""

# Use style attributes, not <style> tags
html = f"""
<div style="width: 50%; padding: 10px;">  <!-- OK: inline -->
    {dynamic_content}
</div>
"""
```

RULE: Avoid <style> tags entirely in gr.HTML f-strings.
RULE: Use inline styles with simple properties only.
RULE: Avoid CSS features that use % or complex syntax.
''',
        category='framework',
        metadata={'framework': 'gradio', 'priority': 'high', 'type': 'constraint'}
    )

    print("✓ Added 5 Gradio framework constraints to knowledge base")
    print("\nKnowledge categories added:")
    print("  - CSS Limitations (@keyframes forbidden)")
    print("  - gr.Blocks CSS scope (limited to Gradio components)")
    print("  - Event handling patterns (.click())")
    print("  - gr.State usage patterns")
    print("  - Python f-string constraints in HTML")
    print("\nThe agent can now query these constraints via RAG!")

if __name__ == "__main__":
    add_gradio_knowledge()