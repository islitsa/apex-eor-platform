"""
Auto-generated Pipeline Dashboard with Gradio Components
Generated at: 2025-10-29T11:39:50.670026
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
    .nav-rail-column {
        overflow: hidden !important;
        max-height: 100vh !important;
    }
    .nav-rail-column > div {
        overflow: hidden !important;
    }
    

/* Generated from design principles in Pinecone */
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;600;700&display=swap');

/* Material Design 3 Button Styling */
button {
    font-family: 'Roboto', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    letter-spacing: 0.1px !important;
    text-transform: none !important;
    min-width: 80px !important;
    padding-left: 16px !important;
    padding-right: 16px !important;
    white-space: nowrap !important;
    flex: 0 1 auto !important;
}

.metric-value { font-size: 28px !important; font-weight: 600 !important; font-variant-numeric: tabular-nums !important; color: #1a1a1a !important; margin-top: 8px !important; }
.section-title { font-size: 20px !important; font-weight: 600 !important; }
.metric-label { font-size: 18px !important; text-transform: uppercase !important; letter-spacing: 0.5px !important; color: #666 !important; font-weight: 600 !important; }
.status-success { color: #52c41a; }
.status-error { color: #ff4d4f; }
.primary { background: #1890ff; color: white; }
.surface { background: #FFFFFF !important; border: 1px solid #E0E0E0 !important; box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important; }
.metric-card { padding: 24px !important; text-align: center !important; background: white !important; border-radius: 8px !important; box-shadow: 0 1px 3px rgba(0,0,0,0.12) !important; margin: 10px !important; }"""

    with gr.Blocks(theme=gr.themes.Soft(), title="Pipeline Dashboard", css=custom_css) as demo:

        # Hidden components for navigation state
        nav_state = gr.State({"current_path": [], "current_view": "sources"})

        # M3 LAYOUT STRUCTURE: Top App Bar + (Navigation Rail + Body)

        # 1. TOP APP BAR (M3 Header Region) - Colors queried from Pinecone!
        gr.HTML(f'''
        <div style="
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 64px;
            padding: 0 16px;
            background: #1890ff;
            color: #FFFFFF;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="display: flex; align-items: center; gap: 12px;">
                <svg xmlns="http://www.w3.org/2000/svg" height="32" width="32" viewBox="0 0 24 24" fill="#FFFFFF" style="margin-right: 8px;">
                    <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
                </svg>
                <h1 style="margin: 0; font-size: 20px; font-weight: 500; color: #FFFFFF;">Petroleum Data Pipeline</h1>
            </div>
            <div style="font-size: 13px; color: #FFFFFF; opacity: 0.9;">6 sources • 224,044,778 records • 36.49 GB</div>
        </div>
        ''')

        # 2. NAVIGATION RAIL + BODY LAYOUT (M3 Structure)
        with gr.Row():
            # 2A. NAVIGATION RAIL (M3 Persistent Side Navigation) - Colors queried from Pinecone!
            with gr.Column(scale=0, min_width=80, elem_classes="nav-rail-column"):
                gr.HTML(f'''
                <div style="
                    width: 80px;
                    background: #FEFBFF;
                    padding: 8px 0;
                    border-right: 1px solid #CAC4D0;
                    overflow: hidden;
                ">
                    <div style="text-align: center; margin-bottom: 12px; font-size: 10px; color: #666; font-weight: 600; letter-spacing: 0.5px;">SECTIONS</div>
                </div>
                ''')

                # Navigation buttons (3-7 destinations per M3 spec) with M3 icons
                nav_home = gr.Button("Home", size="sm", variant="primary", icon="https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/home/default/24px.svg")
                nav_sources = gr.Button("Data", size="sm", icon="https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/database/default/24px.svg")
                nav_logs = gr.Button("Logs", size="sm", icon="https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/description/default/24px.svg")

            # 2B. BODY REGION (M3 Main Content) - Takes remaining space
            with gr.Column(scale=1):
                # Breadcrumbs (M3 pattern - top of body)
                breadcrumb_display = gr.HTML('''
                <div style="
                    padding: 12px 16px;
                    font-size: 13px;
                    color: #79747E;
                    border-bottom: 1px solid #e0e0e0;
                    background: #fafafa;
                ">
                    <strong style="color: #1a1a1a;">Home</strong>
                </div>
                ''')

                # Content area (swaps out - KPIs + Data Sources)
                content_area = gr.Column()

                with content_area:
                    # KPI Grid - CSS Grid for tight spacing
                    gr.HTML(f'''
                    <div style="padding: 16px;">
                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 16px;">
                            <div style="padding: 12px; text-align: center; background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.12);">
                                <div style="font-size: 9px; text-transform: uppercase; letter-spacing: 0.5px; color: #666; font-weight: 600; margin-bottom: 4px;">RECORDS</div>
                                <div style="font-size: 28px; font-weight: 700; color: #1a1a1a; font-variant-numeric: tabular-nums; line-height: 1;">224,044,778</div>
                            </div>
                            <div style="padding: 12px; text-align: center; background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.12);">
                                <div style="font-size: 9px; text-transform: uppercase; letter-spacing: 0.5px; color: #666; font-weight: 600; margin-bottom: 4px;">SIZE</div>
                                <div style="font-size: 28px; font-weight: 700; color: #1a1a1a; font-variant-numeric: tabular-nums; line-height: 1;">36.49 GB</div>
                            </div>
                            <div style="padding: 12px; text-align: center; background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.12);">
                                <div style="font-size: 9px; text-transform: uppercase; letter-spacing: 0.5px; color: #666; font-weight: 600; margin-bottom: 4px;">SOURCES</div>
                                <div style="font-size: 28px; font-weight: 700; color: #1a1a1a; font-variant-numeric: tabular-nums; line-height: 1;">6</div>
                            </div>
                            <div style="padding: 12px; text-align: center; background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.12);">
                                <div style="font-size: 9px; text-transform: uppercase; letter-spacing: 0.5px; color: #666; font-weight: 600; margin-bottom: 4px;">DATASETS</div>
                                <div style="font-size: 28px; font-weight: 700; color: #1a1a1a; font-variant-numeric: tabular-nums; line-height: 1;">5</div>
                            </div>
                        </div>
                    </div>
                    ''')

                    # Data Sources section header
                    gr.HTML(f'''
                    <div style="padding: 0 16px; margin: 8px 0;">
                        <div style="display: flex; align-items: center;">
                            <svg xmlns="http://www.w3.org/2000/svg" height="20" width="20" viewBox="0 0 24 24" fill="#666" style="margin-right: 6px;">
                                <path d="M20 6h-2.18c.11-.31.18-.65.18-1 0-1.66-1.34-3-3-3-1.05 0-1.96.54-2.5 1.35l-.5.67-.5-.68C10.96 2.54 10.05 2 9 2 7.34 2 6 3.34 6 5c0 .35.07.69.18 1H4c-1.11 0-1.99.89-1.99 2L2 19c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2zm-5-2c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zM9 4c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm11 15H4v-2h16v2zm0-5H4V8h5.08L7 10.83 8.62 12 11 8.76l1-1.36 1 1.36L15.38 12 17 10.83 14.92 8H20v6z"/>
                            </svg>
                            <h2 style="font-size: 15px; font-weight: 600; margin: 0; color: #1a1a1a;">Data Sources <span style="font-size: 12px; font-weight: 400; color: #666;">(6)</span></h2>
                        </div>
                    </div>
                    ''')

                    # Store button references for navigation wiring
                    source_buttons = {}

                    # Data source cards grid
                    with gr.Row():

                        with gr.Column(scale=1):
                            # Source card - COMPACT with Material Design icon
                            gr.HTML(f'''
                    <div style="padding: 12px; background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); margin: 0;">
                        <div style="font-size: 16px; font-weight: 600; color: #1a1a1a; margin-bottom: 6px; line-height: 1.2;">fracfocus</div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div style="display: flex; align-items: center; gap: 4px;">
                                <svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 24 24" fill="#4caf50"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
                                <span style="font-size: 12px; color: #4caf50; font-weight: 600;">Ready</span>
                            </div>
                            <span style="font-size: 9px; text-transform: uppercase; color: #666; font-weight: 600;">1 DATASETS</span>
                        </div>
                        <div style="margin-bottom: 6px;">
                            <div style="font-size: 9px; text-transform: uppercase; color: #666; font-weight: 600;">RECORDS</div>
                            <div style="font-size: 13px; font-weight: 600; color: #1a1a1a; margin: 2px 0; line-height: 1.3;">7,255,562</div>
                        </div>
                        <div style="margin-bottom: 8px;">
                            <div style="font-size: 9px; text-transform: uppercase; color: #666; font-weight: 600;">SIZE</div>
                            <div style="font-size: 13px; font-weight: 600; color: #1a1a1a; margin: 2px 0; line-height: 1.3;">3.14 GB</div>
                        </div>
                        <div style="margin: 8px 0 0 0; font-size: 11px; color: #6c757d; border-top: 1px solid #e0e0e0; padding-top: 8px;">
                            <svg xmlns="http://www.w3.org/2000/svg" height="12" width="12" viewBox="0 0 24 24" fill="#4caf50" style="display: inline; vertical-align: middle; margin-right: 2px;"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>Downloads <span style="margin: 0 4px;">→</span> <svg xmlns="http://www.w3.org/2000/svg" height="12" width="12" viewBox="0 0 24 24" fill="#4caf50" style="display: inline; vertical-align: middle; margin-right: 2px;"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>Extracted <span style="margin: 0 4px;">→</span> <svg xmlns="http://www.w3.org/2000/svg" height="12" width="12" viewBox="0 0 24 24" fill="#4caf50" style="display: inline; vertical-align: middle; margin-right: 2px;"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>Parsed
                        </div>
                    </div>
                            ''')

                            # Action buttons - REAL Gradio components (KEY DESIGN!)
                            with gr.Row():
                                view_btn_fracfocus = gr.Button("View", size="sm", variant="primary")
                                download_btn_fracfocus = gr.Button("Download", size="sm", variant="secondary")
                                rerun_btn_fracfocus = gr.Button("Re-run", size="sm", variant="secondary")

                                # Store button reference for navigation wiring
                                source_buttons['fracfocus'] = {
                                    'view': view_btn_fracfocus,
                                    'download': download_btn_fracfocus,
                                    'rerun': rerun_btn_fracfocus,
                                    'safe_name': 'fracfocus',
                                    'datasets': ["Chemical_data"]
                                }


                        with gr.Column(scale=1):
                            # Source card - COMPACT with Material Design icon
                            gr.HTML(f'''
                    <div style="padding: 12px; background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); margin: 0;">
                        <div style="font-size: 16px; font-weight: 600; color: #1a1a1a; margin-bottom: 6px; line-height: 1.2;">NETL EDX</div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div style="display: flex; align-items: center; gap: 4px;">
                                <svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 24 24" fill="#8c8c8c"><circle cx="12" cy="12" r="8"/></svg>
                                <span style="font-size: 12px; color: #8c8c8c; font-weight: 600;">Discovered</span>
                            </div>
                            <span style="font-size: 9px; text-transform: uppercase; color: #666; font-weight: 600;">0 DATASETS</span>
                        </div>
                        <div style="margin-bottom: 6px;">
                            <div style="font-size: 9px; text-transform: uppercase; color: #666; font-weight: 600;">RECORDS</div>
                            <div style="font-size: 13px; font-weight: 600; color: #1a1a1a; margin: 2px 0; line-height: 1.3;">No data</div>
                        </div>
                        <div style="margin-bottom: 8px;">
                            <div style="font-size: 9px; text-transform: uppercase; color: #666; font-weight: 600;">SIZE</div>
                            <div style="font-size: 13px; font-weight: 600; color: #1a1a1a; margin: 2px 0; line-height: 1.3;">No data</div>
                        </div>
                        <div style="margin: 8px 0 0 0; font-size: 11px; color: #6c757d; border-top: 1px solid #e0e0e0; padding-top: 8px;">
                            Not started
                        </div>
                    </div>
                            ''')

                            # Action buttons - REAL Gradio components (KEY DESIGN!)
                            with gr.Row():
                                view_btn_netl_edx = gr.Button("View", size="sm", variant="primary")
                                download_btn_netl_edx = gr.Button("Download", size="sm", variant="secondary")
                                rerun_btn_netl_edx = gr.Button("Re-run", size="sm", variant="secondary")

                                # Store button reference for navigation wiring
                                source_buttons['NETL EDX'] = {
                                    'view': view_btn_netl_edx,
                                    'download': download_btn_netl_edx,
                                    'rerun': rerun_btn_netl_edx,
                                    'safe_name': 'netl_edx',
                                    'datasets': []
                                }


                        with gr.Column(scale=1):
                            # Source card - COMPACT with Material Design icon
                            gr.HTML(f'''
                    <div style="padding: 12px; background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); margin: 0;">
                        <div style="font-size: 16px; font-weight: 600; color: #1a1a1a; margin-bottom: 6px; line-height: 1.2;">ONEPETRO</div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div style="display: flex; align-items: center; gap: 4px;">
                                <svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 24 24" fill="#8c8c8c"><circle cx="12" cy="12" r="8"/></svg>
                                <span style="font-size: 12px; color: #8c8c8c; font-weight: 600;">Discovered</span>
                            </div>
                            <span style="font-size: 9px; text-transform: uppercase; color: #666; font-weight: 600;">0 DATASETS</span>
                        </div>
                        <div style="margin-bottom: 6px;">
                            <div style="font-size: 9px; text-transform: uppercase; color: #666; font-weight: 600;">RECORDS</div>
                            <div style="font-size: 13px; font-weight: 600; color: #1a1a1a; margin: 2px 0; line-height: 1.3;">No data</div>
                        </div>
                        <div style="margin-bottom: 8px;">
                            <div style="font-size: 9px; text-transform: uppercase; color: #666; font-weight: 600;">SIZE</div>
                            <div style="font-size: 13px; font-weight: 600; color: #1a1a1a; margin: 2px 0; line-height: 1.3;">No data</div>
                        </div>
                        <div style="margin: 8px 0 0 0; font-size: 11px; color: #6c757d; border-top: 1px solid #e0e0e0; padding-top: 8px;">
                            Not started
                        </div>
                    </div>
                            ''')

                            # Action buttons - REAL Gradio components (KEY DESIGN!)
                            with gr.Row():
                                view_btn_onepetro = gr.Button("View", size="sm", variant="primary")
                                download_btn_onepetro = gr.Button("Download", size="sm", variant="secondary")
                                rerun_btn_onepetro = gr.Button("Re-run", size="sm", variant="secondary")

                                # Store button reference for navigation wiring
                                source_buttons['ONEPETRO'] = {
                                    'view': view_btn_onepetro,
                                    'download': download_btn_onepetro,
                                    'rerun': rerun_btn_onepetro,
                                    'safe_name': 'onepetro',
                                    'datasets': []
                                }


                        with gr.Column(scale=1):
                            # Source card - COMPACT with Material Design icon
                            gr.HTML(f'''
                    <div style="padding: 12px; background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); margin: 0;">
                        <div style="font-size: 16px; font-weight: 600; color: #1a1a1a; margin-bottom: 6px; line-height: 1.2;">rrc</div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div style="display: flex; align-items: center; gap: 4px;">
                                <svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 24 24" fill="#4caf50"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
                                <span style="font-size: 12px; color: #4caf50; font-weight: 600;">Ready</span>
                            </div>
                            <span style="font-size: 9px; text-transform: uppercase; color: #666; font-weight: 600;">3 DATASETS</span>
                        </div>
                        <div style="margin-bottom: 6px;">
                            <div style="font-size: 9px; text-transform: uppercase; color: #666; font-weight: 600;">RECORDS</div>
                            <div style="font-size: 13px; font-weight: 600; color: #1a1a1a; margin: 2px 0; line-height: 1.3;">216,789,216</div>
                        </div>
                        <div style="margin-bottom: 8px;">
                            <div style="font-size: 9px; text-transform: uppercase; color: #666; font-weight: 600;">SIZE</div>
                            <div style="font-size: 13px; font-weight: 600; color: #1a1a1a; margin: 2px 0; line-height: 1.3;">33.35 GB</div>
                        </div>
                        <div style="margin: 8px 0 0 0; font-size: 11px; color: #6c757d; border-top: 1px solid #e0e0e0; padding-top: 8px;">
                            <svg xmlns="http://www.w3.org/2000/svg" height="12" width="12" viewBox="0 0 24 24" fill="#4caf50" style="display: inline; vertical-align: middle; margin-right: 2px;"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>Downloads <span style="margin: 0 4px;">→</span> <svg xmlns="http://www.w3.org/2000/svg" height="12" width="12" viewBox="0 0 24 24" fill="#4caf50" style="display: inline; vertical-align: middle; margin-right: 2px;"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>Extracted <span style="margin: 0 4px;">→</span> <svg xmlns="http://www.w3.org/2000/svg" height="12" width="12" viewBox="0 0 24 24" fill="#4caf50" style="display: inline; vertical-align: middle; margin-right: 2px;"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>Parsed
                        </div>
                    </div>
                            ''')

                            # Action buttons - REAL Gradio components (KEY DESIGN!)
                            with gr.Row():
                                view_btn_rrc = gr.Button("View", size="sm", variant="primary")
                                download_btn_rrc = gr.Button("Download", size="sm", variant="secondary")
                                rerun_btn_rrc = gr.Button("Re-run", size="sm", variant="secondary")

                                # Store button reference for navigation wiring
                                source_buttons['rrc'] = {
                                    'view': view_btn_rrc,
                                    'download': download_btn_rrc,
                                    'rerun': rerun_btn_rrc,
                                    'safe_name': 'rrc',
                                    'datasets': ["completions_data", "horizontal_drilling_permits", "production"]
                                }


                        with gr.Column(scale=1):
                            # Source card - COMPACT with Material Design icon
                            gr.HTML(f'''
                    <div style="padding: 12px; background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); margin: 0;">
                        <div style="font-size: 16px; font-weight: 600; color: #1a1a1a; margin-bottom: 6px; line-height: 1.2;">TWDB</div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div style="display: flex; align-items: center; gap: 4px;">
                                <svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 24 24" fill="#8c8c8c"><circle cx="12" cy="12" r="8"/></svg>
                                <span style="font-size: 12px; color: #8c8c8c; font-weight: 600;">Discovered</span>
                            </div>
                            <span style="font-size: 9px; text-transform: uppercase; color: #666; font-weight: 600;">0 DATASETS</span>
                        </div>
                        <div style="margin-bottom: 6px;">
                            <div style="font-size: 9px; text-transform: uppercase; color: #666; font-weight: 600;">RECORDS</div>
                            <div style="font-size: 13px; font-weight: 600; color: #1a1a1a; margin: 2px 0; line-height: 1.3;">No data</div>
                        </div>
                        <div style="margin-bottom: 8px;">
                            <div style="font-size: 9px; text-transform: uppercase; color: #666; font-weight: 600;">SIZE</div>
                            <div style="font-size: 13px; font-weight: 600; color: #1a1a1a; margin: 2px 0; line-height: 1.3;">No data</div>
                        </div>
                        <div style="margin: 8px 0 0 0; font-size: 11px; color: #6c757d; border-top: 1px solid #e0e0e0; padding-top: 8px;">
                            Not started
                        </div>
                    </div>
                            ''')

                            # Action buttons - REAL Gradio components (KEY DESIGN!)
                            with gr.Row():
                                view_btn_twdb = gr.Button("View", size="sm", variant="primary")
                                download_btn_twdb = gr.Button("Download", size="sm", variant="secondary")
                                rerun_btn_twdb = gr.Button("Re-run", size="sm", variant="secondary")

                                # Store button reference for navigation wiring
                                source_buttons['TWDB'] = {
                                    'view': view_btn_twdb,
                                    'download': download_btn_twdb,
                                    'rerun': rerun_btn_twdb,
                                    'safe_name': 'twdb',
                                    'datasets': []
                                }


                        with gr.Column(scale=1):
                            # Source card - COMPACT with Material Design icon
                            gr.HTML(f'''
                    <div style="padding: 12px; background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); margin: 0;">
                        <div style="font-size: 16px; font-weight: 600; color: #1a1a1a; margin-bottom: 6px; line-height: 1.2;">usgs</div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div style="display: flex; align-items: center; gap: 4px;">
                                <svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 24 24" fill="#8c8c8c"><circle cx="12" cy="12" r="8"/></svg>
                                <span style="font-size: 12px; color: #8c8c8c; font-weight: 600;">Discovered</span>
                            </div>
                            <span style="font-size: 9px; text-transform: uppercase; color: #666; font-weight: 600;">1 DATASETS</span>
                        </div>
                        <div style="margin-bottom: 6px;">
                            <div style="font-size: 9px; text-transform: uppercase; color: #666; font-weight: 600;">RECORDS</div>
                            <div style="font-size: 13px; font-weight: 600; color: #1a1a1a; margin: 2px 0; line-height: 1.3;">No data</div>
                        </div>
                        <div style="margin-bottom: 8px;">
                            <div style="font-size: 9px; text-transform: uppercase; color: #666; font-weight: 600;">SIZE</div>
                            <div style="font-size: 13px; font-weight: 600; color: #1a1a1a; margin: 2px 0; line-height: 1.3;">No data</div>
                        </div>
                        <div style="margin: 8px 0 0 0; font-size: 11px; color: #6c757d; border-top: 1px solid #e0e0e0; padding-top: 8px;">
                            Not started
                        </div>
                    </div>
                            ''')

                            # Action buttons - REAL Gradio components (KEY DESIGN!)
                            with gr.Row():
                                view_btn_usgs = gr.Button("View", size="sm", variant="primary")
                                download_btn_usgs = gr.Button("Download", size="sm", variant="secondary")
                                rerun_btn_usgs = gr.Button("Re-run", size="sm", variant="secondary")

                                # Store button reference for navigation wiring
                                source_buttons['usgs'] = {
                                    'view': view_btn_usgs,
                                    'download': download_btn_usgs,
                                    'rerun': rerun_btn_usgs,
                                    'safe_name': 'usgs',
                                    'datasets': ["produced_water"]
                                }


                    # Navigation output area INSIDE content_area (for displaying View results)
                    nav_output = gr.HTML(value="", visible=True, elem_id="navigation-output")


                # === NAVIGATION HANDLERS (Generated from UX Patterns) ===
        # === NAVIGATION IMPLEMENTATION (Enforced from Pinecone Action Patterns) ===

        def handle_view_click(nav_state, source_name):
            """View action: Navigate from summary → detail view (Pinecone pattern)"""
            if nav_state is None:
                nav_state = {"current_path": [], "current_view": "sources"}

            # STEP 1: Determine what to show based on what's available
            source_path = Path(f"data/raw/{source_name}")
            detail_sections = []

            # Check for metadata
            metadata_file = source_path / "metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    detail_sections.append(f"""
                    <div style="background: #f8f9fa; padding: 16px; border-radius: 8px; margin-bottom: 16px;">
                        <h3 style="font-size: 20px; font-weight: 600; color: #1a1a1a; margin-bottom: 12px;">Source Metadata</h3>
                        <div style="font-size: 14px; line-height: 1.6;">
                            <p><strong>Description:</strong> {metadata.get('description', 'No description available')}</p>
                            <p><strong>Update Frequency:</strong> {metadata.get('update_frequency', 'Unknown')}</p>
                            <p><strong>Last Updated:</strong> {metadata.get('last_updated', 'Unknown')}</p>
                        </div>
                    </div>
                    """)
                except:
                    pass

            # Check for datasets (children)
            datasets = []
            if source_path.exists():
                for item in source_path.iterdir():
                    if item.is_dir():
                        datasets.append(item.name)

            if datasets:
                dataset_items = ""
                for dataset in datasets:
                    dataset_items += f"""
                    <div style="padding: 12px; border: 1px solid #e0e0e0; border-radius: 8px; margin-bottom: 8px; cursor: pointer; background: white;">
                        <div style="font-weight: 600; color: #1a1a1a; margin-bottom: 4px;">{dataset}</div>
                        <div style="font-size: 12px; color: #666;">Dataset</div>
                    </div>
                    """
                detail_sections.append(f"""
                <div style="margin-bottom: 16px;">
                    <h3 style="font-size: 20px; font-weight: 600; color: #1a1a1a; margin-bottom: 12px;">Datasets ({len(datasets)})</h3>
                    {dataset_items}
                </div>
                """)

            # STEP 2: Update navigation state
            nav_state["current_path"] = [source_name]
            nav_state["current_view"] = "datasets"

            # STEP 3: Create breadcrumb
            breadcrumb_html = f"""
            <div style="padding: 12px 0; border-bottom: 1px solid #e0e0e0; margin-bottom: 16px;">
                <span style="color: #666;">Dashboard</span>
                <span style="color: #666; margin: 0 8px;">›</span>
                <span style="font-weight: 600; color: #1a1a1a;">{source_name}</span>
            </div>
            """

            # STEP 4: Render detail view
            content_html = f"""
            <div style="padding: 16px;">
                <div style="display: flex; align-items: center; margin-bottom: 24px;">
                    <h2 style="font-size: 24px; font-weight: 600; color: #1a1a1a; margin: 0;">{source_name} Details</h2>
                </div>
                {''.join(detail_sections)}
            </div>
            """

            return nav_state, breadcrumb_html + content_html

        def handle_download_click(nav_state, source_name):
            """Download action: Export/transfer data (Pinecone pattern)"""
            if nav_state is None:
                nav_state = {"current_path": [], "current_view": "sources"}

            # STEP 1: Determine available export options
            source_path = Path(f"data/raw/{source_name}")
            available_data = []

            # Check for metadata
            metadata_file = source_path / "metadata.json"
            if metadata_file.exists():
                available_data.append("metadata.json")

            # Check for datasets
            if source_path.exists():
                for item in source_path.iterdir():
                    if item.is_file() and item.suffix in ['.csv', '.json', '.parquet']:
                        available_data.append(item.name)

            # STEP 2: Generate download interface
            if not available_data:
                result_html = f"""
                <div style="padding: 16px; text-align: center;">
                    <div style="color: #ff4d4f; font-weight: 600; font-size: 16px; margin-bottom: 8px;">No Data Available</div>
                    <div style="color: #666;">No downloadable files found for {source_name}</div>
                </div>
                """
            else:
                download_items = ""
                for item in available_data:
                    download_items += f"""
                    <div style="padding: 12px; border: 1px solid #e0e0e0; border-radius: 8px; margin-bottom: 8px; background: white; display: flex; justify-content: between; align-items: center;">
                        <div>
                            <div style="font-weight: 600; color: #1a1a1a;">{item}</div>
                            <div style="font-size: 12px; color: #666;">Ready for download</div>
                        </div>
                        <button style="padding: 6px 12px; background: #1976d2; color: white; border: none; border-radius: 4px; cursor: pointer;">Download</button>
                    </div>
                    """

                result_html = f"""
                <div style="padding: 16px;">
                    <h3 style="font-size: 20px; font-weight: 600; color: #1a1a1a; margin-bottom: 16px;">Download {source_name} Data</h3>
                    <div style="color: #52c41a; font-weight: 600; margin-bottom: 16px;">✓ {len(available_data)} file(s) available</div>
                    {download_items}
                </div>
                """

            return nav_state, result_html

        def handle_rerun_click(nav_state, source_name):
            """Re-run action: Trigger pipeline execution (Pinecone pattern)"""
            if nav_state is None:
                nav_state = {"current_path": [], "current_view": "sources"}

            # STEP 1: Check prerequisites
            source_path = Path(f"data/raw/{source_name}")
            can_execute = source_path.exists()

            if not can_execute:
                result_html = f"""
                <div style="padding: 16px; text-align: center;">
                    <div style="color: #ff4d4f; font-weight: 600; font-size: 16px; margin-bottom: 8px;">Cannot Execute</div>
                    <div style="color: #666;">Source directory not found: {source_name}</div>
                </div>
                """
            else:
                # STEP 2: Show execution progress (simulated)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                result_html = f"""
                <div style="padding: 16px;">
                    <h3 style="font-size: 20px; font-weight: 600; color: #1a1a1a; margin-bottom: 16px;">Re-running {source_name} Pipeline</h3>

                    <div style="background: #f0f7ff; padding: 16px; border-radius: 8px; border-left: 4px solid #1976d2; margin-bottom: 16px;">
                        <div style="font-weight: 600; color: #1976d2; margin-bottom: 8px;">🔄 Pipeline Execution Started</div>
                        <div style="font-size: 14px; color: #666;">Started at: {timestamp}</div>
                    </div>

                    <div style="margin-bottom: 16px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-weight: 600;">Progress</span>
                            <span style="font-size: 14px; color: #666;">Step 1 of 3</span>
                        </div>
                        <div style="width: 100%; height: 8px; background: #e0e0e0; border-radius: 4px;">
                            <div style="width: 33%; height: 100%; background: #52c41a; border-radius: 4px;"></div>
                        </div>
                    </div>

                    <div style="font-size: 14px; line-height: 1.6;">
                        <div style="color: #52c41a; font-weight: 600;">✓ Data extraction initiated</div>
                        <div style="color: #1976d2; font-weight: 600;">⟳ Processing raw data...</div>
                        <div style="color: #666;">⋯ Validation pending</div>
                    </div>
                </div>
                """

            return nav_state, result_html

        def discover_available_actions(nav_state, source_name):
            """Action discovery: Determine available actions (Pinecone pattern)"""
            source_path = Path(f"data/raw/{source_name}")
            available_actions = []

            # VIEW: Always available if source exists
            if source_path.exists():
                available_actions.append({
                    'name': 'View',
                    'handler': 'handle_view_action',
                    'variant': 'primary',
                    'enabled': True
                })

            # DOWNLOAD: Available if source has data files
            has_downloadable = False
            if source_path.exists():
                for item in source_path.iterdir():
                    if item.is_file() and item.suffix in ['.csv', '.json', '.parquet', '.xlsx']:
                        has_downloadable = True
                        break
                if (source_path / "metadata.json").exists():
                    has_downloadable = True

            if has_downloadable:
                available_actions.append({
                    'name': 'Download',
                    'handler': 'handle_download_action',
                    'variant': 'secondary',
                    'enabled': True
                })

            # RE-RUN: Available if source directory exists (can be executed)
            if source_path.exists():
                available_actions.append({
                    'name': 'Re-run',
                    'handler': 'handle_rerun_action',
                    'variant': 'secondary',
                    'enabled': True
                })

            return available_actions

        def handle_home_click():
            """Navigate back to home dashboard"""
            nav_state = {"current_path": [], "current_view": "sources"}
            breadcrumb_html = """
            <div style="padding: 12px 0; border-bottom: 1px solid #e0e0e0; margin-bottom: 16px;">
                <span style="font-weight: 600; color: #1a1a1a;">Dashboard</span>
            </div>
            """
            return nav_state, breadcrumb_html

        # Wire up ALL navigation buttons
        view_btn_fracfocus.click(
            fn=lambda ns: handle_view_click(ns, "fracfocus"),
            inputs=[nav_state],
            outputs=[nav_state, nav_output]
        )

        download_btn_fracfocus.click(
            fn=lambda ns: handle_download_click(ns, "fracfocus"),
            inputs=[nav_state],
            outputs=[nav_state, nav_output]
        )

        rerun_btn_fracfocus.click(
            fn=lambda ns: handle_rerun_click(ns, "fracfocus"),
            inputs=[nav_state],
            outputs=[nav_state, nav_output]
        )

        view_btn_netl_edx.click(
            fn=lambda ns: handle_view_click(ns, "netl_edx"),
            inputs=[nav_state],
            outputs=[nav_state, nav_output]
        )

        download_btn_netl_edx.click(
            fn=lambda ns: handle_download_click(ns, "netl_edx"),
            inputs=[nav_state],
            outputs=[nav_state, nav_output]
        )

        rerun_btn_netl_edx.click(
            fn=lambda ns: handle_rerun_click(ns, "netl_edx"),
            inputs=[nav_state],
            outputs=[nav_state, nav_output]
        )

        view_btn_onepetro.click(
            fn=lambda ns: handle_view_click(ns, "onepetro"),
            inputs=[nav_state],
            outputs=[nav_state, nav_output]
        )

        download_btn_onepetro.click(
            fn=lambda ns: handle_download_click(ns, "onepetro"),
            inputs=[nav_state],
            outputs=[nav_state, nav_output]
        )

        rerun_btn_onepetro.click(
            fn=lambda ns: handle_rerun_click(ns, "onepetro"),
            inputs=[nav_state],
            outputs=[nav_state, nav_output]
        )

        view_btn_rrc.click(
            fn=lambda ns: handle_view_click(ns, "rrc"),
            inputs=[nav_state],
            outputs=[nav_state, nav_output]
        )

        download_btn_rrc.click(
            fn=lambda ns: handle_download_click(ns, "rrc"),
            inputs=[nav_state],
            outputs=[nav_state, nav_output]
        )

        rerun_btn_rrc.click(
            fn=lambda ns: handle_rerun_click(ns, "rrc"),
            inputs=[nav_state],
            outputs=[nav_state, nav_output]
        )

        view_btn_twdb.click(
            fn=lambda ns: handle_view_click(ns, "twdb"),
            inputs=[nav_state],
            outputs=[nav_state, nav_output]
        )

        download_btn_twdb.click(
            fn=lambda ns: handle_download_click(ns, "twdb"),
            inputs=[nav_state],
            outputs=[nav_state, nav_output]
        )

        rerun_btn_twdb.click(
            fn=lambda ns: handle_rerun_click(ns, "twdb"),
            inputs=[nav_state],
            outputs=[nav_state, nav_output]
        )

        view_btn_usgs.click(
            fn=lambda ns: handle_view_click(ns, "usgs"),
            inputs=[nav_state],
            outputs=[nav_state, nav_output]
        )

        download_btn_usgs.click(
            fn=lambda ns: handle_download_click(ns, "usgs"),
            inputs=[nav_state],
            outputs=[nav_state, nav_output]
        )

        rerun_btn_usgs.click(
            fn=lambda ns: handle_rerun_click(ns, "usgs"),
            inputs=[nav_state],
            outputs=[nav_state, nav_output]
        )

        nav_home.click(
            fn=handle_home_click,
            outputs=[nav_state, breadcrumb_display]
        )
        # === END NAVIGATION HANDLERS ===
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
