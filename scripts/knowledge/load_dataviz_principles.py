"""
Load Data-to-Visualization Matching Principles into Pinecone
Based on Opus's guidance: Different data types need different visualizations
"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.knowledge.design_kb_pinecone import DesignKnowledgeBasePinecone

# Data-to-Viz Matching Principles (Opus's Vision)
DATAVIZ_PRINCIPLES = [
    {
        "id": "viz-for-pipeline-flow",
        "title": "Pipeline Stages Visualization",
        "category": "principle",
        "content": """
DATA TYPE: Sequential Pipeline Stages
DATA CHARACTERISTICS:
- Nature: linear_process
- Stages: [download, extract, parse]
- Relationship: sequential
- NOT showing flow quantities

APPROPRIATE VISUALIZATIONS:
1. Horizontal Flow Diagram - Simple boxes with arrows
2. Chevron Progress - Stepped progress indicator
3. Stepped Progress Bar - Linear progress with labels
4. Pipeline Diagram - Boxes connected with arrows

INAPPROPRIATE VISUALIZATIONS:
1. Sankey Diagram - Sankey is for FLOW QUANTITIES between nodes (e.g., "100GB -> 50GB dataset A, 30GB dataset B")
2. Network Graph - Network is for complex relationships, not linear flow
3. Pie Chart - Pie is for parts of whole, not stages

WHY SANKEY IS WRONG:
- User rated 1/5: "I hate the new pipeline vis"
- Sankey shows quantity distribution across paths
- Our pipeline has NO branching quantities
- We're showing STATUS, not FLOW VOLUME

GRADIO IMPLEMENTATION:
```python
# Beautiful simple pipeline flow
with gr.Row():
    gr.HTML('''
    <div style="display: flex; align-items: center; justify-content: space-between; padding: 20px; background: white; border-radius: 8px;">
        <div style="flex: 1; text-align: center; padding: 12px; background: #10b981; color: white; border-radius: 6px; font-weight: 600;">
            ✓ Download
        </div>
        <div style="padding: 0 10px; color: #6b7280; font-size: 20px;">→</div>
        <div style="flex: 1; text-align: center; padding: 12px; background: #10b981; color: white; border-radius: 6px; font-weight: 600;">
            ✓ Extract
        </div>
        <div style="padding: 0 10px; color: #6b7280; font-size: 20px;">→</div>
        <div style="flex: 1; text-align: center; padding: 12px; background: #10b981; color: white; border-radius: 6px; font-weight: 600;">
            ✓ Parse
        </div>
        <div style="padding: 0 10px; color: #6b7280; font-size: 20px;">→</div>
        <div style="flex: 1; text-align: center; padding: 12px; background: #2563eb; color: white; border-radius: 6px; font-weight: 600;">
            ✅ Ready
        </div>
    </div>
    ''')
```

USER FEEDBACK: Simple boxes rated MUCH higher than complex Sankey
        """,
        "rating": 5.0
    },

    {
        "id": "viz-for-dataset-status",
        "title": "Multi-Entity Status Visualization",
        "category": "principle",
        "content": """
DATA TYPE: Multi-Entity Status Monitoring
DATA CHARACTERISTICS:
- Nature: categorical_status
- Entities: multiple_datasets (6+ sources)
- Metrics per entity: [size, records, status]
- Task: comparison and monitoring
- NOT showing flow or relationships

APPROPRIATE VISUALIZATIONS:
1. Card Grid - Individual cards for each entity (USER RATED 4/5)
2. Status Dashboard - Grouped status indicators
3. Comparison Table - Tabular comparison with sorting
4. Grouped Bar Chart - For metric comparison

INAPPROPRIATE VISUALIZATIONS:
1. Sankey - NOT showing flow between datasets
2. Line Chart - NOT time series data
3. Scatter Plot - NOT showing correlation
4. Network Graph - NOT showing relationships

WHY CARDS ARE BEST:
- Each dataset is independent entity
- Status + metrics clearly visible
- Actions (View, Download, Re-run) per entity
- User rated 4/5 for card layout

GRADIO IMPLEMENTATION: See component-sor-card-html-v2

USER FEEDBACK: Cards > Accordions (4/5 vs 1/5)
        """,
        "rating": 5.0
    },

    {
        "id": "when-to-use-sankey",
        "title": "When Sankey Diagrams Are Appropriate",
        "category": "principle",
        "content": """
DATA TYPE: Flow Quantities with Distribution
DATA CHARACTERISTICS:
- Nature: quantitative_flow
- Requirement: showing quantity distribution across paths
- Example: "100GB total flows to 3 datasets: 50GB, 30GB, 20GB"
- Has branching with DIFFERENT quantities per branch

APPROPRIATE USE CASES:
1. Budget Allocation - "$1M -> $500K dept A, $300K dept B, $200K dept C"
2. Energy Flow - "1000 kWh -> 600 kWh heating, 300 kWh lighting, 100 kWh other"
3. Data Transformation Losses - "1M records -> 800K valid, 150K errors, 50K duplicates"
4. Multi-Stage Filtering - Showing quantity reduction at each filter

NOT APPROPRIATE FOR:
1. Simple pipeline stages (YOUR CASE!) - No branching quantities
2. Status monitoring - Not showing flow
3. Entity comparison - Not showing distribution
4. Linear processes - No quantity splits

DETECTION RULE:
if data has "stages" but NOT "quantity_per_path":
    DO NOT use Sankey
    Use simple flow diagram instead

USER FEEDBACK: "I hate the Sankey pipeline vis" (1/5 rating)
        """,
        "rating": 5.0
    },

    {
        "id": "beautiful-pipeline-dashboard-layout",
        "title": "Pipeline Monitoring Dashboard Layout Pattern",
        "category": "pattern",
        "content": """
DATA TYPE: Petroleum Pipeline Monitoring Dashboard
TASK: Real-time status monitoring and control

DESIGN SYSTEM:
Colors:
- Primary: #2563eb (Blue)
- Success: #10b981 (Green)
- Warning: #f59e0b (Amber)
- Danger: #ef4444 (Red)
- Neutral: #6b7280 (Gray)

Typography:
- Headers: 24px bold
- Metrics: 36px monospace
- Labels: 14px regular gray

Spacing: 8px grid system

LAYOUT PATTERN:
1. Top KPIs (4 metric cards in row)
   - Total Records
   - Data Volume (GB)
   - Ready Datasets
   - Pipeline Status

2. Pipeline Flow Visualization
   - Horizontal stepped flow
   - Status colors (green=complete, blue=active)
   - Simple boxes with arrows (NOT Sankey)

3. Dataset Grid (2x3 or 3x2 cards)
   - Card per source
   - Status indicator (color + icon)
   - Key metrics (records, size)
   - Pipeline stages (Download → Extract → Parse)
   - Action buttons (View, Download, Re-run)

4. Control Panel (bottom)
   - Primary actions (Run Pipeline button)
   - Filters (select datasets)
   - Secondary actions (Download All, Refresh)

USER VALIDATION: This layout received positive feedback after fixing Sankey issue
        """,
        "rating": 4.0
    },

    {
        "id": "data-analysis-to-viz-selection",
        "title": "Algorithm: Data Analysis to Viz Selection",
        "category": "algorithm",
        "content": """
STEP 1: Analyze Data Structure
1. Count entities (sources, datasets, records)
2. Identify metrics per entity
3. Check for relationships (hierarchy, network, flow)
4. Check for time series
5. Identify user task (monitoring, analysis, exploration, control)

STEP 2: Query Pinecone for Matching Viz Principles
Query: "Data type: [type], Task: [task], Has flow: [bool]"
Filter: category=principle, appropriate_for=[task]

STEP 3: Score Each Visualization Option
Scoring Rules:
- Perfect data type match: +50 points
- Task match: +30 points
- User rated highly (4-5 stars): +20 points
- Listed in "inappropriate_for": -100 points
- Sankey without flow data: -200 points

STEP 4: Select Highest Scored Visualization
Return gradio_implementation from top-scored principle

EXAMPLE FOR PIPELINE DASHBOARD:
Data Analysis:
- Type: multi_entity_status
- Task: monitoring
- Entities: 6 sources
- Has flow: FALSE
- Has time_series: FALSE

Viz Scores:
- card_grid: 100 (type match + task match + user rating)
- sankey: -150 (inappropriate - no flow data)
- simple_flow: 80 (task match + appropriate)

Result: Use card_grid for datasets, simple_flow for pipeline stages
        """,
        "rating": 5.0
    },

    {
        "id": "user-feedback-viz-lessons",
        "title": "User Feedback: Visualization Lessons Learned",
        "category": "principle",
        "content": """
LESSON 1: Sankey for Pipeline Stages
- User rating: 1/5
- Feedback: "The pipeline interactive vis is the weirdest pipeline vis I have ever seen"
- Issue: Used Sankey for simple sequential stages without flow quantities
- Fix: Use simple horizontal boxes with arrows

LESSON 2: Cards vs Accordions for SOR
- Cards rating: 4/5
- Accordions rating: 1/5
- Feedback: "I hate the new SOR cards, the old ones were BETTER"
- Issue: Changed from cards to accordions
- Fix: Use card grid layout, NOT accordions

LESSON 3: Pipeline Stages Must Be Visible
- Feedback: "for each SOR we have 3 steps: download, extract, parsed - why is that not being displayed?"
- Issue: Not showing Download → Extract → Parse stages per source
- Fix: Include pipeline stages indicator in each card

LESSON 4: Functional vs Visual Buttons
- Feedback: "We needed those buttons that didn't work yet"
- Issue: Removed buttons because they weren't functional
- Fix: Include visual buttons with disclaimer, don't remove them

RULE: User feedback overrides design theory
If user rates something 4/5, USE IT
If user rates something 1/5, NEVER USE IT
        """,
        "rating": 5.0
    }
]

def load_dataviz_principles():
    """Load data-to-viz matching principles into Pinecone"""

    print("=" * 70)
    print("LOADING DATA-TO-VISUALIZATION MATCHING PRINCIPLES")
    print("=" * 70)

    # Connect to Pinecone
    kb = DesignKnowledgeBasePinecone()

    # Store each principle
    print(f"\nStoring {len(DATAVIZ_PRINCIPLES)} visualization principles...")
    for principle in DATAVIZ_PRINCIPLES:
        kb.add_guideline(
            guideline_id=principle['id'],
            title=principle['title'],
            content=principle['content'],
            category=principle['category'],
            metadata={'rating': principle.get('rating', 3.0)}
        )
        print(f"  [OK] {principle['title']}")

    print(f"\n[OK] All {len(DATAVIZ_PRINCIPLES)} principles loaded successfully!")
    print("\nPrinciples cover:")
    print("  - Pipeline flow visualization (NOT Sankey)")
    print("  - Dataset status visualization (cards, not accordions)")
    print("  - When Sankey IS appropriate (flow quantities)")
    print("  - Dashboard layout patterns")
    print("  - Data-to-viz selection algorithm")
    print("  - User feedback lessons")

    print("\n" + "=" * 70)

if __name__ == '__main__':
    load_dataviz_principles()
