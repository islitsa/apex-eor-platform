"""
Dashboard Builder - Template-based code generator
Generates REAL Gradio components (gr.Button) instead of HTML strings
This allows proper event handling and navigation

Note: This is NOT an agent - it's a deterministic template-based builder.
It queries design principles from Pinecone but uses string templates, not LLM reasoning.
"""

from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime
import json
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.knowledge.design_kb_pinecone import DesignKnowledgeBasePinecone


class DashboardBuilder:
    """
    Template-based dashboard generator that queries design principles from Pinecone
    - Uses gr.Button() instead of HTML <span> for buttons
    - Places navigation placeholder for LLM-generated code
    - All components and handlers stay inside gr.Blocks context
    """

    def __init__(self):
        # Connect to design principles in Pinecone
        try:
            self.design_kb = DesignKnowledgeBasePinecone()
            print("[DashboardBuilder] Connected to design principles database")
        except Exception as e:
            print(f"[DashboardBuilder] WARNING: Could not connect to design KB: {e}")
            self.design_kb = None

    def _query_color_token(self, token_name: str) -> str:
        """
        Query specific color token from M3 Design Tokens in Pinecone.
        This makes colors truly RAG-based instead of hardcoded.

        Args:
            token_name: Name of the token (e.g., "primary", "on-primary", "surface")

        Returns:
            Hex color value (e.g., "#1890ff")
        """
        if not self.design_kb:
            # Fallback to M3 defaults if Pinecone unavailable
            defaults = {
                "primary": "#1890ff",
                "on-primary": "#FFFFFF",
                "surface": "#FEFBFF",
                "outline-variant": "#CAC4D0"
            }
            return defaults.get(token_name, "#000000")

        # Query the authoritative design tokens document
        results = self.design_kb.query(
            f"material design 3 design tokens {token_name}",
            category="design-tokens",
            top_k=1
        )

        if results:
            content = results[0]['content']
            # Extract color value: "primary: #1890ff"
            import re
            pattern = rf'{token_name}:\s*(#[0-9A-Fa-f]{{6}})'
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                color = match.group(1)
                print(f"  [Color Token] {token_name}: {color}")
                return color

        # Fallback if not found
        print(f"  [Color Token] {token_name}: Using default")
        defaults = {
            "primary": "#1890ff",
            "on-primary": "#FFFFFF",
            "surface": "#FEFBFF",
            "outline-variant": "#CAC4D0"
        }
        return defaults.get(token_name, "#000000")

    def _query_design_principles(self) -> Dict[str, Any]:
        """
        Query Pinecone for design principles BEFORE generating any components
        Following RAG-first approach
        """
        if not self.design_kb:
            return {}

        print("[DashboardBuilder] Querying design principles from Pinecone...")

        principles = {}

        # Query typography
        typo_results = self.design_kb.query(
            "typography font size hierarchy dashboard metrics",
            category="typography",
            top_k=2
        )
        if typo_results:
            principles['typography'] = typo_results[0]
            print(f"  [Design] Typography: {typo_results[0]['title'][:60]}")

        # Query spacing
        spacing_results = self.design_kb.query(
            "8px grid spacing padding margin",
            category="spacing",
            top_k=2
        )
        if spacing_results:
            principles['spacing'] = spacing_results[0]
            print(f"  [Design] Spacing: {spacing_results[0]['title'][:60]}")

        # Query colors
        color_results = self.design_kb.query(
            "color palette status indicators",
            category="colors",
            top_k=2
        )
        if color_results:
            principles['colors'] = color_results[0]
            print(f"  [Design] Colors: {color_results[0]['title'][:60]}")

        # Query M3 structural layout patterns (App Bar + Navigation Rail + Body)
        layout_results = self.design_kb.query(
            "material design 3 app structure navigation rail body persistent",
            category="layout",
            top_k=2
        )
        if layout_results:
            principles['layout'] = layout_results[0]
            print(f"  [Design] Layout: {layout_results[0]['title'][:60]}")

        print(f"[DashboardBuilder] Retrieved {len(principles)} design principles")
        return principles

    def assemble(self, context: Dict[str, Any]) -> str:
        """
        DEPRECATED: Use build() instead
        Kept for backwards compatibility with existing code
        """
        import warnings
        warnings.warn(
            "assemble() is deprecated. Use build() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.build(context)

    def build(self, context: Dict[str, Any]) -> str:
        """
        Generate complete dashboard code with proper Gradio components

        Args:
            context: Dictionary containing data sources, metrics, etc.

        Returns:
            Complete Python code string for Gradio dashboard
        """

        print("[DashboardBuilder] Generating dashboard with real Gradio components...")

        # STEP 1: Query design principles FIRST (RAG-first approach)
        design_principles = self._query_design_principles()

        # STEP 1.5: Query M3 color tokens from Pinecone (RAG-based colors!)
        print("[DashboardBuilder] Querying M3 color tokens from Pinecone...")
        primary_color = self._query_color_token("primary")
        on_primary_color = self._query_color_token("on-primary")
        surface_color = self._query_color_token("surface")
        outline_color = self._query_color_token("outline-variant")

        # STEP 2: Extract data from context
        data_sources_dict = context.get('data_sources', {})
        metrics = context.get('metrics', {})

        # Convert dict to list for easier processing
        sources = []
        for source_name, source_data in data_sources_dict.items():
            sources.append({
                'source': source_name,
                'datasets': list(source_data.get('datasets', {}).values()),
                'pipeline_stages_used': source_data.get('pipeline_stages_used', []),
                'processing_notes': source_data.get('processing_notes', {})
            })

        # Calculate summary metrics from context
        total_records = metrics.get('total_records', 0)
        total_size_bytes = metrics.get('total_size_bytes', 0)
        total_size_gb = total_size_bytes / (1024**3)  # Convert bytes to GB
        total_datasets = metrics.get('total_datasets', 0)

        # Generate the dashboard code
        dashboard_code = f'''"""
Auto-generated Pipeline Dashboard with Gradio Components
Generated at: {datetime.now().isoformat()}
"""
import gradio as gr
import json
from pathlib import Path
from datetime import datetime

def create_dashboard():
    """Create pipeline dashboard with proper Gradio components for navigation"""

    base_path = Path("data/raw")

    # Custom CSS to hide Navigation Rail scrollbar
    custom_css = """
    /* Hide scrollbar on Navigation Rail column */
    .nav-rail-column {{
        overflow: hidden !important;
        max-height: 100vh !important;
    }}
    .nav-rail-column > div {{
        overflow: hidden !important;
    }}
    """

    with gr.Blocks(theme=gr.themes.Soft(), title="Pipeline Dashboard", css=custom_css) as demo:

        # Hidden components for navigation state
        nav_state = gr.State({{"current_path": [], "current_view": "sources"}})

        # M3 LAYOUT STRUCTURE: Top App Bar + (Navigation Rail + Body)

        # 1. TOP APP BAR (M3 Header Region) - Colors queried from Pinecone!
        gr.HTML(f\'\'\'
        <div style="
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 64px;
            padding: 0 16px;
            background: {primary_color};
            color: {on_primary_color};
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="display: flex; align-items: center; gap: 12px;">
                <svg xmlns="http://www.w3.org/2000/svg" height="32" width="32" viewBox="0 0 24 24" fill="{on_primary_color}" style="margin-right: 8px;">
                    <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
                </svg>
                <h1 style="margin: 0; font-size: 20px; font-weight: 500; color: {on_primary_color};">Petroleum Data Pipeline</h1>
            </div>
            <div style="font-size: 13px; color: {on_primary_color}; opacity: 0.9;">{len(sources)} sources • {total_records:,} records • {total_size_gb:.2f} GB</div>
        </div>
        \'\'\')

        # 2. NAVIGATION RAIL + BODY LAYOUT (M3 Structure)
        with gr.Row():
            # 2A. NAVIGATION RAIL (M3 Persistent Side Navigation) - Colors queried from Pinecone!
            with gr.Column(scale=0, min_width=80, elem_classes="nav-rail-column"):
                gr.HTML(f\'\'\'
                <div style="
                    width: 80px;
                    background: {surface_color};
                    padding: 8px 0;
                    border-right: 1px solid {outline_color};
                    overflow: hidden;
                ">
                    <div style="text-align: center; margin-bottom: 12px; font-size: 10px; color: #666; font-weight: 600; letter-spacing: 0.5px;">SECTIONS</div>
                </div>
                \'\'\')

                # Navigation buttons (3-7 destinations per M3 spec) with M3 icons
                nav_home = gr.Button("Home", size="sm", variant="primary", icon="https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/home/default/24px.svg")
                nav_sources = gr.Button("Data", size="sm", icon="https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/database/default/24px.svg")
                nav_logs = gr.Button("Logs", size="sm", icon="https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/description/default/24px.svg")

            # 2B. BODY REGION (M3 Main Content) - Takes remaining space
            with gr.Column(scale=1):
                # Breadcrumbs (M3 pattern - top of body)
                breadcrumb_display = gr.HTML(\'\'\'
                <div style="
                    padding: 12px 16px;
                    font-size: 13px;
                    color: #79747E;
                    border-bottom: 1px solid #e0e0e0;
                    background: #fafafa;
                ">
                    <strong style="color: #1a1a1a;">Home</strong>
                </div>
                \'\'\')

                # Content area (swaps out - KPIs + Data Sources)
                content_area = gr.Column()

                with content_area:
                    # KPI Grid - CSS Grid for tight spacing
                    gr.HTML(f\'\'\'
                    <div style="padding: 16px;">
                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 16px;">
                            <div style="padding: 12px; text-align: center; background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.12);">
                                <div style="font-size: 9px; text-transform: uppercase; letter-spacing: 0.5px; color: #666; font-weight: 600; margin-bottom: 4px;">RECORDS</div>
                                <div style="font-size: 28px; font-weight: 700; color: #1a1a1a; font-variant-numeric: tabular-nums; line-height: 1;">{total_records:,}</div>
                            </div>
                            <div style="padding: 12px; text-align: center; background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.12);">
                                <div style="font-size: 9px; text-transform: uppercase; letter-spacing: 0.5px; color: #666; font-weight: 600; margin-bottom: 4px;">SIZE</div>
                                <div style="font-size: 28px; font-weight: 700; color: #1a1a1a; font-variant-numeric: tabular-nums; line-height: 1;">{total_size_gb:.2f} GB</div>
                            </div>
                            <div style="padding: 12px; text-align: center; background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.12);">
                                <div style="font-size: 9px; text-transform: uppercase; letter-spacing: 0.5px; color: #666; font-weight: 600; margin-bottom: 4px;">SOURCES</div>
                                <div style="font-size: 28px; font-weight: 700; color: #1a1a1a; font-variant-numeric: tabular-nums; line-height: 1;">{len(sources)}</div>
                            </div>
                            <div style="padding: 12px; text-align: center; background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.12);">
                                <div style="font-size: 9px; text-transform: uppercase; letter-spacing: 0.5px; color: #666; font-weight: 600; margin-bottom: 4px;">DATASETS</div>
                                <div style="font-size: 28px; font-weight: 700; color: #1a1a1a; font-variant-numeric: tabular-nums; line-height: 1;">{total_datasets}</div>
                            </div>
                        </div>
                    </div>
                    \'\'\')

                    # Data Sources section header
                    gr.HTML(f\'\'\'
                    <div style="padding: 0 16px; margin: 8px 0;">
                        <div style="display: flex; align-items: center;">
                            <svg xmlns="http://www.w3.org/2000/svg" height="20" width="20" viewBox="0 0 24 24" fill="#666" style="margin-right: 6px;">
                                <path d="M20 6h-2.18c.11-.31.18-.65.18-1 0-1.66-1.34-3-3-3-1.05 0-1.96.54-2.5 1.35l-.5.67-.5-.68C10.96 2.54 10.05 2 9 2 7.34 2 6 3.34 6 5c0 .35.07.69.18 1H4c-1.11 0-1.99.89-1.99 2L2 19c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2zm-5-2c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zM9 4c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm11 15H4v-2h16v2zm0-5H4V8h5.08L7 10.83 8.62 12 11 8.76l1-1.36 1 1.36L15.38 12 17 10.83 14.92 8H20v6z"/>
                            </svg>
                            <h2 style="font-size: 15px; font-weight: 600; margin: 0; color: #1a1a1a;">Data Sources <span style="font-size: 12px; font-weight: 400; color: #666;">({len(sources)})</span></h2>
                        </div>
                    </div>
                    \'\'\')

                    # Store button references for navigation wiring
                    source_buttons = {{}}

                    # Data source cards grid
                    with gr.Row():
'''

        # Generate source cards with proper Gradio components
        for source_data in sources:
            source_name = source_data.get('source', 'Unknown')
            safe_name = source_name.replace(' ', '_').replace('-', '_').lower()

            dashboard_code += self._generate_source_card_with_gradio_buttons(
                source_data,
                safe_name
            )

        # Add nav_output component INSIDE content_area
        dashboard_code += '''
                    # Navigation output area INSIDE content_area (for displaying View results)
                    nav_output = gr.HTML(value="", visible=True, elem_id="navigation-output")
'''

        # Close the Row
        dashboard_code += "\n"

        # Add placeholder for navigation handlers (will be filled by UX generator agent)
        dashboard_code += '''
        # === NAVIGATION_HANDLER_PLACEHOLDER ===
        # UXCodeGenerator agent will inject navigation code here
        # This placeholder ensures code is injected inside gr.Blocks context

    return demo

if __name__ == "__main__":
    demo = create_dashboard()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7867,
        share=False
    )
'''

        print(f"[DashboardBuilder] Generated {len(dashboard_code):,} chars")
        print(f"[DashboardBuilder] Sources: {len(sources)}, Datasets: {total_datasets}")

        return dashboard_code

    def _generate_source_card_with_gradio_buttons(self, source_data: Dict, safe_name: str) -> str:
        """
        Generate Gradio components for a source card
        Uses actual gr.Button components that can have click handlers

        Key design: Use gr.Button() instead of HTML <span>
        """

        source_name = source_data.get('source', 'Unknown')
        datasets = source_data.get('datasets', [])

        # Calculate totals for this source from pipeline stages
        total_records = 0
        total_size_bytes = 0

        for dataset in datasets:
            # Check parsed stage first, then extracted, then downloads
            pipeline_stages = dataset.get('pipeline_stages', {})
            for stage_name in ['parsed', 'extracted', 'downloads']:
                stage = pipeline_stages.get(stage_name, {})
                if stage.get('status') == 'complete':
                    total_records += stage.get('total_rows', 0)
                    total_size_bytes += stage.get('total_size_bytes', 0)
                    break  # Use the most processed stage available

        total_size = total_size_bytes / (1024**2)  # MB

        if total_size > 1024:
            size_str = f"{total_size/1024:.2f} GB"
        elif total_size == 0:
            size_str = "No data"
        else:
            size_str = f"{total_size:.2f} MB"

        # Determine status - Use Material Design SVG icon instead of emoji
        if not datasets or total_records == 0:
            status_icon = '<svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 24 24" fill="#8c8c8c"><circle cx="12" cy="12" r="8"/></svg>'
            status_text = "Discovered"
            status_color = "#8c8c8c"
            records_str = "No data"
        else:
            status_icon = '<svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 24 24" fill="#4caf50"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>'
            status_text = "Ready"
            status_color = "#4caf50"
            records_str = f"{total_records:,}"

        # Get pipeline stages - Use SVG checkmarks (M3 Status Indicators)
        pipeline_stages_used = source_data.get('pipeline_stages_used', [])
        if pipeline_stages_used:
            # M3 checkmark SVG icon
            checkmark_svg = '<svg xmlns="http://www.w3.org/2000/svg" height="12" width="12" viewBox="0 0 24 24" fill="#4caf50" style="display: inline; vertical-align: middle; margin-right: 2px;"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>'
            stage_labels = []
            for stage in pipeline_stages_used:
                stage_labels.append(f'{checkmark_svg}{stage.title()}')
            stages_display = ' <span style="margin: 0 4px;">→</span> '.join(stage_labels)
        else:
            stages_display = "Not started"

        # Inline styles - MAXIMUM DENSITY (12px padding, tight spacing)
        card_style = "padding: 12px; background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); margin: 0;"
        title_style = "font-size: 16px; font-weight: 600; color: #1a1a1a; margin-bottom: 6px; line-height: 1.2;"
        metric_label_style = "font-size: 9px; text-transform: uppercase; color: #666; font-weight: 600;"
        metric_value_style = "font-size: 13px; font-weight: 600; color: #1a1a1a; margin: 2px 0; line-height: 1.3;"

        return f'''
                        with gr.Column(scale=1):
                            # Source card - COMPACT with Material Design icon
                            gr.HTML(f\'\'\'
                    <div style="{card_style}">
                        <div style="{title_style}">{source_name}</div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div style="display: flex; align-items: center; gap: 4px;">
                                {status_icon}
                                <span style="font-size: 12px; color: {status_color}; font-weight: 600;">{status_text}</span>
                            </div>
                            <span style="{metric_label_style}">{len(datasets)} DATASETS</span>
                        </div>
                        <div style="margin-bottom: 6px;">
                            <div style="{metric_label_style}">RECORDS</div>
                            <div style="{metric_value_style}">{records_str}</div>
                        </div>
                        <div style="margin-bottom: 8px;">
                            <div style="{metric_label_style}">SIZE</div>
                            <div style="{metric_value_style}">{size_str}</div>
                        </div>
                        <div style="margin: 8px 0 0 0; font-size: 11px; color: #6c757d; border-top: 1px solid #e0e0e0; padding-top: 8px;">
                            {stages_display}
                        </div>
                    </div>
                            \'\'\')

                            # Action buttons - REAL Gradio components (KEY DESIGN!)
                            with gr.Row():
                                view_btn_{safe_name} = gr.Button("View", size="sm", variant="primary")
                                download_btn_{safe_name} = gr.Button("Download", size="sm", variant="secondary")
                                rerun_btn_{safe_name} = gr.Button("Re-run", size="sm", variant="secondary")

                                # Store button reference for navigation wiring
                                source_buttons['{source_name}'] = {{
                                    'view': view_btn_{safe_name},
                                    'download': download_btn_{safe_name},
                                    'rerun': rerun_btn_{safe_name},
                                    'safe_name': '{safe_name}',
                                    'datasets': {json.dumps([d.get('name', 'Unknown') for d in datasets])}
                                }}

'''


# For backwards compatibility - keep old name as alias
ComponentBasedAssembler = DashboardBuilder


if __name__ == '__main__':
    # Test the builder
    from src.analyzers.pipeline_context_analyzer import PipelineContextAnalyzer

    print("Testing DashboardBuilder...")

    # Generate context
    print("\n[1/2] Auto-discovering context...")
    analyzer = PipelineContextAnalyzer()
    context = analyzer.analyze_filesystem()

    # Generate dashboard
    print("\n[2/2] Generating dashboard with Gradio components...")
    builder = DashboardBuilder()
    dashboard_code = builder.build(context)

    # Save for inspection
    output_path = project_root / "generated_dashboard.py"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(dashboard_code)

    print(f"\n[DONE] Dashboard saved: {output_path}")
    print(f"[DONE] Size: {len(dashboard_code):,} chars")
    print("\nCheck for:")
    print("  - gr.Button() components (not HTML spans)")
    print("  - NAVIGATION_HANDLER_PLACEHOLDER for injection")
    print("  - source_buttons dictionary with button references")
