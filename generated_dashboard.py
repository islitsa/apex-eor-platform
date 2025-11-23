"""
Auto-generated Pipeline Dashboard with Gradio Components
Generated at: 2025-10-29T11:13:31.076149
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
    """

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
