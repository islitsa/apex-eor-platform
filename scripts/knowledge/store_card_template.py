"""
Store V2 SOR Card HTML Template in Pinecone
This is the PROVEN card design (user rated 4/5)
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.knowledge.design_kb_pinecone import DesignKnowledgeBasePinecone


# The PROVEN V2 card template (user rated 4/5)
SOR_CARD_TEMPLATE = """
<div style="
    background: white;
    border: 1px solid {{border_color}};
    border-radius: 8px;
    padding: 20px;
    margin: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    height: 200px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
">
    <div>
        <h3 style="margin: 0 0 10px 0; color: {{text_color}}; font-size: 18px; font-weight: 600;">
            {{source_name}}
        </h3>
        <div style="
            display: inline-block;
            background: {{status_color}};
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            margin-bottom: 15px;
        ">
            {{status}}
        </div>
    </div>

    <div style="color: {{text_secondary}}; font-size: 14px; line-height: 1.6;">
        <div><strong>{{records_formatted}}</strong> records</div>
        <div><strong>{{size_formatted}}</strong></div>
        <div style="font-size: 12px; margin-top: 8px;">
            {{pipeline_stages}}
        </div>
    </div>

    <div style="margin-top: 15px;">
        <span style="
            display: inline-block;
            background: {{primary_color}};
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 12px;
            margin-right: 8px;
            opacity: 0.7;
        ">View</span>
        <span style="
            display: inline-block;
            background: transparent;
            color: {{primary_color}};
            border: 1px solid {{primary_color}};
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 12px;
            margin-right: 8px;
            opacity: 0.7;
        ">Download</span>
        <span style="
            display: inline-block;
            background: transparent;
            color: {{text_secondary}};
            border: 1px solid {{border_color}};
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 12px;
            opacity: 0.7;
        ">Re-run</span>
    </div>
    <div style="font-size: 10px; color: {{text_secondary}}; margin-top: 8px; font-style: italic;">
        Actions available in future version
    </div>
</div>
"""


def store_card_template():
    """Store the V2 card template in Pinecone"""

    kb = DesignKnowledgeBasePinecone()

    print("="*70)
    print("STORING V2 SOR CARD TEMPLATE IN PINECONE")
    print("="*70)

    # Store as a component template (not a guideline)
    success = kb.add_guideline(
        guideline_id="component-sor-card-html-v2",
        title="SOR Card HTML Component (V2 - User Rated 4/5)",
        content=f"""
PROVEN SOR Card HTML Template
User Rating: 4/5
Layout: Card-based (NOT accordion)

TEMPLATE:
{SOR_CARD_TEMPLATE}

USAGE IN GENERATED CODE:
```python
card_html = '''
{SOR_CARD_TEMPLATE}
'''.format(
    source_name="RRC Production",
    status="Ready",
    status_color="#52c41a",
    records_formatted="216.1M",
    size_formatted="33.2 GB",
    pipeline_stages="✓ Download → ✓ Extract → ✓ Parse",
    primary_color="#1890ff",
    border_color="#d9d9d9",
    text_color="#262626",
    text_secondary="#8c8c8c"
)

gr.HTML(card_html)
```

VARIABLES TO FILL:
- {{{{source_name}}}}: Display name (e.g., "RRC Production")
- {{{{status}}}}: Status text (e.g., "Ready", "Pending")
- {{{{status_color}}}}: Badge color (#52c41a for Ready, #8c8c8c for Pending)
- {{{{records_formatted}}}}: Formatted record count (e.g., "216.1M")
- {{{{size_formatted}}}}: Formatted size (e.g., "33.2 GB")
- {{{{pipeline_stages}}}}: Pipeline status (e.g., "✓ Download → ✓ Extract → ✓ Parse")
- {{{{primary_color}}}}: #1890ff
- {{{{border_color}}}}: #d9d9d9
- {{{{text_color}}}}: #262626
- {{{{text_secondary}}}}: #8c8c8c

KEY DESIGN PRINCIPLES:
- Fixed height (200px) for consistent grid layout
- Box shadow for depth
- Status badge with color coding
- Visual buttons (opacity 0.7 to show not yet functional)
- White background with border
""",
        category="component",
        metadata={
            "component_type": "sor_card",
            "layout_style": "card",
            "user_rating": 4,
            "version": "v2",
            "proven": True
        }
    )

    if success:
        print("\n✓ SOR Card HTML template stored successfully!")
        print("\nComponent ID: component-sor-card-html-v2")
        print("Category: component")
        print("User Rating: 4/5")
        print("\nComponentAssembler can now query:")
        print('  kb.query("SOR card HTML template", category="component")')
    else:
        print("\n✗ Failed to store template")

    print("="*70)


if __name__ == "__main__":
    store_card_template()
