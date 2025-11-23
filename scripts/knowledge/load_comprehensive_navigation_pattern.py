"""
Load Comprehensive Gradio Navigation Pattern into Pinecone
Includes: back button, breadcrumb buttons, up/root navigation, current location display
Following Opus's principle: Generic patterns, specific implementations
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.knowledge.design_kb_pinecone import DesignKnowledgeBasePinecone

def load_comprehensive_navigation_pattern():
    kb = DesignKnowledgeBasePinecone()

    comprehensive_nav_pattern = {
        "id": "gradio-complete-bidirectional-navigation",
        "title": "Complete Gradio Bidirectional Navigation Pattern (Generic - All Navigation Types)",
        "category": "pattern",
        "content": """
## Complete Gradio Bidirectional Navigation Pattern
### Generic pattern with multiple navigation options: Back button, Breadcrumb buttons, Current location display

### Problem
Users need to navigate both DOWN (into folders) and UP (to parents/root) the hierarchy.
Static HTML breadcrumbs don't work - need real Gradio buttons for Python handlers.

### Solution: Multiple Navigation Options

Choose the approach that fits your UI:

---

## Option 1: Single Back Button (Simplest)

```python
with gr.Blocks() as demo:
    # Navigation state - stack of path segments
    nav_state = gr.State([])  # e.g., ["rrc", "completions_data", "parsed"]

    # Current location display + Back button
    with gr.Row():
        current_location = gr.Markdown("📁 **Root** / Data Sources")
        back_btn = gr.Button("⬅️ Back", visible=False, size="sm", scale=0)

    # Content area
    content_area = gr.HTML("")

    # Navigate DOWN - push to stack
    def go_down(state, item_name):
        new_state = state + [item_name]
        location = "📁 **Root** / " + " / ".join(new_state)
        content = render_content(new_state)  # Dynamic discovery
        return new_state, location, content, gr.update(visible=True)

    # Navigate UP - pop from stack
    def go_up(state):
        if not state:
            return state, "📁 **Root** / Data Sources", render_root(), gr.update(visible=False)

        new_state = state[:-1]
        location = "📁 **Root** / " + " / ".join(new_state) if new_state else "📁 **Root** / Data Sources"
        content = render_content(new_state)
        back_visible = len(new_state) > 0
        return new_state, location, content, gr.update(visible=back_visible)

    # Wire buttons
    view_btn.click(
        fn=lambda s: go_down(s, "source_name"),
        inputs=[nav_state],
        outputs=[nav_state, current_location, content_area, back_btn]
    )

    back_btn.click(
        fn=go_up,
        inputs=[nav_state],
        outputs=[nav_state, current_location, content_area, back_btn]
    )
```

---

## Option 2: Breadcrumb Buttons (Best UX - Click any level)

```python
with gr.Blocks() as demo:
    nav_state = gr.State([])

    # Breadcrumb buttons - click any level to jump there
    with gr.Row():
        root_btn = gr.Button("📁 Root", size="sm", variant="secondary")
        breadcrumb_btns = []  # Will show/hide dynamically

        # Pre-create buttons for max depth (e.g., 4 levels)
        for i in range(4):
            btn = gr.Button("", visible=False, size="sm", variant="secondary")
            breadcrumb_btns.append(btn)

    content_area = gr.HTML("")

    # Navigate to specific depth
    def navigate_to_depth(state, target_depth):
        '''Jump to any level in hierarchy - 0=root, 1=source, 2=dataset, etc.'''
        new_state = state[:target_depth]  # Truncate to target depth
        content = render_content(new_state)

        # Update breadcrumb button visibility and labels
        breadcrumb_updates = []
        for i in range(4):
            if i < len(new_state):
                breadcrumb_updates.append(gr.update(visible=True, value=new_state[i]))
            else:
                breadcrumb_updates.append(gr.update(visible=False))

        return [new_state, content] + breadcrumb_updates

    # Navigate down
    def go_down(state, item_name):
        new_state = state + [item_name]
        content = render_content(new_state)

        breadcrumb_updates = []
        for i in range(4):
            if i < len(new_state):
                breadcrumb_updates.append(gr.update(visible=True, value=new_state[i]))
            else:
                breadcrumb_updates.append(gr.update(visible=False))

        return [new_state, content] + breadcrumb_updates

    # Wire breadcrumb clicks - each goes to that depth
    root_btn.click(
        fn=lambda s: navigate_to_depth(s, 0),
        inputs=[nav_state],
        outputs=[nav_state, content_area] + breadcrumb_btns
    )

    breadcrumb_btns[0].click(
        fn=lambda s: navigate_to_depth(s, 1),
        inputs=[nav_state],
        outputs=[nav_state, content_area] + breadcrumb_btns
    )

    breadcrumb_btns[1].click(
        fn=lambda s: navigate_to_depth(s, 2),
        inputs=[nav_state],
        outputs=[nav_state, content_area] + breadcrumb_btns
    )
    # ... continue for all depth levels

    # View buttons go down
    view_btn.click(
        fn=lambda s: go_down(s, "item_name"),
        inputs=[nav_state],
        outputs=[nav_state, content_area] + breadcrumb_btns
    )
```

---

## Option 3: Hybrid - Breadcrumb Display + Back Button

```python
with gr.Blocks() as demo:
    nav_state = gr.State([])

    # Breadcrumb display (read-only) + Back button
    with gr.Row():
        breadcrumb_display = gr.HTML('<div style="font-size: 1.1em;">📁 <b>Root</b> / Data Sources</div>')
        with gr.Column(scale=0):
            back_btn = gr.Button("⬅️ Back", visible=False, size="sm")
            root_btn = gr.Button("🏠 Root", visible=False, size="sm")

    content_area = gr.HTML("")

    def update_breadcrumb_display(state):
        '''Generate HTML breadcrumb display'''
        if not state:
            return '<div style="font-size: 1.1em;">📁 <b>Root</b> / Data Sources</div>'

        parts = ['📁 <b>Root</b>'] + [f'<b>{part}</b>' for part in state]
        return f'<div style="font-size: 1.1em;">{" / ".join(parts)}</div>'

    def go_down(state, item_name):
        new_state = state + [item_name]
        breadcrumb = update_breadcrumb_display(new_state)
        content = render_content(new_state)
        return new_state, breadcrumb, content, gr.update(visible=True), gr.update(visible=True)

    def go_up(state):
        if not state:
            return state, update_breadcrumb_display([]), render_root(), gr.update(visible=False), gr.update(visible=False)

        new_state = state[:-1]
        breadcrumb = update_breadcrumb_display(new_state)
        content = render_content(new_state)
        back_visible = len(new_state) > 0
        return new_state, breadcrumb, content, gr.update(visible=back_visible), gr.update(visible=back_visible)

    def go_to_root(state):
        return [], update_breadcrumb_display([]), render_root(), gr.update(visible=False), gr.update(visible=False)

    view_btn.click(
        fn=lambda s: go_down(s, "item"),
        inputs=[nav_state],
        outputs=[nav_state, breadcrumb_display, content_area, back_btn, root_btn]
    )

    back_btn.click(fn=go_up, inputs=[nav_state], outputs=[nav_state, breadcrumb_display, content_area, back_btn, root_btn])
    root_btn.click(fn=go_to_root, inputs=[nav_state], outputs=[nav_state, breadcrumb_display, content_area, back_btn, root_btn])
```

---

## Generic Content Rendering (Works with ALL options)

```python
def render_content(path_stack):
    '''
    Render content based on depth - DISCOVERS structure dynamically
    path_stack: [] = root, ["rrc"] = source, ["rrc", "completions"] = dataset, etc.
    '''
    base_path = Path("data/raw")

    if not path_stack:
        # Root level - show all sources
        return render_sources(base_path)

    # Build full path
    full_path = base_path
    for segment in path_stack:
        full_path = full_path / segment

    if not full_path.exists():
        return f'<div class="error">Path not found: {full_path}</div>'

    if full_path.is_file():
        return render_file_info(full_path)
    else:
        return render_folder_contents(full_path, path_stack)

def render_folder_contents(folder_path, path_stack):
    '''Discover and render folder contents - NO hardcoded paths'''
    html = '<div class="items-grid">'

    # Discover what's in this folder at runtime
    for item in sorted(folder_path.iterdir()):
        item_type = "📁" if item.is_dir() else "📄"
        item_name = item.name

        # Count contents if folder
        count_str = ""
        if item.is_dir():
            try:
                count = len(list(item.iterdir()))
                count_str = f'<span class="count">{count} items</span>'
            except:
                pass

        html += f'''
        <div class="item-card">
            <div class="item-header">{item_type} {item_name}</div>
            {count_str}
            <button onclick="view_{item_name.replace("-", "_")}" class="view-btn">View</button>
        </div>
        '''

    html += '</div>'
    return html
```

---

## Key Principles (Opus's Scalability)

1. **State-Based Navigation**: Path is a list/stack - push to go down, pop to go up, truncate to jump
2. **No Hardcoded Paths**: Use `iterdir()` to discover structure dynamically
3. **Depth-Agnostic**: Works at ANY depth (2 levels or 20 levels)
4. **Real Gradio Components**: `gr.Button()` and `gr.HTML()`, not onclick handlers
5. **Multiple Navigation Options**: Back button, breadcrumb buttons, or hybrid
6. **Generic Content Rendering**: Same `render_content()` function works for all depths

---

## Pattern Selection Guide

- **Simple hierarchy (2-3 levels)**: Option 1 (Back button)
- **Deep hierarchy (4+ levels)**: Option 2 (Breadcrumb buttons)
- **Large screens, need context**: Option 3 (Hybrid)

All options follow the same principle: **state-driven, dynamically discovered, depth-agnostic**.

### Implementation Checklist

✅ Navigation state (`gr.State([])`)
✅ Current location indicator (Markdown or HTML)
✅ Navigation buttons (Back, Root, or Breadcrumbs)
✅ Down navigation (append to state)
✅ Up navigation (pop from state or truncate)
✅ Dynamic content rendering using `iterdir()`
✅ Button visibility updates based on depth
✅ Works for ANY domain (petroleum, medical, finance, etc.)
""",
        "tags": ["gradio", "navigation", "bidirectional", "back-button", "breadcrumb", "generic", "scalable", "complete"],
        "metadata": {
            "pattern_type": "navigation",
            "framework": "gradio",
            "scalability": "generic",
            "navigation_options": ["back_button", "breadcrumb_buttons", "hybrid"],
            "opus_approved": True
        }
    }

    print("Loading Comprehensive Gradio Navigation pattern into Pinecone...")
    kb.add_guideline(
        guideline_id=comprehensive_nav_pattern["id"],
        title=comprehensive_nav_pattern["title"],
        content=comprehensive_nav_pattern["content"],
        category=comprehensive_nav_pattern["category"],
        metadata=comprehensive_nav_pattern["metadata"]
    )
    print(f"[OK] Loaded: {comprehensive_nav_pattern['title']}")

    # Verify it's retrievable
    print("\nVerifying pattern retrieval...")
    results = kb.query(
        "gradio navigation up down hierarchy bidirectional breadcrumb back button complete",
        category="pattern",
        top_k=5
    )

    for i, result in enumerate(results, 1):
        title_safe = result['title'].encode('ascii', 'replace').decode('ascii')
        print(f"{i}. {title_safe} (score: {result.get('score', 0):.2f})")
        if result['id'] == comprehensive_nav_pattern['id']:
            print("   ^ NEW COMPREHENSIVE PATTERN!")

if __name__ == "__main__":
    load_comprehensive_navigation_pattern()
