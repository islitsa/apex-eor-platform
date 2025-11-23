"""
Load Design Principles into Pinecone
Based on Material Design, Apple HIG, and USER FEEDBACK

This rebuilds the design knowledge base that was deleted.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.knowledge.design_kb_pinecone import DesignKnowledgeBasePinecone


def load_all_design_principles():
    """Load comprehensive design principles into Pinecone"""

    kb = DesignKnowledgeBasePinecone()

    print("="*70)
    print("LOADING DESIGN PRINCIPLES INTO PINECONE")
    print("="*70)

    principles = []

    # ========================================================================
    # LAYOUT PATTERNS (Learned from User Feedback!)
    # ========================================================================

    principles.append({
        "id": "layout-sor-cards-vs-accordion",
        "title": "SOR Cards: Card-Based Layout > Accordions",
        "content": """
For Source of Record (SOR) status displays, use CARD-BASED layout, NOT accordions.

USER FEEDBACK (1/5 rating): "I hate the new SOR cards, the old ones were BETTER"

PREFERRED PATTERN (Rated 4/5):
- Individual cards with borders and shadows
- Status badge with color coding
- Records count and file size displayed
- Visual action buttons (View, Download, Re-run)
- Fixed height cards in grid layout

AVOID (Rated 1/5):
- Accordion-based layout for SOR data
- Collapsible sections that hide status
- Text-only status displays

IMPLEMENTATION:
```python
gr.HTML(f'''
<div style="
    background: white;
    border: 1px solid #d9d9d9;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    height: 200px;
">
    <h3>{source_name}</h3>
    <span class="status-badge">{status}</span>
    <div>{records} records</div>
    <div>{size}</div>
</div>
''')
```

RATIONALE: Users need to see all SOR statuses AT A GLANCE, not hidden in accordions.
""",
        "category": "layout",
        "confidence": 0.95,
        "source": "user_feedback_2025"
    })

    principles.append({
        "id": "viz-pipeline-stages",
        "title": "Pipeline Visualization: Simple Boxes > Sankey Diagrams",
        "content": """
For pipeline stage visualization (Download → Extract → Parse), use SIMPLE COLORED BOXES, NOT Sankey diagrams.

USER FEEDBACK (1/5 rating): "The top pipeline 'interactive' vis is the weirdest pipeline vis I have ever seen"

PREFERRED PATTERN:
- Plotly figure with colored rectangles
- Arrows between stages
- Clear stage labels
- Color coding for status (green=complete, blue=in-progress, gray=pending)
- Fixed height (100px), horizontal layout

AVOID:
- Sankey diagrams (too complex, confusing flow)
- Vertical flowcharts
- Interactive node-link diagrams

IMPLEMENTATION:
```python
fig = go.Figure()
stages = ["Download", "Extract", "Parse"]
colors = ["#52c41a", "#1890ff", "#d9d9d9"]

for i, (stage, color) in enumerate(zip(stages, colors)):
    fig.add_shape(
        type="rect",
        x0=i*2, y0=0, x1=i*2+1.5, y1=1,
        fillcolor=color,
        line=dict(color=color, width=2),
        opacity=0.8
    )
    fig.add_annotation(
        x=i*2+0.75, y=0.5,
        text=stage,
        showarrow=False,
        font=dict(color='white', size=12)
    )
```

RATIONALE: Users need CLARITY, not complexity. Pipeline stages are linear, show them linearly.
""",
        "category": "visualization",
        "confidence": 0.95,
        "source": "user_feedback_2025"
    })

    principles.append({
        "id": "buttons-visual-over-functional",
        "title": "Buttons: Visual Presence > Functional (Initially)",
        "content": """
Include visual action buttons EVEN IF not yet functional.

USER FEEDBACK: "We needed those buttons that didn't work yet"

PRINCIPLE: Visual affordances matter more than immediate functionality.
Users understand "Coming Soon" features, but they need to SEE the intended UI.

IMPLEMENTATION:
```python
# Visual buttons with disabled state + explanation
<button style="opacity: 0.7;">View</button>
<button style="opacity: 0.7;">Download</button>
<button style="opacity: 0.7;">Re-run</button>
<div style="font-size: 10px; font-style: italic;">
    Actions available in future version
</div>
```

RATIONALE: Shows users the intended interface, sets expectations, looks complete.
""",
        "category": "interaction",
        "confidence": 0.9,
        "source": "user_feedback_2025"
    })

    # ========================================================================
    # MATERIAL DESIGN 3 PRINCIPLES
    # ========================================================================

    principles.append({
        "id": "md3-color-system",
        "title": "Material Design 3: Color System",
        "content": """
Material Design 3 Color System for Gradio dashboards:

PRIMARY COLORS:
- Primary: #1890ff (blue) - main actions, key UI elements
- Success: #52c41a (green) - positive states, completed actions
- Warning: #faad14 (amber) - warnings, in-progress states
- Error: #ff4d4f (red) - errors, failed states

NEUTRAL COLORS:
- Text Primary: #262626 (almost black)
- Text Secondary: #8c8c8c (gray)
- Border: #d9d9d9 (light gray)
- Background Light: #fafafa (off-white)

USAGE:
- Status badges: Use semantic colors (green=Ready, blue=Running, red=Error)
- Buttons: Primary color for main actions
- Text hierarchy: Primary for headers, secondary for details
- Borders: Light gray for card boundaries

ACCESSIBILITY: All combinations meet WCAG AA contrast ratios (4.5:1)
""",
        "category": "colors",
        "confidence": 1.0,
        "source": "material_design_3"
    })

    principles.append({
        "id": "md3-typography",
        "title": "Material Design 3: Typography",
        "content": """
Typography for Gradio dashboards:

FONT FAMILY: Use system fonts (Gradio default) or Roboto

HIERARCHY:
- Page Title: 24-28px, font-weight: 600
- Section Headers: 18-20px, font-weight: 600
- Card Titles: 16-18px, font-weight: 600
- Body Text: 14px, font-weight: 400
- Small Text: 12px, font-weight: 400
- Micro Text: 10px, font-weight: 400

LINE HEIGHT: 1.5 for readability

IMPLEMENTATION:
```python
gr.Markdown("# Page Title")  # 24px
gr.Markdown("## Section Header")  # 20px
gr.Markdown("### Card Title")  # 18px
```
""",
        "category": "typography",
        "confidence": 1.0,
        "source": "material_design_3"
    })

    principles.append({
        "id": "md3-spacing",
        "title": "Material Design 3: Spacing (8dp Grid)",
        "content": """
Use 8dp (8px) grid system for all spacing:

SPACING SCALE:
- 4px: tight spacing (within buttons)
- 8px: compact spacing (between related items)
- 16px: default spacing (between components)
- 24px: comfortable spacing (between sections)
- 32px: loose spacing (major sections)

PADDING:
- Cards: 20px (close to 16px/24px)
- Buttons: 6px 12px (vertical horizontal)
- Sections: 16-24px

MARGINS:
- Between cards: 10-16px
- Between sections: 24-32px

IMPLEMENTATION:
```python
with gr.Row():
    with gr.Column(scale=1):
        gr.Markdown("## Section")  # 24px margin below
```
""",
        "category": "spacing",
        "confidence": 1.0,
        "source": "material_design_3"
    })

    # ========================================================================
    # APPLE HUMAN INTERFACE GUIDELINES
    # ========================================================================

    principles.append({
        "id": "apple-clarity",
        "title": "Apple HIG: Clarity Principle",
        "content": """
Apple's Clarity Principle: "Throughout the system, text is legible at every size, icons are precise and lucid, adornments are subtle and appropriate, and a sharpened focus on functionality motivates the design."

FOR DASHBOARDS:
- Use clear, precise labels (not jargon)
- Icons should be recognizable at small sizes
- Avoid decorative elements that don't serve function
- Prioritize readable text over stylistic fonts

EXAMPLES:
✅ "Total Records: 216,789,216"
❌ "Records: 216.8M" (less precise)

✅ Status badges with text + color
❌ Icon-only status indicators

RATIONALE: Users need to understand information quickly and accurately.
""",
        "category": "usability",
        "confidence": 1.0,
        "source": "apple_hig"
    })

    principles.append({
        "id": "apple-consistency",
        "title": "Apple HIG: Consistency Principle",
        "content": """
Maintain visual and behavioral consistency throughout the interface.

CONSISTENCY RULES:
- Use same card design for all SOR displays
- Use same color scheme for all status indicators
- Use same button styles for all actions
- Use same spacing throughout

IMPLEMENTATION:
- Create reusable components (card template, button template)
- Store in Pinecone as proven patterns
- Reference by ID, don't recreate

ANTI-PATTERN: Mixing card styles, accordion styles, list styles for same data type

RATIONALE: Consistency reduces cognitive load and builds user confidence.
""",
        "category": "usability",
        "confidence": 1.0,
        "source": "apple_hig"
    })

    # ========================================================================
    # DATA VISUALIZATION PRINCIPLES
    # ========================================================================

    principles.append({
        "id": "viz-type-selection",
        "title": "Visualization Type Selection Guide",
        "content": """
Match visualization type to data structure:

LINEAR SEQUENCES (Pipeline Stages):
- Horizontal box diagram with arrows
- Timeline visualization
- Step indicator
AVOID: Sankey, network graphs, circular flows

HIERARCHICAL DATA:
- Tree diagrams
- Nested cards
- Accordion (only if >5 levels)

COMPARISONS:
- Bar charts (horizontal for names, vertical for time)
- Column charts
- Grouped bars for multi-category

TRENDS OVER TIME:
- Line charts
- Area charts (for cumulative values)

PROPORTIONS:
- Pie charts (max 5 slices)
- Donut charts
- Stacked bars

RELATIONSHIPS:
- Scatter plots
- Bubble charts
- Heatmaps

PRINCIPLE: Choose the SIMPLEST visualization that clearly shows the pattern.
""",
        "category": "visualization",
        "confidence": 1.0,
        "source": "data_viz_best_practices"
    })

    # ========================================================================
    # SCROLLING & VIEWPORT PRINCIPLES
    # ========================================================================

    principles.append({
        "id": "scrolling-cards",
        "title": "Scrolling: When to Use Scrollbars",
        "content": """
Scrollbar usage guidelines:

FIXED HEIGHT + SCROLLBARS:
- Long lists (>10 items)
- Chat/log displays
- File browsers
- Data tables

NO SCROLLBARS (Page Scroll):
- Dashboard overview pages
- Status cards (show all)
- Form inputs
- Settings pages

IMPLEMENTATION:
```python
# Scrollable logs
gr.Textbox(lines=10, max_lines=20)  # Scrolls after 10 lines

# Card grid - no scrollbars
with gr.Row():
    # Cards auto-wrap to next row
```

PRINCIPLE: Users should see all critical status information without scrolling.
Scrolling is for details, not for overview.
""",
        "category": "layout",
        "confidence": 0.9,
        "source": "ux_best_practices"
    })

    # ========================================================================
    # LOAD INTO PINECONE
    # ========================================================================

    print(f"\nLoading {len(principles)} design principles...")

    for i, principle in enumerate(principles, 1):
        success = kb.add_guideline(
            guideline_id=principle["id"],
            title=principle["title"],
            content=principle["content"],
            category=principle["category"],
            metadata={
                "confidence": principle.get("confidence", 0.8),
                "source": principle.get("source", "unknown")
            }
        )

        if success:
            print(f"  [{i}/{len(principles)}] OK {principle['title']}")
        else:
            print(f"  [{i}/{len(principles)}] FAILED: {principle['title']}")

    print("\n" + "="*70)
    print("DESIGN PRINCIPLES LOADED")
    print("="*70)
    print(f"\nTotal principles: {len(principles)}")
    print("\nCategories:")
    categories = {}
    for p in principles:
        cat = p["category"]
        categories[cat] = categories.get(cat, 0) + 1
    for cat, count in categories.items():
        print(f"  - {cat}: {count}")

    print("\n" + "="*70)
    print("USAGE")
    print("="*70)
    print("""
Now the ComponentAssembler can query design principles:

# Query for SOR card layout
principles = kb.query("how to display source of record cards", category="layout")

# Query for pipeline visualization
viz_guidance = kb.query("pipeline stage visualization", category="visualization")

# Query for colors
colors = kb.query("status indicator colors", category="colors")
""")
    print("="*70)


if __name__ == "__main__":
    load_all_design_principles()
