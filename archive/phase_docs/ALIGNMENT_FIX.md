# Left/Right Alignment Fix

## Problem

Generated dashboards had dataset cards on the left and file browser on the right, but they appeared disconnected:
- No visual relationship between left cards and right selector
- Heights didn't align properly
- User couldn't tell which card on left was selected on right
- Felt like two separate UIs instead of one connected experience

## Root Cause

The Gradio Developer prompt had example code for drilldown but didn't specify:
1. How to align left and right columns
2. How to show visual connection between them
3. How to highlight selected card

## Solution Applied

### 1. Added Visual Alignment Requirements

**File:** [src/agents/gradio_developer.py](src/agents/gradio_developer.py#L363-L371)

Added specific requirements:
```python
VISUAL ALIGNMENT REQUIREMENTS:
- Use gr.Row(equal_height=True) to align left cards with right file browser
- Left column: Dataset cards as gr.HTML() with consistent card heights
- Right column: Interactive selector + file browser, same total height as left cards
- Add CSS to ensure cards in left column match the vertical space of right column
- Make dataset_selector labels match the card titles for visual connection
- CRITICAL: When dataset is selected on right, regenerate left HTML with highlighted card using gr.update()
- Example: Update left gr.HTML() component on selection change to show which card is active
- Use visual indicator: border, background color, or icon to show selected card on left matches right selector
```

### 2. Updated Example Structure

**File:** [src/agents/gradio_developer.py](src/agents/gradio_developer.py#L333-L361)

Changed from:
```python
# Old: No alignment specified
with gr.Blocks() as demo:
    dataset_selector = gr.Radio(...)
    file_browser = gr.Dataframe(...)
```

To:
```python
# New: Explicit alignment with equal_height
with gr.Blocks() as demo:
    with gr.Row(equal_height=True):  # CRITICAL: equal_height ensures alignment
        with gr.Column(scale=1):
            # Left: Dataset cards (can be HTML for styling)
            gr.HTML(create_dataset_cards_html())

        with gr.Column(scale=1):
            # Right: Interactive file browser
            dataset_selector = gr.Radio(...)
            file_browser = gr.Dataframe(...)
```

### 3. Added UX Designer Guidance

**File:** [src/agents/ux_designer.py](src/agents/ux_designer.py#L301-L307)

Added fallback pattern when progressive disclosure isn't possible:
```python
LEFT/RIGHT LAYOUT ALIGNMENT (when progressive disclosure isn't possible):
- If using side-by-side layout (left: cards, right: file browser), ensure visual connection:
  * Match card titles with selector options (same text, same icons)
  * Use equal heights: left cards column should match right browser column height
  * Add visual indicator: highlight selected card when it matches right-side selection
  * Use consistent spacing: card gaps should match browser section spacing
  * Add connecting element: arrow, line, or shared color to show relationship
```

## Expected Impact

When you regenerate the dashboard, it should now:

1. **Equal Heights:** Left cards column and right browser column align at top and bottom
2. **Visual Connection:** Card titles match selector options (same text, same icon)
3. **Selected State:** When you select "fracfocus" on right, the fracfocus card on left highlights
4. **Consistent Spacing:** Card gaps match the spacing in the file browser section
5. **Connected Feel:** UI feels like one integrated dashboard instead of two separate panels

## Technical Details

### How Selection Highlighting Works

The LLM will generate code like:
```python
# Store cards HTML component reference
cards_display = gr.HTML(create_dataset_cards_html())

# Event handler updates BOTH file browser AND cards
def update_selection(dataset_name):
    files = get_dataset_files(dataset_name)
    cards_html = create_dataset_cards_html(selected=dataset_name)  # Pass selected dataset
    return gr.update(value=files), gr.update(value=cards_html)

dataset_selector.change(
    update_selection,
    inputs=[dataset_selector],
    outputs=[file_browser, cards_display]  # Update both outputs
)
```

### CSS Strategy

The helper function `create_dataset_card()` will add a CSS class to highlight selected:
```python
def create_dataset_card(name: str, data: dict, selected: bool = False) -> str:
    card_class = "md-card-elevated dataset-card"
    if selected:
        card_class += " selected"  # Add 'selected' class

    return f'''<div class="{card_class}">...</div>'''
```

With CSS:
```css
.dataset-card.selected {
    border: 2px solid var(--md-sys-color-primary);
    box-shadow: 0 4px 16px rgba(var(--md-sys-color-primary-rgb), 0.3);
}
```

## Testing

Regenerate your dashboard with the same prompt. You should see:
1. Left and right sides align at the top
2. When you select a dataset, the corresponding card on the left highlights
3. The overall layout feels more connected and cohesive

## Limitations

This is a **visual workaround** for Gradio's limitation that HTML and interactive components can't nest.

**Still not exactly like Lovable:**
- Lovable: File explorer expands **inside** the card
- Ours: File explorer appears on the right, but **visually connected** to the card

**Why we can't do exactly like Lovable:**
- Gradio's `gr.HTML()` is static (can't contain expandable sections)
- Gradio's `gr.Accordion()` can't be nested inside `gr.HTML()`
- This is a fundamental Gradio architecture limitation

**For true Lovable-style in-context expansion:**
- Would need custom Gradio component (JavaScript development)
- Or switch to Streamlit (allows arbitrary HTML/JS)
- Or use full Gradio components instead of HTML cards (loses M3 styling)

This fix maximizes UX quality **within Gradio's constraints**.

---

## Files Modified

- [src/agents/gradio_developer.py](src/agents/gradio_developer.py#L333-L371) - Added alignment requirements and updated example structure
- [src/agents/ux_designer.py](src/agents/ux_designer.py#L301-L307) - Added left/right layout guidance
