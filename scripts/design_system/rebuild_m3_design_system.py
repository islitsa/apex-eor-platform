"""
Rebuild M3 Design System in Pinecone - Proper RAG Architecture

This script creates a clean, authoritative M3 design system with:
1. Single source of truth for design tokens (colors, spacing, typography)
2. Component specs that REFERENCE tokens, not hardcode them
3. Clear separation between principles and implementation examples

Key Principle: Make design choices queryable, not hardcoded.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from knowledge.design_kb_pinecone import DesignKnowledgeBasePinecone


# ==============================================================================
# DESIGN TOKENS - Single Source of Truth
# ==============================================================================

M3_DESIGN_TOKENS = {
    "id": "m3-design-tokens-authority",
    "category": "design-tokens",
    "title": "Material Design 3 Design Tokens (Authoritative)",
    "content": """Material Design 3 Design Tokens

This is the SINGLE SOURCE OF TRUTH for all M3 design values.
All component specifications must reference these tokens, never hardcode values.

═══════════════════════════════════════════════════════════════════
COLOR TOKENS
═══════════════════════════════════════════════════════════════════

PRIMARY PALETTE:
  primary: #1890ff          (Blue - main brand color, key actions)
  on-primary: #FFFFFF       (White - text on primary color)
  primary-container: #D6E4FF (Light blue - emphasized containers)
  on-primary-container: #001D35

SURFACE COLORS:
  surface: #FEFBFF          (Off-white - default background)
  surface-variant: #E7E0EC  (Light gray - subtle containers)
  on-surface: #1C1B1F       (Almost black - default text)
  on-surface-variant: #49454F (Gray - secondary text)

ACCENT COLORS:
  secondary: #625B71        (Purple-gray - less prominent actions)
  tertiary: #7D5260         (Burgundy - tertiary actions)
  error: #B3261E            (Red - errors, destructive actions)
  success: #4CAF50          (Green - success states)
  warning: #FB8C00          (Orange - warnings)

OUTLINE/BORDERS:
  outline: #79747E          (Medium gray - borders, dividers)
  outline-variant: #CAC4D0  (Light gray - subtle borders)

═══════════════════════════════════════════════════════════════════
SPACING TOKENS (8dp Grid System)
═══════════════════════════════════════════════════════════════════

  xs: 4px     (0.5 units - tight spacing)
  sm: 8px     (1 unit - compact spacing)
  md: 16px    (2 units - default spacing)
  lg: 24px    (3 units - comfortable spacing)
  xl: 32px    (4 units - spacious sections)
  2xl: 48px   (6 units - major section breaks)

═══════════════════════════════════════════════════════════════════
TYPOGRAPHY TOKENS
═══════════════════════════════════════════════════════════════════

FONT FAMILY:
  base: 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif

DISPLAY SIZES (Headlines):
  display-large: 57px / 64px line-height, font-weight: 400
  display-medium: 45px / 52px, weight: 400
  display-small: 36px / 44px, weight: 400

HEADLINE SIZES:
  headline-large: 32px / 40px, weight: 400
  headline-medium: 28px / 36px, weight: 400
  headline-small: 24px / 32px, weight: 400

TITLE SIZES:
  title-large: 22px / 28px, weight: 400
  title-medium: 16px / 24px, weight: 500
  title-small: 14px / 20px, weight: 500

BODY SIZES:
  body-large: 16px / 24px, weight: 400
  body-medium: 14px / 20px, weight: 400
  body-small: 12px / 16px, weight: 400

LABEL SIZES:
  label-large: 14px / 20px, weight: 500
  label-medium: 12px / 16px, weight: 500
  label-small: 11px / 16px, weight: 500

═══════════════════════════════════════════════════════════════════
ELEVATION TOKENS (Shadows)
═══════════════════════════════════════════════════════════════════

  level-0: none
  level-1: 0 1px 2px rgba(0,0,0,0.3), 0 1px 3px rgba(0,0,0,0.15)
  level-2: 0 2px 6px rgba(0,0,0,0.3), 0 2px 4px rgba(0,0,0,0.15)
  level-3: 0 4px 8px rgba(0,0,0,0.3), 0 4px 6px rgba(0,0,0,0.15)
  level-4: 0 6px 10px rgba(0,0,0,0.3), 0 6px 8px rgba(0,0,0,0.15)
  level-5: 0 8px 12px rgba(0,0,0,0.3), 0 8px 10px rgba(0,0,0,0.15)

═══════════════════════════════════════════════════════════════════
BORDER RADIUS TOKENS
═══════════════════════════════════════════════════════════════════

  none: 0px
  xs: 4px     (Small elements)
  sm: 8px     (Buttons, chips)
  md: 12px    (Cards, dialogs)
  lg: 16px    (Large containers)
  xl: 28px    (FABs, prominent elements)
  full: 9999px (Pills, circular)

═══════════════════════════════════════════════════════════════════
USAGE IN CODE
═══════════════════════════════════════════════════════════════════

When generating components, QUERY these tokens:

```python
# Query for primary color
color_tokens = design_kb.query("material design 3 design tokens primary color")
primary_color = extract_token(color_tokens, "primary")  # Returns: #1890ff

# Use in component
background: {primary_color}
```

DO NOT hardcode values like:
  background: #6750A4  # ❌ WRONG - hardcoded
  background: {primary}  # ✅ CORRECT - references token
""",
    "metadata": {"authority": "true", "version": "1.0"}
}


# ==============================================================================
# COMPONENT SPECIFICATIONS - Reference Tokens
# ==============================================================================

M3_TOP_APP_BAR = {
    "id": "m3-top-app-bar-spec",
    "category": "component",
    "title": "Material Design 3 Top App Bar Specification",
    "content": """Material Design 3 Top App Bar

═══════════════════════════════════════════════════════════════════
TYPES AND DIMENSIONS
═══════════════════════════════════════════════════════════════════

1. SMALL (Default for dashboards):
   - Height: 64px
   - Use case: Most applications

2. MEDIUM:
   - Height: 112px
   - Use case: Content-focused apps

3. LARGE:
   - Height: 152px
   - Use case: Marketing, landing pages

FOR DASHBOARDS: Always use SMALL (64px)

═══════════════════════════════════════════════════════════════════
STRUCTURE
═══════════════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────────┐
│ [Icon] Title                              [Action] [Action]   │ 64px
└──────────────────────────────────────────────────────────────┘

REGIONS:
- Leading: Optional navigation icon or logo
- Title: App name or current section
- Trailing: 0-3 action buttons (search, settings, menu)

═══════════════════════════════════════════════════════════════════
COLOR SPECIFICATION
═══════════════════════════════════════════════════════════════════

REFERENCE DESIGN TOKENS (query: "m3 design tokens"):
- Background: {primary}           → #1890ff (blue)
- Text/Icons: {on-primary}        → #FFFFFF (white)
- Box Shadow: {elevation-level-2}

CONTRAST REQUIREMENT:
- Must meet WCAG AA: 4.5:1 minimum contrast ratio
- Between background and text colors

═══════════════════════════════════════════════════════════════════
GRADIO IMPLEMENTATION PATTERN
═══════════════════════════════════════════════════════════════════

```python
# Step 1: Query design tokens
tokens = design_kb.query("material design 3 design tokens")
primary = extract_token(tokens, "primary")         # #1890ff
on_primary = extract_token(tokens, "on-primary")   # #FFFFFF
elevation = extract_token(tokens, "elevation-level-2")

# Step 2: Build Top App Bar
gr.HTML(f'''
<div style="
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
    padding: 0 16px;
    background: {primary};
    color: {on_primary};
    box-shadow: {elevation};
">
    <div style="display: flex; align-items: center; gap: 12px;">
        <svg height="32" width="32" viewBox="0 0 24 24" fill="{on_primary}">
            <path d="M19 3H5c-1.1 0-2 .9-2 2v14..."/>
        </svg>
        <h1 style="margin: 0; font-size: 20px; font-weight: 500; color: {on_primary};">
            App Title
        </h1>
    </div>
    <div style="display: flex; gap: 8px;">
        <!-- Action buttons -->
    </div>
</div>
''')
```

KEY PRINCIPLES:
- NEVER hardcode colors - always query tokens
- Height MUST be 64px for dashboards
- Title uses title-large typography token
- Actions use icon buttons (48x48px touch target)
""",
    "metadata": {"component_type": "app_bar", "references": ["m3-design-tokens-authority"]}
}


M3_NAVIGATION_RAIL = {
    "id": "m3-navigation-rail-spec",
    "category": "component",
    "title": "Material Design 3 Navigation Rail Specification",
    "content": """Material Design 3 Navigation Rail

═══════════════════════════════════════════════════════════════════
DIMENSIONS AND STRUCTURE
═══════════════════════════════════════════════════════════════════

WIDTH:
- Collapsed (default): 80px
- Expanded: 256px (replaces drawer functionality in M3)

HEIGHT:
- Full viewport height
- Persistent (always visible)

CONTENT:
- 3-7 destination buttons (M3 recommendation)
- Optional FAB at top
- Optional menu at bottom

═══════════════════════════════════════════════════════════════════
COLOR SPECIFICATION
═══════════════════════════════════════════════════════════════════

REFERENCE DESIGN TOKENS:
- Background: {surface}                → #FEFBFF
- Border: {outline-variant}            → #CAC4D0
- Active indicator: {secondary-container}
- Active icon: {on-secondary-container}
- Inactive icon: {on-surface-variant}

═══════════════════════════════════════════════════════════════════
GRADIO IMPLEMENTATION PATTERN
═══════════════════════════════════════════════════════════════════

```python
# Query tokens
tokens = design_kb.query("material design 3 design tokens")
surface = extract_token(tokens, "surface")
outline = extract_token(tokens, "outline-variant")

# Navigation Rail
with gr.Column(scale=0, min_width=80):
    gr.HTML(f'''
    <div style="
        width: 80px;
        background: {surface};
        border-right: 1px solid {outline};
        padding: 8px 0;
    ">
        <div style="text-align: center; margin-bottom: 16px;">
            <!-- Logo/Icon -->
        </div>
    </div>
    ''')

    # 3-7 navigation buttons
    nav_home = gr.Button("Home", size="sm", icon="home.svg")
    nav_data = gr.Button("Data", size="sm", icon="database.svg")
    nav_settings = gr.Button("Settings", size="sm", icon="settings.svg")
```

KEY PRINCIPLES:
- Width: 80px (collapsed) - DO NOT CHANGE
- Contains 3-7 destinations (M3 spec)
- Persistent (always visible)
- NO mention of scrollbars (implementation detail, not M3 spec)
""",
    "metadata": {"component_type": "navigation_rail", "references": ["m3-design-tokens-authority"]}
}


def main():
    """Rebuild M3 design system in Pinecone with proper architecture"""

    print("="*70)
    print("REBUILDING M3 DESIGN SYSTEM IN PINECONE")
    print("="*70)
    print()
    print("Architecture:")
    print("  1. Design Tokens (AUTHORITY) - Single source of truth")
    print("  2. Component Specs - Reference tokens, never hardcode")
    print("  3. Clear separation between principles and implementation")
    print()

    kb = DesignKnowledgeBasePinecone()

    documents = [
        ("Design Tokens (Authority)", M3_DESIGN_TOKENS),
        ("Top App Bar Specification", M3_TOP_APP_BAR),
        ("Navigation Rail Specification", M3_NAVIGATION_RAIL),
    ]

    print("Adding documents to Pinecone:")
    print("-" * 70)

    for name, doc in documents:
        try:
            kb.add_guideline(
                guideline_id=doc["id"],
                title=doc["title"],
                content=doc["content"],
                category=doc["category"],
                metadata=doc.get("metadata", {})
            )
            print(f"✓ {name}")
        except Exception as e:
            print(f"✗ {name}: {e}")

    print()
    print("="*70)
    print("VERIFICATION")
    print("="*70)

    # Verify design tokens
    print("\n1. Querying for primary color...")
    results = kb.query("material design 3 primary color design tokens", top_k=1)
    if results:
        content = results[0]['content']
        if '#1890ff' in content:
            print("   ✓ Primary color #1890ff (blue) found")
        if 'primary: #1890ff' in content:
            print("   ✓ Formatted as token: 'primary: #1890ff'")
        if '#6750A4' not in content:
            print("   ✓ No purple #6750A4 in design tokens")
        else:
            print("   ✗ WARNING: Purple still present")

    # Verify Top App Bar references tokens
    print("\n2. Querying Top App Bar spec...")
    results = kb.query("material design 3 top app bar", top_k=1)
    if results:
        content = results[0]['content']
        has_reference = '{primary}' in content or 'query' in content.lower() or 'reference design tokens' in content.lower()
        has_hardcode = '#6750A4' in content or '#1890ff' in content

        if has_reference:
            print("   ✓ Top App Bar references design tokens")
        if not has_hardcode:
            print("   ✓ No hardcoded colors in Top App Bar spec")
        else:
            print("   ✗ WARNING: Hardcoded colors still present")

    print()
    print("="*70)
    print("NEXT STEPS")
    print("="*70)
    print("1. Update component_assembler_v3.py to query colors from Pinecone")
    print("2. Add principle consistency tests")
    print("3. Regenerate dashboard with query-based colors")
    print("4. User can now change colors by updating ONE document in Pinecone")
    print()


if __name__ == "__main__":
    main()
