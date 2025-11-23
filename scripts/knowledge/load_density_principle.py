"""
Load density and information architecture principles into Pinecone
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.knowledge.design_kb_pinecone import DesignKnowledgeBasePinecone as DesignKnowledgeBase

# Material Design 3 Density Principle
density_principle = {
    "id": "material-design-density",
    "title": "Material Design 3: Density & Information Architecture",
    "category": "density",
    "content": """
# Material Design 3: Density & Information Architecture

## Density Levels
Material Design supports 3 density levels for dashboard layouts:
- **Default (-0)**: Standard spacing, comfortable for most users
- **Comfortable (-1)**: Slightly reduced spacing (recommended for dashboards)
- **Compact (-2)**: Minimal spacing, maximum information density

## Dashboard Density Guidelines
For data-heavy dashboards showing multiple cards:

1. **Reduce vertical spacing**: Use 8px-12px margins instead of 16px-24px
2. **Compact padding**: Use 16px padding in cards instead of 24px
3. **Tighter typography**: Reduce line-height to 1.2-1.4
4. **Remove redundant spacing**: Header margins should be 0-8px
5. **Grid layout**: Use CSS Grid with gap: 12px for efficient space usage

## Compact Card Style
```css
.compact-card {
    padding: 16px;           /* Instead of 24px */
    margin: 8px 0;           /* Instead of 16px */
    border-radius: 6px;      /* Slightly smaller */
}
```

## Typography Hierarchy (Compact)
- Page title: 24px (reduced from 34px)
- Section heading: 16px (reduced from 20px)
- Card title: 18px (reduced from 20px)
- Body text: 14px
- Small labels: 11px

## Information Density Best Practices
- **Viewport optimization**: Fit primary content in 1280x800 without scrolling
- **Horizontal space**: Use multi-column layouts (Grid) to maximize width
- **Visual hierarchy**: Use size/weight differences, not spacing
- **Remove decorative elements**: Focus on data, not chrome

## Example: Compact Dashboard Layout
```html
<div style="max-width: 100%; padding: 12px;">
    <h1 style="font-size: 24px; margin: 0 0 12px 0;">Dashboard</h1>

    <!-- KPI Row: Compact cards in Grid -->
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px;">
        <div style="padding: 16px; background: white; border-radius: 6px;">
            <div style="font-size: 11px; color: #666;">METRIC</div>
            <div style="font-size: 32px; font-weight: 700; line-height: 1.2;">1,234</div>
        </div>
    </div>

    <!-- Data cards: 2-3 per row depending on content -->
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
        <div style="padding: 16px; background: white; border-radius: 6px;">
            Card content
        </div>
    </div>
</div>
```

## Key Metrics for Density
- **Default**: ~40-50% screen utilization
- **Comfortable**: ~60-70% screen utilization
- **Compact**: ~80-90% screen utilization (recommended for dashboards)
"""
}

if __name__ == '__main__':
    kb = DesignKnowledgeBase()

    print("Loading density principle into Pinecone...")
    kb.add_pattern(
        pattern_id=density_principle['id'],
        title=density_principle['title'],
        content=density_principle['content'],
        category=density_principle['category']
    )

    print(f"[OK] Loaded: {density_principle['title']}")

    # Verify
    results = kb.query("dashboard density compact layout", category="density", top_k=1)
    if results:
        print(f"\n[Verified] Found principle with score: {results[0].get('score', 0):.2f}")
    else:
        print("[WARNING] Could not verify - principle may not be in index yet")
