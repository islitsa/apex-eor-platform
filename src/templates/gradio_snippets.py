"""
Gradio Code Snippets Library (Opus Extreme Optimization)

Pre-validated, reusable Gradio code patterns.
Instead of generating code (6,000+ tokens), assemble snippets (100 tokens).

Philosophy: "Don't generate, assemble validated LEGOs"
"""

from typing import Dict, List

# ============================================================================
# CORE COMPONENT SNIPPETS
# ============================================================================

COMPONENTS = {
    # Data Source Cards
    "data_source_cards": """
    # Data source cards with navigation
    with gr.Row():
        with gr.Column(scale=1):
            source_cards = gr.Radio(
                choices=[src for src in {data_sources}],
                label="Data Sources",
                value=list({data_sources})[0] if {data_sources} else None
            )
        with gr.Column(scale=2):
            dataset_selector = gr.Dropdown(
                label="Select Dataset",
                choices=[],
                interactive=True
            )
    """,

    # File Browser
    "file_browser": """
    file_browser = gr.File(
        file_count="multiple",
        label="Files",
        interactive=False
    )
    """,

    # Data Table
    "data_table": """
    data_table = gr.Dataframe(
        label="{label}",
        interactive=False,
        wrap=True
    )
    """,

    # Navigation Dropdown
    "nav_dropdown": """
    {var_name} = gr.Dropdown(
        label="{label}",
        choices={choices},
        value={default},
        interactive=True
    )
    """,

    # Action Button
    "action_button": """
    {var_name} = gr.Button("{label}", variant="{variant}")
    """,

    # Status Display
    "status_display": """
    status = gr.Textbox(
        label="Status",
        value="Ready",
        interactive=False
    )
    """
,

    # AUTO-GENERATED from Pinecone M3 patterns
    "material_design_3_navigation_rail_specification": """with gr.Column(
        elem_classes=["navigation-rail"],
        elem_id="{rail_id}",
        scale=0,
        min_width=80
    ) as rail:
        rail.style = \"\"\"
            background-color: #FEFBFF !important;
            border-right: 1px solid #CAC4D0 !important;
            width: 80px !important;
            min-width: 80px !important;
            max-width: 80px !important;
            height: 100vh !important;
            padding: 12px 0 !important;
        \"\"\"
        
        with gr.Column(elem_classes=["rail-content"]):
            nav_btn_1 = gr.Button(
                value="",
                elem_classes=["rail-button"],
                elem_id="{btn_1_id}",
                variant="secondary"
            )
            nav_btn_2 = gr.Button(
                value="",
                elem_classes=["rail-button"],
                elem_id="{btn_2_id}",
                variant="secondary"
            )
            nav_btn_3 = gr.Button(
                value="",
                elem_classes=["rail-button"],
                elem_id="{btn_3_id}",
                variant="secondary"
            )
            nav_btn_4 = gr.Button(
                value="",
                elem_classes=["rail-button"],
                elem_id="{btn_4_id}",
                variant="secondary"
            )
            nav_btn_5 = gr.Button(
                value="",
                elem_classes=["rail-button"],
                elem_id="{btn_5_id}",
                variant="secondary"
            )
        
        rail.elem_css = \"\"\"
            .rail-button {
                width: 56px !important;
                height: 56px !important;
                margin: 4px auto !important;
                border-radius: 16px !important;
                background: transparent !important;
                border: none !important;
            }
        \"\"\"""",
    "material_design_3_compact_card_layout": """with gr.Column(elem_classes=["compact-card"]):
        with gr.Row():
            with gr.Column(scale=4):
                gr.Markdown(
                    "**{title}**",
                    elem_classes=["card-title"]
                )
                gr.Markdown(
                    "{subtitle}",
                    elem_classes=["card-subtitle"]
                )
            with gr.Column(scale=1, min_width=60):
                gr.Markdown(
                    "STATUS",
                    elem_classes=["card-label"]
                )
                gr.Markdown(
                    "**{status_value}**",
                    elem_classes=["card-value"]
                )
        
        with gr.Row():
            gr.Markdown(
                "{body_text}",
                elem_classes=["card-body"]
            )
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("METRIC", elem_classes=["card-label"])
                gr.Markdown("**{metric_value}**", elem_classes=["card-value"])
            with gr.Column(scale=1):
                gr.Markdown("TREND", elem_classes=["card-label"])
                gr.Markdown("**{trend_value}**", elem_classes=["card-value"])
            with gr.Column(scale=2):
                action_btn = gr.Button(
                    "{action_label}",
                    size="sm",
                    variant="secondary",
                    elem_classes=["card-action"]
                )""",
    "m3_navigation_card_pattern": """with gr.Column():
        card_html = gr.HTML(
            value=f\"\"\"
            <div style="background: #FFFBFE; border-radius: 12px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); margin: 8px 0;">
                <div style="font-size: 16px; font-weight: 600; color: #1C1B1F; margin-bottom: 8px;">{title}</div>
                <div style="font-size: 14px; color: #79747E; line-height: 1.5;">{description}</div>
            </div>
            \"\"\".replace('{title}', '{title}').replace('{description}', '{description}')
        )
        
        with gr.Row():
            action_btn = gr.Button(
                value="{button_text}",
                variant="primary",
                size="sm",
                scale=1
            )
            secondary_btn = gr.Button(
                value="{secondary_button_text}",
                variant="secondary", 
                size="sm",
                scale=1
            )
        
        result_output = gr.Textbox(
            label="{output_label}",
            value="{default_value}",
            interactive=False,
            visible=False
        )
        
        def handle_primary_action():
            return gr.update(visible=True, value="{action_result}")
        
        def handle_secondary_action():
            return gr.update(visible=True, value="{secondary_result}")
        
        action_btn.click(
            fn=handle_primary_action,
            outputs=result_output
        )
        
        secondary_btn.click(
            fn=handle_secondary_action,
            outputs=result_output
        )""",
    "m3_metric_card_pattern": """with gr.Column():
        metric_card = gr.HTML(
            value=f\"\"\"
            <div style="background: #FFFBFE; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); text-align: center;">
                <div style="font-size: 12px; color: #79747E; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; font-weight: 600;">{"{label}"}</div>
                <div style="font-size: 45px; font-weight: 400; color: #1C1B1F; line-height: 1.2; font-variant-numeric: tabular-nums;">{"{value}"}</div>
                <div style="font-size: 14px; color: #79747E; margin-top: 8px;">{"{description}"}</div>
            </div>
            \"\"\"
        )""",
    "material_design_3_navigation_rail_implementation_in_gradio": """with gr.Row(elem_classes="nav-container"):
        with gr.Column(scale=0, min_width=80, elem_classes="nav-rail"):
            gr.HTML(f'''
                <div style="
                    width: 80px;
                    background: var(--color-accent-soft);
                    padding: 16px 8px;
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    border-right: 1px solid var(--border-color-primary);
                    position: fixed;
                    left: 0;
                    top: 0;
                    z-index: 100;
                ">
                    <div style="margin-bottom: 24px;">
                        <button style="
                            width: 56px;
                            height: 56px;
                            border-radius: 16px;
                            background: var(--color-accent);
                            border: none;
                            color: white;
                            font-size: 24px;
                            cursor: pointer;
                        ">{fab_icon}</button>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 12px;">
                        <button class="nav-item" onclick="showTab('{tab1_id}')" style="
                            width: 56px; height: 32px; border: none; background: none;
                            border-radius: 16px; cursor: pointer; color: var(--body-text-color);
                        ">{nav1_icon}</button>
                        <button class="nav-item" onclick="showTab('{tab2_id}')" style="
                            width: 56px; height: 32px; border: none; background: none;
                            border-radius: 16px; cursor: pointer; color: var(--body-text-color);
                        ">{nav2_icon}</button>
                        <button class="nav-item" onclick="showTab('{tab3_id}')" style="
                            width: 56px; height: 32px; border: none; background: none;
                            border-radius: 16px; cursor: pointer; color: var(--body-text-color);
                        ">{nav3_icon}</button>
                        <button class="nav-item" onclick="showTab('{tab4_id}')" style="
                            width: 56px; height: 32px; border: none; background: none;
                            border-radius: 16px; cursor: pointer; color: var(--body-text-color);
                        ">{nav4_icon}</button>
                    </div>
                </div>
                <style>
                    .nav-item:hover {{
                        background: var(--color-accent-soft) !important;
                    }}
                </style>
            ''')
        with gr.Column(elem_classes="main-content", elem_id="content-area"):
            gr.Markdown(f"### {content_title}")
            content_display = gr.HTML(f"<div id='tab-content'>{default_content}</div>")""",
    "material_design_3_button_sizes_and_density": """with gr.Column():
        gr.HTML(\"\"\"
            <style>
            .large-btn { height: 40px !important; padding: 0 24px !important; font-size: 14px !important; font-weight: 500 !important; margin: 4px !important; }
            .medium-btn { height: 32px !important; padding: 0 16px !important; font-size: 13px !important; font-weight: 500 !important; margin: 4px !important; }
            .small-btn { height: 28px !important; padding: 0 12px !important; font-size: 12px !important; font-weight: 500 !important; margin: 4px !important; }
            .xs-btn { height: 24px !important; padding: 0 8px !important; font-size: 11px !important; font-weight: 500 !important; margin: 4px !important; }
            .btn-row { gap: 8px !important; margin-top: 16px !important; }
            </style>
        \"\"\")
        
        gr.Markdown("### {section_title}")
        
        with gr.Row(elem_classes="btn-row"):
            large_btn = gr.Button(
                value="{large_label}",
                elem_classes="large-btn",
                variant="primary"
            )
            medium_btn = gr.Button(
                value="{medium_label}",
                elem_classes="medium-btn",
                variant="secondary"
            )
        
        with gr.Row(elem_classes="btn-row"):
            small_btn = gr.Button(
                value="{small_label}",
                elem_classes="small-btn",
                variant="secondary"
            )
            xs_btn = gr.Button(
                value="{xs_label}",
                elem_classes="xs-btn",
                variant="secondary"
            )
        
        status_display = gr.Textbox(
            label="Button Status",
            value="{status_message}",
            interactive=False,
            elem_classes="btn-row"
        )
        
        large_btn.click(lambda: "Large button clicked", outputs=status_display)
        medium_btn.click(lambda: "Medium button clicked", outputs=status_display)
        small_btn.click(lambda: "Small button clicked", outputs=status_display)
        xs_btn.click(lambda: "Extra small button clicked", outputs=status_display)""",
    "material_design_3_status_indicators_and_icons": """with gr.Column():
        gr.Markdown("### {title}")
        
        with gr.Row():
            gr.HTML(\"\"\"
                <div style="display: inline-flex; align-items: center; gap: 8px; padding: 8px 12px; border-radius: 8px; background-color: #e8f5e8; border: 1px solid #4caf50;">
                    <svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 24 24" fill="#4caf50">
                        <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                    </svg>
                    <span style="color: #2e7d2e; font-weight: 500;">{success_message}</span>
                </div>
            \"\"\")
            
            gr.HTML(\"\"\"
                <div style="display: inline-flex; align-items: center; gap: 8px; padding: 8px 12px; border-radius: 8px; background-color: #fff3e0; border: 1px solid #fb8c00;">
                    <svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 24 24" fill="#fb8c00">
                        <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
                    </svg>
                    <span style="color: #e65100; font-weight: 500;">{warning_message}</span>
                </div>
            \"\"\")
        
        with gr.Row():
            gr.HTML(\"\"\"
                <div style="display: inline-flex; align-items: center; gap: 8px; padding: 8px 12px; border-radius: 8px; background-color: #fdeaea; border: 1px solid #ba1a1a;">
                    <svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 24 24" fill="#ba1a1a">
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                    </svg>
                    <span style="color: #ba1a1a; font-weight: 500;">{error_message}</span>
                </div>
            \"\"\")
            
            gr.HTML(\"\"\"
                <div style="display: inline-flex; align-items: center; gap: 8px; padding: 8px 12px; border-radius: 8px; background-color: #e3f2fd; border: 1px solid #2196f3;">
                    <svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 24 24" fill="#2196f3">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
                    </svg>
                    <span style="color: #1565c0; font-weight: 500;">{info_message}</span>
                </div>
            \"\"\")""",
    "material_design_3_persistent_navigation_pattern_for_dashboards": """with gr.Row():
        # Navigation Rail
        with gr.Column(scale=1, min_width=120):
            gr.Markdown("### {app_title}")
            nav_home = gr.Button("🏠 Home", variant="secondary", size="sm")
            nav_dashboard = gr.Button("📊 Dashboard", variant="secondary", size="sm")
            nav_analytics = gr.Button("📈 Analytics", variant="secondary", size="sm")
            nav_reports = gr.Button("📋 Reports", variant="secondary", size="sm")
            nav_settings = gr.Button("⚙️ Settings", variant="secondary", size="sm")
        
        # Main Content Area
        with gr.Column(scale=4):
            # Top App Bar
            with gr.Row():
                page_title = gr.Markdown("## {page_title}")
                with gr.Row():
                    search_box = gr.Textbox(placeholder="Search...", scale=2, container=False)
                    action_btn = gr.Button("⋮", size="sm", scale=0)
            
            # Breadcrumbs
            breadcrumbs = gr.Markdown("🏠 > {breadcrumb_path}")
            
            # Dynamic Body Content
            with gr.Column():
                content_area = gr.HTML(\"\"\"
                    <div style="min-height: 400px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                        <h3>{content_title}</h3>
                        <p>{content_description}</p>
                        {dynamic_content}
                    </div>
                \"\"\")
                
                # Data Display Area
                data_table = gr.Dataframe(
                    headers=["{col1}", "{col2}", "{col3}"],
                    value="{table_data}",
                    interactive=False
                )
                
                # Action Panel
                with gr.Row():
                    primary_action = gr.Button("{primary_action_label}", variant="primary")
                    secondary_action = gr.Button("{secondary_action_label}", variant="secondary")
                    status_indicator = gr.Textbox(value="{status_message}", interactive=False, container=False)""",
    "gradio_navigation_layout_preventing_duplicate_sections": """with gr.Column() as main_container:
        # Static content section (visible initially)
        with gr.Column(visible=True) as static_content:
            gr.Markdown("### {section_title}")
            with gr.Row():
                with gr.Column():
                    gr.Markdown("**Data Sources**")
                    data_table = gr.Dataframe(
                        value={data_sources},
                        headers=["Source", "Status", "Records"],
                        interactive=False
                    )
                with gr.Column():
                    gr.Markdown("**Quick Actions**")
                    refresh_btn = gr.Button("Refresh Data", variant="secondary")
                    export_btn = gr.Button("Export Report", variant="primary")
        
        # Dynamic navigation output (hidden initially)
        nav_output = gr.Column(visible=False)
        
        # Navigation controls
        with gr.Row():
            home_btn = gr.Button("Home", size="sm")
            dashboard_btn = gr.Button("Dashboard", size="sm")
            reports_btn = gr.Button("Reports", size="sm")
        
        # Navigation handlers
        def show_static():
            return gr.update(visible=True), gr.update(visible=False)
        
        def show_dynamic():
            return gr.update(visible=False), gr.update(visible=True)
        
        home_btn.click(show_static, outputs=[static_content, nav_output])
        dashboard_btn.click(show_dynamic, outputs=[static_content, nav_output])
        reports_btn.click(show_dynamic, outputs=[static_content, nav_output])""",
    "complete_gradio_bidirectional_navigation_pattern_generic_all_navigation_types": """with gr.Column():
        # Navigation Header
        with gr.Row():
            back_btn = gr.Button("← Back", variant="secondary", size="sm")
            current_location = gr.Markdown("**Current:** {current_path}")
        
        # Breadcrumb Navigation
        with gr.Row():
            breadcrumb_html = gr.HTML(value="{breadcrumb_html}")
            breadcrumb_buttons = gr.Row(visible=False)
        
        # Content Area
        with gr.Column():
            content_title = gr.Markdown("### {content_title}")
            navigation_data = gr.Dataframe(
                headers=["Name", "Type", "Modified"],
                datatype=["str", "str", "str"],
                value={navigation_items},
                interactive=False,
                height=300
            )
        
        # Navigation Controls
        with gr.Row():
            go_home_btn = gr.Button("🏠 Home", size="sm")
            refresh_btn = gr.Button("🔄 Refresh", size="sm")
            path_input = gr.Textbox(
                placeholder="Enter path to navigate...",
                label="Go to Path",
                scale=3
            )
            go_btn = gr.Button("Go", variant="primary", size="sm")
        
        # Hidden State
        current_path_state = gr.State(value="{initial_path}")
        navigation_history = gr.State(value=[])
        
        # Event Handlers
        back_btn.click(
            fn={back_handler},
            inputs=[current_path_state, navigation_history],
            outputs=[current_path_state, navigation_data, current_location, navigation_history]
        )
        
        navigation_data.select(
            fn={navigate_handler},
            inputs=[current_path_state, navigation_data],
            outputs=[current_path_state, navigation_data, current_location, navigation_history]
        )
        
        go_home_btn.click(
            fn={home_handler},
            outputs=[current_path_state, navigation_data, current_location, navigation_history]
        )
        
        go_btn.click(
            fn={path_handler},
            inputs=[path_input, current_path_state],
            outputs=[current_path_state, navigation_data, current_location, path_input, navigation_history]
        )
        
        refresh_btn.click(
            fn={refresh_handler},
            inputs=[current_path_state],
            outputs=[navigation_data, current_location]
        )""",
    "folder_navigation_pattern_view_doubleclick": """with gr.Column():
        gr.Markdown("### {folder_title}")
        
        # Navigation breadcrumb
        breadcrumb = gr.Markdown("📁 {breadcrumb_path}")
        
        # Current folder contents
        with gr.Row():
            with gr.Column(scale=3):
                folder_display = gr.Dataframe(
                    headers=["Type", "Name", "Size", "Modified"],
                    value={folder_contents},
                    interactive=False,
                    wrap=True
                )
            
            with gr.Column(scale=1):
                gr.Markdown("**Actions**")
                view_btn = gr.Button("👁️ View Selected", variant="primary")
                back_btn = gr.Button("⬅️ Back", variant="secondary")
                refresh_btn = gr.Button("🔄 Refresh")
        
        # Status and metadata
        with gr.Row():
            status_text = gr.Textbox(
                label="Status",
                value="{current_status}",
                interactive=False
            )
            item_count = gr.Textbox(
                label="Items",
                value="{item_count}",
                interactive=False
            )
        
        # Navigation logic
        selected_row = gr.State(value=None)
        current_path = gr.State(value="{initial_path}")
        
        folder_display.select(
            fn=lambda evt: evt.index[0] if evt.index else None,
            outputs=selected_row
        )
        
        view_btn.click(
            fn=lambda row, path, data: navigate_into_item(row, path, data),
            inputs=[selected_row, current_path, folder_display],
            outputs=[folder_display, breadcrumb, current_path, status_text]
        )
        
        back_btn.click(
            fn=lambda path: navigate_back(path),
            inputs=current_path,
            outputs=[folder_display, breadcrumb, current_path, status_text]
        )""",
    "gradio_bidirectional_navigation_with_backup_buttons_generic": """with gr.Column():
        with gr.Row():
            back_btn = gr.Button("← Back", size="sm", visible=False)
            up_btn = gr.Button("↑ Up", size="sm", visible=False)
            refresh_btn = gr.Button("🔄", size="sm")
        
        current_path = gr.Markdown("**Current:** {current_location}")
        
        nav_state = gr.State(value={{"path": [], "current": "{initial_item}", "items": {items_data}}})
        
        main_content = gr.Dataframe(
            value={content_data},
            headers={headers_list},
            interactive=False
        )
        
        with gr.Row():
            view_selected = gr.Button("View Selected", variant="primary")
            action_btn = gr.Button("{action_label}")
        
        selected_item = gr.Textbox(visible=False)
        
        def navigate_back(state):
            if state["path"]:
                state["path"].pop()
                current = state["path"][-1] if state["path"] else "{root_item}"
                state["current"] = current
                return update_navigation_display(state)
            return gr.update(), gr.update(), gr.update(), gr.update(), state
        
        def navigate_up(state):
            if len(state["path"]) > 1:
                state["path"] = state["path"][:-1]
                state["current"] = state["path"][-1]
                return update_navigation_display(state)
            return gr.update(), gr.update(), gr.update(), gr.update(), state
        
        def update_navigation_display(state):
            path_display = " → ".join(state["path"]) if state["path"] else state["current"]
            back_visible = len(state["path"]) > 0
            up_visible = len(state["path"]) > 1
            content = {filtered_content_data}
            return (
                gr.update(visible=back_visible),
                gr.update(visible=up_visible), 
                f"**Current:** {path_display}",
                gr.update(value=content),
                state
            )
        
        back_btn.click(navigate_back, [nav_state], [back_btn, up_btn, current_path, main_content, nav_state])
        up_btn.click(navigate_up, [nav_state], [back_btn, up_btn, current_path, main_content, nav_state])""",
    "pipeline_stage_click_interaction": """with gr.Column():
        gr.Markdown("### Pipeline Progress")
        
        with gr.Row():
            download_btn = gr.Button("○ Downloads", elem_id="stage_download", variant="secondary")
            extract_btn = gr.Button("○ Extract", elem_id="stage_extract", variant="secondary") 
            parse_btn = gr.Button("○ Parse", elem_id="stage_parse", variant="secondary")
        
        stage_output = gr.Dataframe(
            headers=["File", "Status", "Size"],
            value=[],
            interactive=False,
            visible=False
        )
        
        stage_text = gr.Textbox(
            value="Click on a completed stage to view results",
            interactive=False,
            lines=3
        )
        
        def show_downloads():
            return {
                download_btn: gr.Button("✓ Downloads", variant="primary"),
                stage_output: gr.Dataframe(value={download_data}, visible=True),
                stage_text: gr.Textbox(value="Downloaded files:", visible=False)
            }
        
        def show_extracts():
            return {
                extract_btn: gr.Button("✓ Extracted", variant="primary"),
                stage_output: gr.Dataframe(value={extract_data}, visible=True),
                stage_text: gr.Textbox(value="Extracted files:", visible=False)
            }
        
        def show_parsed():
            return {
                parse_btn: gr.Button("✓ Parsed", variant="primary"),
                stage_output: gr.Dataframe(value={parse_data}, visible=True),
                stage_text: gr.Textbox(value="Parsed data:", visible=False)
            }
        
        download_btn.click(show_downloads, outputs=[download_btn, stage_output, stage_text])
        extract_btn.click(show_extracts, outputs=[extract_btn, stage_output, stage_text])
        parse_btn.click(show_parsed, outputs=[parse_btn, stage_output, stage_text])""",
    "dashboard_with_sidebar_layout_v2_fixed": """with gr.Row():
        with gr.Column(scale=1, min_width=250):
            gr.Markdown("## {sidebar_title}")
            nav_btn1 = gr.Button("{nav_button_1}", variant="primary")
            nav_btn2 = gr.Button("{nav_button_2}")
            nav_btn3 = gr.Button("{nav_button_3}")
            gr.Markdown("---")
            filter_input = gr.Textbox(label="{filter_label}", placeholder="{filter_placeholder}")
            apply_filter = gr.Button("{apply_filter_btn}")
            
        with gr.Column(scale=4):
            with gr.Row():
                gr.Markdown("### {metadata_title}")
                refresh_btn = gr.Button("🔄", size="sm")
            
            with gr.Row():
                with gr.Column():
                    status_box = gr.Textbox(label="{status_label}", value="{status_value}", interactive=False)
                with gr.Column():
                    count_box = gr.Textbox(label="{count_label}", value="{count_value}", interactive=False)
                with gr.Column():
                    updated_box = gr.Textbox(label="{updated_label}", value="{updated_value}", interactive=False)
            
            gr.Markdown("---")
            
            with gr.Row():
                gr.Markdown("## {main_title}")
                export_btn = gr.Button("{export_button}", variant="secondary")
            
            main_content = gr.Dataframe(
                headers=["{col1_header}", "{col2_header}", "{col3_header}"],
                datatype=["str", "str", "number"],
                value="{table_data}",
                interactive=True
            )
            
            with gr.Row():
                action_input = gr.Textbox(label="{action_label}", placeholder="{action_placeholder}")
                submit_btn = gr.Button("{submit_button}", variant="primary")""",
    "material_design_3_app_structure_top_app_bar_navigation_body": """with gr.Column(elem_classes=["m3-app-structure"]):
        # Top App Bar
        with gr.Row(elem_classes=["m3-top-bar"], variant="compact"):
            with gr.Column(scale=3):
                gr.Markdown("## {app_title}")
            with gr.Column(scale=1):
                with gr.Row():
                    search_btn = gr.Button("🔍", size="sm", variant="secondary")
                    settings_btn = gr.Button("⚙️", size="sm", variant="secondary")
                    profile_btn = gr.Button("👤", size="sm", variant="secondary")
        
        # Main Content Area
        with gr.Row(elem_classes=["m3-main-content"]):
            # Navigation Rail (Desktop/Tablet)
            with gr.Column(scale=1, min_width=80, elem_classes=["m3-nav-rail"]):
                nav_home = gr.Button("🏠\nHome", variant="primary", size="sm")
                nav_dashboard = gr.Button("📊\nDashboard", variant="secondary", size="sm")
                nav_projects = gr.Button("📁\nProjects", variant="secondary", size="sm")
                nav_analytics = gr.Button("📈\nAnalytics", variant="secondary", size="sm")
                nav_settings = gr.Button("⚙️\nSettings", variant="secondary", size="sm")
            
            # Body Content
            with gr.Column(scale=6, elem_classes=["m3-body-content"]):
                gr.Markdown("### {content_title}")
                content_area = gr.Textbox(
                    value="{main_content}",
                    placeholder="{content_placeholder}",
                    lines=8,
                    interactive=True
                )
                
                with gr.Row():
                    data_table = gr.Dataframe(
                        value={data_table},
                        headers=["{col1}", "{col2}", "{col3}"],
                        interactive=True
                    )
                
                with gr.Row():
                    action_primary = gr.Button("{primary_action}", variant="primary")
                    action_secondary = gr.Button("{secondary_action}", variant="secondary")
        
        # Mobile Navigation Bar (Bottom)
        with gr.Row(elem_classes=["m3-nav-bar-mobile"], visible=False):
            mob_home = gr.Button("🏠", variant="primary", size="sm")
            mob_dashboard = gr.Button("📊", variant="secondary", size="sm")
            mob_projects = gr.Button("📁", variant="secondary", size="sm")
            mob_analytics = gr.Button("📈", variant="secondary", size="sm")""",
    "scrolling_when_to_use_scrollbars": """with gr.Column():
        gr.Markdown("### {title}")
        
        # Fixed height scrollable components
        with gr.Row():
            with gr.Column():
                gr.Markdown("**Chat Log (Scrollable)**")
                chat_log = gr.Textbox(
                    value="{chat_messages}",
                    lines=8,
                    max_lines=15,
                    label="Messages",
                    interactive=False
                )
            
            with gr.Column():
                gr.Markdown("**File List (Scrollable)**")
                file_list = gr.Dataframe(
                    value="{file_data}",
                    headers=["Name", "Size", "Modified"],
                    max_rows=6,
                    overflow_row_behaviour="paginate"
                )
        
        # Non-scrollable dashboard overview
        gr.Markdown("**System Status (Show All)**")
        with gr.Row():
            with gr.Column():
                gr.Textbox(value="{cpu_status}", label="CPU", interactive=False)
                gr.Textbox(value="{memory_status}", label="Memory", interactive=False)
            
            with gr.Column():
                gr.Textbox(value="{disk_status}", label="Disk", interactive=False)
                gr.Textbox(value="{network_status}", label="Network", interactive=False)
        
        # Form inputs - no scrollbars needed
        gr.Markdown("**Settings (Full View)**")
        with gr.Column():
            gr.Textbox(value="{username}", label="Username")
            gr.Textbox(value="{email}", label="Email")
            
        gr.Button("{action_button}")""",
    "buttons_visual_presence_functional_initially": """with gr.Column():
        gr.Markdown("### {title}")
        
        with gr.Row():
            # Functional buttons
            process_btn = gr.Button("{process_label}", variant="primary")
            clear_btn = gr.Button("{clear_label}", variant="secondary")
            
        with gr.Row():
            # Non-functional buttons (coming soon)
            view_btn = gr.Button(
                "{view_label}", 
                variant="secondary",
                interactive=False,
                elem_classes="coming-soon-btn"
            )
            download_btn = gr.Button(
                "{download_label}", 
                variant="secondary", 
                interactive=False,
                elem_classes="coming-soon-btn"
            )
            rerun_btn = gr.Button(
                "{rerun_label}", 
                variant="secondary",
                interactive=False, 
                elem_classes="coming-soon-btn"
            )
            
        gr.Markdown(
            '<div style="opacity: 0.7; font-size: 0.9em; color: #666; text-align: center;">'
            '🚧 {coming_soon_text}</div>',
            elem_classes="coming-soon-notice"
        )
        
        output_area = gr.Textbox(
            label="{output_label}",
            value="{output_value}",
            lines=5,
            interactive=False
        )
        
        # Event handlers for functional buttons only
        process_btn.click(
            fn=lambda x: f"Processing: {x}",
            inputs=[],
            outputs=[output_area]
        )
        
        clear_btn.click(
            fn=lambda: "",
            inputs=[],
            outputs=[output_area]
        )""",
    "contextbased_action_discovery_pattern": """with gr.Column():
        gr.Markdown("### Context-Based Action Discovery")
        
        with gr.Row():
            item_input = gr.Textbox(
                label="Item ID/Path",
                placeholder="{item_placeholder}",
                value="{default_item}"
            )
            context_input = gr.Textbox(
                label="Context Info",
                placeholder="{context_placeholder}",
                value="{default_context}"
            )
        
        discover_btn = gr.Button("Discover Available Actions", variant="primary")
        
        with gr.Row():
            capabilities_display = gr.Textbox(
                label="Detected Capabilities",
                value="{capabilities}",
                interactive=False,
                lines=3
            )
            context_display = gr.Textbox(
                label="Context Analysis",
                value="{context_analysis}",
                interactive=False,
                lines=3
            )
        
        actions_table = gr.Dataframe(
            headers=["Action", "Available", "Requirements", "Priority"],
            value={actions_data},
            label="Available Actions",
            interactive=False
        )
        
        with gr.Row():
            selected_action = gr.Dropdown(
                choices={action_choices},
                label="Select Action",
                value="{default_action}"
            )
            execute_btn = gr.Button("Execute Action", variant="secondary")
        
        result_output = gr.Textbox(
            label="Action Result",
            value="{result}",
            interactive=False,
            lines=4
        )""",
    "view_action_masterdetail_navigation_pattern": """with gr.Column():
        # Breadcrumb navigation
        breadcrumb = gr.Markdown("🏠 Home > {master_view_title}")
        
        with gr.Row():
            back_btn = gr.Button("← Back to {master_view_title}", variant="secondary", size="sm")
            
        # Detail view header
        gr.Markdown("### {item_title}")
        
        # Detail content area
        detail_content = gr.Markdown("{detail_content}")
        
        # Detail data table (if applicable)
        detail_table = gr.Dataframe(
            value={detail_data},
            interactive=False,
            visible=True,
            label="Details"
        )
        
        # Action buttons for detail view
        with gr.Row():
            edit_btn = gr.Button("Edit", variant="primary")
            delete_btn = gr.Button("Delete", variant="stop")
            share_btn = gr.Button("Share", variant="secondary")
        
        # Status/feedback area
        status_msg = gr.Textbox(
            value="",
            placeholder="Status messages appear here...",
            interactive=False,
            visible=False,
            label="Status"
        )
        
        # Hidden state to track current item
        current_item_id = gr.State(value="{item_id}")
        master_view_context = gr.State(value="{master_context}")""",
    "download_action_exporttransfer_pattern": """with gr.Column():
        gr.Markdown("### Export {data_type}")
        
        with gr.Row():
            format_dropdown = gr.Dropdown(
                choices=["{format_1}", "{format_2}", "{format_3}"],
                value="{default_format}",
                label="Export Format",
                scale=2
            )
            include_metadata = gr.Checkbox(
                label="Include Metadata",
                value=True,
                scale=1
            )
        
        with gr.Row():
            filename_input = gr.Textbox(
                value="{default_filename}",
                label="Filename",
                placeholder="Enter filename..."
            )
        
        export_btn = gr.Button(
            "{export_button_label}",
            variant="primary",
            size="lg"
        )
        
        status_text = gr.Textbox(
            label="Export Status",
            value="Ready to export",
            interactive=False
        )
        
        download_file = gr.File(
            label="Download Ready",
            visible=False
        )
        
        def handle_export(format_type, include_meta, filename):
            # Process export logic here
            return "Exporting...", gr.File(visible=True, value="{exported_file_path}")
        
        export_btn.click(
            handle_export,
            inputs=[format_dropdown, include_metadata, filename_input],
            outputs=[status_text, download_file]
        )""",
    "edit_action_modifyupdate_pattern": """with gr.Column():
        gr.Markdown("### Edit {item_type}")
        
        with gr.Row():
            item_selector = gr.Dropdown(
                choices={item_list},
                label="Select {item_type} to Edit",
                value="{default_item}"
            )
            load_btn = gr.Button("Load", variant="secondary")
        
        with gr.Column(visible=False) as edit_panel:
            gr.Markdown("#### Modify Details")
            
            with gr.Row():
                field1 = gr.Textbox(label="{field1_label}", value="{field1_value}")
                field2 = gr.Textbox(label="{field2_label}", value="{field2_value}")
            
            field3 = gr.Textbox(
                label="{field3_label}", 
                value="{field3_value}",
                lines=3
            )
            
            with gr.Row():
                save_btn = gr.Button("Update {item_type}", variant="primary")
                cancel_btn = gr.Button("Cancel", variant="secondary")
        
        status_msg = gr.Markdown("")
        
        def load_item(selected_id):
            if selected_id:
                return {
                    gr.update(visible=True),
                    "{loaded_field1_data}",
                    "{loaded_field2_data}", 
                    "{loaded_field3_data}"
                }
            return gr.update(visible=False), "", "", ""
        
        def save_changes(id_val, f1, f2, f3):
            # Validation and save logic here
            return "✅ {item_type} updated successfully!", gr.update(visible=False)
        
        def cancel_edit():
            return "", gr.update(visible=False)
        
        load_btn.click(
            load_item,
            inputs=[item_selector],
            outputs=[edit_panel, field1, field2, field3]
        )
        
        save_btn.click(
            save_changes,
            inputs=[item_selector, field1, field2, field3],
            outputs=[status_msg, edit_panel]
        )
        
        cancel_btn.click(
            cancel_edit,
            outputs=[status_msg, edit_panel]
        )"""
}


# ============================================================================
# INTERACTION PATTERNS (Event Handlers)
# ============================================================================

INTERACTIONS = {
    # Navigation: Source → Dataset
    "source_to_dataset_nav": """
    def update_datasets(source_name):
        if source_name in PIPELINE_DATA["sources"]:
            datasets = list(PIPELINE_DATA["sources"][source_name].get("datasets", {}).keys())
            return gr.Dropdown(choices=datasets, value=datasets[0] if datasets else None)
        return gr.Dropdown(choices=[], value=None)

    {source_selector}.change(
        update_datasets,
        inputs=[{source_selector}],
        outputs=[{dataset_selector}]
    )
    """,

    # Navigation: Dataset → Details
    "dataset_to_details_nav": """
    def show_dataset_details(source_name, dataset_name):
        if not source_name or not dataset_name:
            return "No selection"

        dataset = PIPELINE_DATA["sources"][source_name]["datasets"].get(dataset_name, {})
        details = f"Dataset: {dataset_name}\\n"
        details += f"Records: {dataset.get('records', 'N/A')}\\n"
        details += f"Status: {dataset.get('status', 'Unknown')}"
        return details

    {dataset_selector}.change(
        show_dataset_details,
        inputs=[{source_selector}, {dataset_selector}],
        outputs=[{detail_display}]
    )
    """,

    # Button Click: Load Files
    "button_load_files": """
    def load_files_{id}(dataset_name):
        # Load files for dataset
        files = get_files_for_dataset(dataset_name)
        return files

    {button}.click(
        load_files_{id},
        inputs=[{dataset_selector}],
        outputs=[{file_browser}]
    )
    """,

    # Search/Filter
    "search_filter": """
    def filter_data_{id}(search_term, data):
        if not search_term:
            return data
        return [row for row in data if search_term.lower() in str(row).lower()]

    {search_box}.change(
        filter_data_{id},
        inputs=[{search_box}, {data_source}],
        outputs=[{data_table}]
    )
    """
}


# ============================================================================
# COMPLETE PATTERNS (Full Dashboard Templates)
# ============================================================================

PATTERNS = {
    "pipeline_navigation": """
import gradio as gr
from typing import Dict, List

# Pipeline data structure
PIPELINE_DATA = {pipeline_data}

def create_pipeline_dashboard():
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# Pipeline Data Navigator")

        # Main layout: Source → Dataset → Details
        with gr.Row():
            # Column 1: Data Source Selection
            with gr.Column(scale=1):
                gr.Markdown("### Data Sources")
                source_selector = gr.Radio(
                    choices=list(PIPELINE_DATA["sources"].keys()),
                    label="Select Source",
                    value=list(PIPELINE_DATA["sources"].keys())[0]
                )

            # Column 2: Dataset Selection
            with gr.Column(scale=1):
                gr.Markdown("### Datasets")
                dataset_selector = gr.Dropdown(
                    label="Select Dataset",
                    choices=[],
                    interactive=True
                )

            # Column 3: Details Display
            with gr.Column(scale=2):
                gr.Markdown("### Details")
                details_display = gr.Textbox(
                    label="Dataset Information",
                    lines=10,
                    interactive=False
                )

        # Event Handlers
        def update_datasets(source_name):
            datasets = list(PIPELINE_DATA["sources"][source_name].get("datasets", {}).keys())
            return gr.Dropdown(choices=datasets, value=datasets[0] if datasets else None)

        def show_details(source_name, dataset_name):
            if not dataset_name:
                return "No dataset selected"
            dataset = PIPELINE_DATA["sources"][source_name]["datasets"].get(dataset_name, {})
            details = f"**Dataset:** {dataset_name}\\n\\n"
            details += f"**Records:** {dataset.get('records', 'N/A'):,}\\n"
            details += f"**Status:** {dataset.get('status', 'Unknown')}\\n"
            details += f"**Last Updated:** {dataset.get('last_updated', 'N/A')}"
            return details

        # Wire events
        source_selector.change(update_datasets, [source_selector], [dataset_selector])
        dataset_selector.change(show_details, [source_selector, dataset_selector], [details_display])

        # Auto-load first dataset
        demo.load(update_datasets, [source_selector], [dataset_selector])

    return demo

if __name__ == "__main__":
    demo = create_pipeline_dashboard()
    demo.launch()
""",

    "data_grid_with_filter": """
import gradio as gr
import pandas as pd

def create_data_grid(data: pd.DataFrame):
    with gr.Blocks() as demo:
        gr.Markdown("# Data Grid")

        # Search bar
        search = gr.Textbox(label="Search", placeholder="Filter data...")

        # Data table
        table = gr.Dataframe(
            value=data,
            label="Data",
            interactive=False,
            wrap=True
        )

        # Filter handler
        def filter_data(search_term):
            if not search_term:
                return data
            mask = data.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
            return data[mask]

        search.change(filter_data, [search], [table])

    return demo
""",

    "master_detail_view": """
import gradio as gr

def create_master_detail(items: list):
    with gr.Blocks() as demo:
        with gr.Row():
            # Master list
            with gr.Column(scale=1):
                item_list = gr.Radio(
                    choices=[item['name'] for item in items],
                    label="Items"
                )

            # Detail view
            with gr.Column(scale=2):
                detail_view = gr.JSON(label="Details")

        # Selection handler
        def show_detail(item_name):
            item = next((i for i in items if i['name'] == item_name), {})
            return item

        item_list.change(show_detail, [item_list], [detail_view])

    return demo
""",

    # HIERARCHICAL NAVIGATION PATTERNS (moved from COMPONENTS for proper matching)
    "hierarchical_data_navigation_source_dataset_stage_files": """
import gradio as gr
from typing import Dict, List

# Pipeline data structure
PIPELINE_DATA = {pipeline_data}

def create_dashboard():
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# Hierarchical Data Navigator")

        # Four-level navigation: Source → Dataset → Stage → Files
        with gr.Row():
            source_dropdown = gr.Dropdown(
                choices=list(PIPELINE_DATA["sources"].keys()),
                label="Source",
                value=list(PIPELINE_DATA["sources"].keys())[0] if PIPELINE_DATA["sources"] else None,
                interactive=True
            )
            dataset_dropdown = gr.Dropdown(
                choices=[],
                label="Dataset",
                interactive=True
            )
            stage_dropdown = gr.Dropdown(
                choices=[],
                label="Stage",
                interactive=True
            )

        with gr.Row():
            refresh_btn = gr.Button("🔄 Refresh", size="sm")
            current_path = gr.Textbox(
                label="Current Path",
                value="",
                interactive=False
            )

        # File listing
        files_df = gr.Dataframe(
            headers=["Name", "Type", "Size", "Modified"],
            value=[],
            interactive=False,
            wrap=True,
            label="Files in Stage"
        )

        selected_file = gr.Textbox(
            label="Selected File",
            value="",
            interactive=False
        )

        # Event handlers
        def update_datasets(source_name):
            if not source_name or source_name not in PIPELINE_DATA["sources"]:
                return gr.Dropdown(choices=[]), gr.Dropdown(choices=[]), "", []
            datasets = list(PIPELINE_DATA["sources"][source_name].get("datasets", {}).keys())
            return (
                gr.Dropdown(choices=datasets, value=datasets[0] if datasets else None),
                gr.Dropdown(choices=[]),
                f"{source_name}",
                []
            )

        def update_stages(source_name, dataset_name):
            if not source_name or not dataset_name:
                return gr.Dropdown(choices=[]), "", []
            stages = ["downloads", "extracted", "parsed"]  # Common pipeline stages
            return (
                gr.Dropdown(choices=stages, value=stages[0] if stages else None),
                f"{source_name}/{dataset_name}",
                []
            )

        def update_files(source_name, dataset_name, stage_name):
            if not source_name or not dataset_name or not stage_name:
                return "", []
            path = f"{source_name}/{dataset_name}/{stage_name}"
            # Mock file listing (in real implementation, would scan directory)
            files = [
                ["file1.csv", "CSV", "1.2 MB", "2025-01-15"],
                ["file2.json", "JSON", "856 KB", "2025-01-15"],
                ["file3.parquet", "Parquet", "2.4 MB", "2025-01-14"]
            ]
            return path, files

        # Wire events
        source_dropdown.change(
            update_datasets,
            [source_dropdown],
            [dataset_dropdown, stage_dropdown, current_path, files_df]
        )
        dataset_dropdown.change(
            update_stages,
            [source_dropdown, dataset_dropdown],
            [stage_dropdown, current_path, files_df]
        )
        stage_dropdown.change(
            update_files,
            [source_dropdown, dataset_dropdown, stage_dropdown],
            [current_path, files_df]
        )

        # Auto-load on launch
        demo.load(update_datasets, [source_dropdown], [dataset_dropdown, stage_dropdown, current_path, files_df])

    return demo

if __name__ == "__main__":
    demo = create_dashboard()
    demo.launch()
""",

    "complete_hierarchical_folder_navigation_generic_works_for_any_structure": """
import gradio as gr
from typing import Dict, List

PIPELINE_DATA = {pipeline_data}

def create_dashboard():
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 📁 Folder Navigator")

        with gr.Row():
            base_path_input = gr.Textbox(
                label="Base Path",
                value="/",
                placeholder="Enter root directory path"
            )
            refresh_btn = gr.Button("🔄 Refresh", size="sm")

        current_path_display = gr.Textbox(
            label="Current Location",
            value="/",
            interactive=False
        )

        with gr.Row():
            up_btn = gr.Button("⬆️ Up", size="sm")
            home_btn = gr.Button("🏠 Home", size="sm")

        # Folder contents display
        folder_contents = gr.Dataframe(
            headers=["Type", "Name", "Size", "Modified"],
            datatype=["str", "str", "str", "str"],
            value=[
                ["Folder", "downloads", "-", "2025-01-15"],
                ["Folder", "extracted", "-", "2025-01-15"],
                ["Folder", "parsed", "-", "2025-01-14"],
                ["File", "metadata.json", "4 KB", "2025-01-15"]
            ],
            interactive=False,
            wrap=True,
            label="Contents"
        )

        with gr.Row():
            selected_item = gr.Textbox(
                label="Selected Item",
                value="",
                interactive=False
            )
            navigate_btn = gr.Button("📂 Open", size="sm", variant="primary")

        status_text = gr.Markdown("Ready")

        # Hidden state for current relative path
        current_relative_path = gr.State(value="")

        # Event handlers
        def go_up(current_path):
            if not current_path or current_path == "/":
                return "/", [], "Already at root"
            parts = current_path.rstrip("/").split("/")
            new_path = "/".join(parts[:-1]) or "/"
            return new_path, [], f"Navigated to {new_path}"

        def go_home():
            return "/", [], "Navigated to home"

        def navigate_into(selected, current):
            if not selected:
                return current, [], "No item selected"
            new_path = f"{current.rstrip('/')}/{selected}".replace("//", "/")
            return new_path, [], f"Navigated to {new_path}"

        # Wire events
        up_btn.click(go_up, [current_path_display], [current_path_display, folder_contents, status_text])
        home_btn.click(go_home, outputs=[current_path_display, folder_contents, status_text])
        navigate_btn.click(navigate_into, [selected_item, current_path_display], [current_path_display, folder_contents, status_text])

        folder_contents.select(
            lambda evt: evt.value[1] if evt.value else "",
            outputs=[selected_item]
        )

    return demo

if __name__ == "__main__":
    demo = create_dashboard()
    demo.launch()
""",

    "breadcrumb_navigation_pattern_works_at_any_depth": """
import gradio as gr
from typing import Dict, List

PIPELINE_DATA = {pipeline_data}

def create_dashboard():
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# Breadcrumb Navigation")

        breadcrumb_html = gr.HTML(value="<span style='color: #666;'>📁 Root</span>")

        # Current path display
        hidden_path = gr.Textbox(value="", visible=False, label="Path State")

        # Content area
        with gr.Column():
            content_title = gr.Markdown("### Root Directory")
            navigation_data = gr.Dataframe(
                headers=["Name", "Type", "Modified"],
                datatype=["str", "str", "str"],
                value=[
                    ["downloads", "Folder", "2025-01-15"],
                    ["extracted", "Folder", "2025-01-15"],
                    ["parsed", "Folder", "2025-01-14"]
                ],
                interactive=False,
                height=300,
                label="Contents"
            )

        # Navigation status
        nav_status = gr.Textbox(label="Status", value="Ready", interactive=False)

        # Helper functions
        def create_breadcrumb_html(current_path):
            if not current_path:
                return "<span style='color: #666;'>📁 Root</span>"

            parts = current_path.split('/')
            html_parts = ["<a href='#' style='color: #0066cc; text-decoration: none; cursor: pointer;' data-index='0'>📁 Root</a>"]

            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    html_parts.append(f"<span style='color: #333; font-weight: bold;'>{part}</span>")
                else:
                    html_parts.append(f"<a href='#' style='color: #0066cc; text-decoration: none; cursor: pointer;' data-index='{i+1}'>{part}</a>")

            return " / ".join(html_parts)

        def navigate_to_item(evt):
            if not evt or not evt.value:
                return "", create_breadcrumb_html(""), "No item selected", []

            item_name = evt.value[0]
            # Simulate navigation into folder
            new_path = item_name
            breadcrumb = create_breadcrumb_html(new_path)

            # Mock sub-contents
            sub_contents = [
                ["file1.csv", "File", "2025-01-15"],
                ["file2.json", "File", "2025-01-15"]
            ]

            return new_path, breadcrumb, f"Navigated to {new_path}", sub_contents

        # Wire events
        navigation_data.select(
            navigate_to_item,
            outputs=[hidden_path, breadcrumb_html, nav_status, navigation_data]
        )

        # Initialize breadcrumb
        demo.load(lambda: create_breadcrumb_html(""), outputs=[breadcrumb_html])

    return demo

if __name__ == "__main__":
    demo = create_dashboard()
    demo.launch()
""",

    # BEAUTIFUL M3 HIERARCHICAL NAVIGATION (Material Design 3 styled)
    "hierarchical_data_navigation_m3": """
import gradio as gr
from typing import Dict, List
import time

# Import M3 theme
from src.templates.m3_theme import get_m3_theme_css

# Lazy-load analyzer for dynamic data access
from src.analyzers.pipeline_context_analyzer import PipelineContextAnalyzer

# Pipeline summary (lightweight - no full data embedded!)
SUMMARY_DATA = {pipeline_data}

# Context cache to avoid re-scanning filesystem on every interaction
_CONTEXT_CACHE = None
_CACHE_TIMESTAMP = None
CACHE_TTL = 60  # seconds

def get_cached_context():
    \"\"\"Get pipeline context with caching to avoid repeated filesystem scans\"\"\"
    global _CONTEXT_CACHE, _CACHE_TIMESTAMP

    now = time.time()
    if _CONTEXT_CACHE is None or _CACHE_TIMESTAMP is None or (now - _CACHE_TIMESTAMP) > CACHE_TTL:
        analyzer = PipelineContextAnalyzer()
        _CONTEXT_CACHE = analyzer.generate_context_from_filesystem()
        _CACHE_TIMESTAMP = now

    return _CONTEXT_CACHE

def create_dashboard():
    # Use pre-calculated summary stats (instant!)
    total_sources = SUMMARY_DATA.get("total_sources", 0)
    total_datasets = SUMMARY_DATA.get("total_datasets", 0)
    processing_count = SUMMARY_DATA.get("processing_count", 0)

    with gr.Blocks(theme=gr.themes.Soft(), css=get_m3_theme_css()) as demo:
        # Beautiful gradient header with ETL branding
        gr.HTML(\"\"\"
        <div class="md-header-gradient md-fade-in">
            <h1 class="md-header-title">⚙️ ETL Pipeline Monitor</h1>
            <p class="md-header-subtitle">Monitor your petroleum data ingestion pipeline</p>
        </div>
        \"\"\")

        # ETL Pipeline Stage Visualization
        gr.HTML(\"\"\"
        <div class="md-card md-fade-in" style="margin: 16px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                <!-- Stage 1: Download -->
                <div style="flex: 1; min-width: 120px; text-align: center;">
                    <div style="background: rgba(255,255,255,0.95); border-radius: 12px; padding: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                        <div style="font-size: 32px; margin-bottom: 8px;">📥</div>
                        <div style="font-weight: 600; color: #1a1a1a; font-size: 14px; margin-bottom: 4px;">DOWNLOAD</div>
                        <div style="display: inline-block; background: #10b981; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">✓ COMPLETE</div>
                    </div>
                </div>

                <!-- Arrow -->
                <div style="color: white; font-size: 24px; font-weight: bold;">→</div>

                <!-- Stage 2: Extract -->
                <div style="flex: 1; min-width: 120px; text-align: center;">
                    <div style="background: rgba(255,255,255,0.95); border-radius: 12px; padding: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                        <div style="font-size: 32px; margin-bottom: 8px;">📦</div>
                        <div style="font-weight: 600; color: #1a1a1a; font-size: 14px; margin-bottom: 4px;">EXTRACT</div>
                        <div style="display: inline-block; background: #10b981; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">✓ COMPLETE</div>
                    </div>
                </div>

                <!-- Arrow -->
                <div style="color: white; font-size: 24px; font-weight: bold;">→</div>

                <!-- Stage 3: Parse -->
                <div style="flex: 1; min-width: 120px; text-align: center;">
                    <div style="background: rgba(255,255,255,0.95); border-radius: 12px; padding: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                        <div style="font-size: 32px; margin-bottom: 8px;">⚡</div>
                        <div style="font-weight: 600; color: #1a1a1a; font-size: 14px; margin-bottom: 4px;">PARSE</div>
                        <div style="display: inline-block; background: #10b981; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">✓ COMPLETE</div>
                    </div>
                </div>

                <!-- Arrow -->
                <div style="color: white; font-size: 24px; font-weight: bold;">→</div>

                <!-- Stage 4: Validate -->
                <div style="flex: 1; min-width: 120px; text-align: center;">
                    <div style="background: rgba(255,255,255,0.95); border-radius: 12px; padding: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                        <div style="font-size: 32px; margin-bottom: 8px;">✅</div>
                        <div style="font-weight: 600; color: #1a1a1a; font-size: 14px; margin-bottom: 4px;">VALIDATE</div>
                        <div style="display: inline-block; background: #6b7280; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">⏳ READY</div>
                    </div>
                </div>
            </div>
            <div style="margin-top: 16px; text-align: center; color: white; font-size: 13px; font-weight: 500;">
                ⚙️ Pipeline Status: <span style="background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 8px; font-weight: 600;">3/4 Stages Complete</span>
            </div>
        </div>
        \"\"\")

        with gr.Row():
            # Left sidebar: ETL Pipeline Metrics
            with gr.Column(scale=1, min_width=250):
                gr.HTML(\"\"\"
                <div class="md-slide-in">
                    <div style="margin-bottom: 12px; padding: 12px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; color: white; text-align: center;">
                        <div style="font-size: 13px; font-weight: 600; letter-spacing: 0.5px;">⚙️ PIPELINE HEALTH</div>
                    </div>

                    <div style="margin-bottom: 16px;">
                        <div class="md-card md-status-card md-status-card-success">
                            <div style="font-size: 32px; font-weight: 300; color: var(--md-success);">{}</div>
                            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--md-on-surface-variant);">🗂️ Petroleum Sources</div>
                            <div style="font-size: 10px; color: var(--md-on-surface-variant); margin-top: 4px;">FracFocus, RRC, USGS...</div>
                        </div>
                    </div>
                    <div style="margin-bottom: 16px;">
                        <div class="md-card md-status-card md-status-card-info">
                            <div style="font-size: 32px; font-weight: 300; color: var(--md-info);">{}</div>
                            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--md-on-surface-variant);">📊 Datasets Ingested</div>
                            <div style="font-size: 10px; color: var(--md-on-surface-variant); margin-top: 4px;">Ready for analysis</div>
                        </div>
                    </div>
                    <div style="margin-bottom: 16px;">
                        <div class="md-card md-status-card md-status-card-warning">
                            <div style="font-size: 32px; font-weight: 300; color: var(--md-warning);">{}</div>
                            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--md-on-surface-variant);">⏳ In Pipeline</div>
                            <div style="font-size: 10px; color: var(--md-on-surface-variant); margin-top: 4px;">Currently processing</div>
                        </div>
                    </div>

                    <div style="margin-top: 20px; padding: 12px; background: #f3f4f6; border-radius: 8px; border-left: 4px solid #10b981;">
                        <div style="font-size: 11px; font-weight: 600; color: #1a1a1a; margin-bottom: 6px;">✓ Pipeline Status</div>
                        <div style="font-size: 10px; color: #6b7280;">All critical stages operational</div>
                        <div style="font-size: 10px; color: #6b7280; margin-top: 2px;">Last refresh: Just now</div>
                    </div>
                </div>
                \"\"\".format(total_sources, total_datasets, processing_count))

            # Main content: ETL Data Explorer
            with gr.Column(scale=2):
                gr.Markdown("### 🔍 Explore Pipeline Data", elem_classes=["m3-title-large"])

                with gr.Row():
                    source_dropdown = gr.Dropdown(
                        choices=SUMMARY_DATA.get("source_names", []),
                        label="📁 Source",
                        value=SUMMARY_DATA.get("source_names", [None])[0] if SUMMARY_DATA.get("source_names") else None,
                        interactive=True,
                        elem_classes=["md-fade-in"]
                    )
                    dataset_dropdown = gr.Dropdown(
                        choices=[],
                        label="📊 Dataset",
                        interactive=True,
                        elem_classes=["md-fade-in"]
                    )
                    stage_dropdown = gr.Dropdown(
                        choices=[],
                        label="⚙️ Stage",
                        interactive=True,
                        elem_classes=["md-fade-in"]
                    )

                # Breadcrumb path display
                gr.HTML(\"\"\"
                <div class="md-card md-card-filled" style="margin: 16px 0;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 14px; color: var(--md-on-surface-variant); font-weight: 500;">📍 Current Path:</span>
                        <span id="breadcrumb-path" style="font-size: 14px; color: var(--md-primary); font-weight: 600;">Home</span>
                    </div>
                </div>
                \"\"\")

                current_path = gr.Textbox(
                    label="Current Path",
                    value="",
                    interactive=False,
                    visible=False
                )

                with gr.Row():
                    refresh_btn = gr.Button(
                        "🔄 Refresh",
                        size="sm",
                        variant="secondary",
                        elem_classes=["md-button-outlined"]
                    )

                # File listing with M3 styling
                gr.Markdown("### 📄 Files", elem_classes=["m3-title-medium"])
                files_df = gr.Dataframe(
                    headers=["Name", "Type", "Size", "Modified"],
                    value=[],
                    interactive=False,
                    wrap=True,
                    label="Files in Stage",
                    elem_classes=["md-data-table", "md-fade-in"]
                )

                # File selection info
                selected_file = gr.Textbox(
                    label="Selected File",
                    value="",
                    interactive=False,
                    visible=False
                )

        # Event handlers (using lazy loading with cache)
        def update_datasets(source_name):
            if not source_name:
                return gr.Dropdown(choices=[]), gr.Dropdown(choices=[]), "", []

            # Lazy load: Read from cached context dynamically
            context = get_cached_context()
            source_data = context.get("data_sources", {}).get(source_name, {})
            datasets = list(source_data.get("datasets", {}).keys())

            path = f"{{source_name}}"
            return (
                gr.Dropdown(choices=datasets, value=datasets[0] if datasets else None),
                gr.Dropdown(choices=[]),
                path,
                []
            )

        def update_stages(source_name, dataset_name):
            if not source_name or not dataset_name:
                return gr.Dropdown(choices=[]), "", []

            # Lazy load: Read from cached context dynamically
            try:
                context = get_cached_context()
                dataset = context.get("data_sources", {}).get(source_name, {}).get("datasets", {}).get(dataset_name, {})
                pipeline_stages = dataset.get("pipeline_stages", {})
                stages = list(pipeline_stages.keys())

                if not stages:
                    stages = ["downloads", "extracted", "parsed"]  # fallback
            except:
                stages = ["downloads", "extracted", "parsed"]  # fallback

            path = f"{{source_name}} / {{dataset_name}}"
            return (
                gr.Dropdown(choices=stages, value=stages[0] if stages else None),
                path,
                []
            )

        def update_files(source_name, dataset_name, stage_name):
            if not source_name or not dataset_name or not stage_name:
                return "", []
            path = f"{{source_name}} / {{dataset_name}} / {{stage_name}}"

            # Lazy load: Read from cached context dynamically
            files = []
            try:
                context = get_cached_context()
                dataset = context.get("data_sources", {}).get(source_name, {}).get("datasets", {}).get(dataset_name, {})
                stage_info = dataset.get("pipeline_stages", {}).get(stage_name, {})
                file_list = stage_info.get("files", [])

                for file_info in file_list:
                    filename = file_info.get("file", "unknown")
                    rows = file_info.get("rows", 0)
                    size_bytes = file_info.get("size_bytes", 0)
                    file_format = file_info.get("format", "").upper()

                    # Format size
                    if size_bytes > 1024**3:  # GB
                        size = f"{{size_bytes / (1024**3):.2f}} GB"
                    elif size_bytes > 1024**2:  # MB
                        size = f"{{size_bytes / (1024**2):.2f}} MB"
                    elif size_bytes > 1024:  # KB
                        size = f"{{size_bytes / 1024:.2f}} KB"
                    else:
                        size = f"{{size_bytes}} bytes"

                    # Format rows
                    rows_str = f"{{rows:,}} rows"

                    files.append([f"📄 {{filename}}", file_format, size, rows_str])

                if not files:
                    files = [[f"No files in {{{{stage_name}}}}", "", "", ""]]
            except Exception as e:
                files = [[f"Error loading files: {{{{str(e)}}}}", "", "", ""]]

            return path, files

        # Wire events
        source_dropdown.change(
            update_datasets,
            [source_dropdown],
            [dataset_dropdown, stage_dropdown, current_path, files_df]
        )
        dataset_dropdown.change(
            update_stages,
            [source_dropdown, dataset_dropdown],
            [stage_dropdown, current_path, files_df]
        )
        stage_dropdown.change(
            update_files,
            [source_dropdown, dataset_dropdown, stage_dropdown],
            [current_path, files_df]
        )

        # Auto-load on launch
        demo.load(
            update_datasets,
            [source_dropdown],
            [dataset_dropdown, stage_dropdown, current_path, files_df]
        )

    return demo

if __name__ == "__main__":
    demo = create_dashboard()
    demo.launch()
""",

    "pipeline_monitoring_m3": """
import gradio as gr
from typing import Dict, List
import time

# Import M3 theme
from src.templates.m3_theme import get_m3_theme_css

# Lazy-load analyzer for dynamic data access
from src.analyzers.pipeline_context_analyzer import PipelineContextAnalyzer

# Pipeline summary (lightweight - no full data embedded!)
SUMMARY_DATA = {pipeline_data}

# Context cache
_CONTEXT_CACHE = None
_CACHE_TIMESTAMP = None
CACHE_TTL = 60

def get_cached_context():
    global _CONTEXT_CACHE, _CACHE_TIMESTAMP
    now = time.time()
    if _CONTEXT_CACHE is None or _CACHE_TIMESTAMP is None or (now - _CACHE_TIMESTAMP) > CACHE_TTL:
        # Use saved context which has pipeline stage metadata
        from shared_state import PipelineState
        _CONTEXT_CACHE = PipelineState.load_context(check_freshness=False)
        _CACHE_TIMESTAMP = now
    return _CONTEXT_CACHE

def create_dashboard():
    total_sources = SUMMARY_DATA.get("total_sources", 0)
    total_datasets = SUMMARY_DATA.get("total_datasets", 0)
    processing_count = SUMMARY_DATA.get("processing_count", 0)

    with gr.Blocks(theme=gr.themes.Soft(), css=get_m3_theme_css()) as demo:
        # Header
        gr.HTML('''
        <div class="md-header-gradient md-fade-in">
            <h1 class="md-header-title">⚙️ ETL Pipeline Monitor</h1>
            <p class="md-header-subtitle">Petroleum Data Ingestion Pipeline</p>
        </div>
        ''')

        # Pipeline Stage Visualization
        gr.HTML('''
        <div class="md-card md-fade-in" style="margin: 16px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                <div style="flex: 1; min-width: 120px; text-align: center;">
                    <div style="background: rgba(255,255,255,0.95); border-radius: 12px; padding: 16px;">
                        <div style="font-size: 32px; margin-bottom: 8px;">📥</div>
                        <div style="font-weight: 600; font-size: 14px; margin-bottom: 4px;">DOWNLOAD</div>
                        <div style="display: inline-block; background: #10b981; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">✓ COMPLETE</div>
                    </div>
                </div>
                <div style="color: white; font-size: 24px; font-weight: bold;">→</div>
                <div style="flex: 1; min-width: 120px; text-align: center;">
                    <div style="background: rgba(255,255,255,0.95); border-radius: 12px; padding: 16px;">
                        <div style="font-size: 32px; margin-bottom: 8px;">📦</div>
                        <div style="font-weight: 600; font-size: 14px; margin-bottom: 4px;">EXTRACT</div>
                        <div style="display: inline-block; background: #10b981; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">✓ COMPLETE</div>
                    </div>
                </div>
                <div style="color: white; font-size: 24px; font-weight: bold;">→</div>
                <div style="flex: 1; min-width: 120px; text-align: center;">
                    <div style="background: rgba(255,255,255,0.95); border-radius: 12px; padding: 16px;">
                        <div style="font-size: 32px; margin-bottom: 8px;">⚡</div>
                        <div style="font-weight: 600; font-size: 14px; margin-bottom: 4px;">PARSE</div>
                        <div style="display: inline-block; background: #10b981; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">✓ COMPLETE</div>
                    </div>
                </div>
                <div style="color: white; font-size: 24px; font-weight: bold;">→</div>
                <div style="flex: 1; min-width: 120px; text-align: center;">
                    <div style="background: rgba(255,255,255,0.95); border-radius: 12px; padding: 16px;">
                        <div style="font-size: 32px; margin-bottom: 8px;">✅</div>
                        <div style="font-weight: 600; font-size: 14px; margin-bottom: 4px;">VALIDATE</div>
                        <div style="display: inline-block; background: #6b7280; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">⏳ READY</div>
                    </div>
                </div>
            </div>
            <div style="margin-top: 16px; text-align: center; color: white; font-size: 13px; font-weight: 500;">
                ⚙️ Pipeline Status: <span style="background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 8px; font-weight: 600;">3/4 Stages Complete</span>
            </div>
        </div>
        ''')

        with gr.Row():
            # Left: Dataset Tree View
            with gr.Column(scale=1, min_width=300):
                gr.Markdown("### 📁 Dataset Explorer")

                # Search/Filter
                search_box = gr.Textbox(
                    placeholder="Search datasets and files...",
                    label="🔍 Search",
                    elem_classes=["md-fade-in"]
                )

                # Dataset tree (using Radio for now, will enhance to tree)
                dataset_tree = gr.Radio(
                    choices=[],
                    label="Datasets",
                    elem_classes=["md-fade-in"]
                )

                # Pipeline health summary
                gr.HTML(f'''
                <div style="margin-top: 20px; padding: 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; color: white;">
                    <div style="font-size: 13px; font-weight: 600; margin-bottom: 12px; text-align: center;">⚙️ PIPELINE HEALTH</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div style="text-align: center;">
                            <div style="font-size: 24px; font-weight: 300;">{total_sources}</div>
                            <div style="font-size: 10px; opacity: 0.9;">Sources</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 24px; font-weight: 300;">{total_datasets}</div>
                            <div style="font-size: 10px; opacity: 0.9;">Datasets</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 24px; font-weight: 300;">{processing_count}</div>
                            <div style="font-size: 10px; opacity: 0.9;">Processing</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 24px; font-weight: 300; color: #10b981;">✓</div>
                            <div style="font-size: 10px; opacity: 0.9;">Healthy</div>
                        </div>
                    </div>
                </div>
                ''')

            # Center: File Browser with Per-Dataset Status
            with gr.Column(scale=2):
                gr.Markdown("### 📊 Dataset Status & Files")

                # Per-dataset status card (dynamic)
                dataset_status = gr.HTML('''
                <div class="md-card" style="padding: 16px; margin-bottom: 16px; background: #f9fafb;">
                    <div style="color: #6b7280; font-size: 14px;">Select a dataset to view details</div>
                </div>
                ''')

                # File list table
                file_table = gr.Dataframe(
                    headers=["Name", "Type", "Size", "Records", "Status"],
                    datatype=["str", "str", "str", "str", "str"],
                    label="Files in Stage",
                    elem_classes=["md-fade-in"]
                )

                # Breadcrumb
                breadcrumb = gr.Textbox(
                    value="Home",
                    label="📍 Current Path",
                    interactive=False
                )

            # Right: File Preview Panel
            with gr.Column(scale=1, min_width=300):
                gr.Markdown("### 👁️ File Preview")

                # File metadata
                file_metadata = gr.HTML('''
                <div class="md-card" style="padding: 16px; background: #f9fafb;">
                    <div style="color: #6b7280; font-size: 13px; text-align: center;">
                        Select a file to preview
                    </div>
                </div>
                ''')

                # Column info
                gr.Markdown("**Columns**")
                column_table = gr.Dataframe(
                    headers=["Column", "Type"],
                    datatype=["str", "str"],
                    label="Schema",
                    elem_classes=["md-fade-in"]
                )

                # Sample data
                gr.Markdown("**Sample Data**")
                sample_data = gr.Dataframe(
                    label="First 5 Rows",
                    elem_classes=["md-fade-in"]
                )

        # Load initial dataset list
        def load_datasets():
            context = get_cached_context()
            data_sources = context.get("data_sources", {})
            dataset_list = []

            for source_name, source_data in data_sources.items():
                datasets = source_data.get("datasets", {})
                if datasets:
                    for ds_name in datasets.keys():
                        dataset_list.append(f"{source_name} / {ds_name}")
                else:
                    dataset_list.append(source_name)

            return gr.Radio(choices=dataset_list, value=dataset_list[0] if dataset_list else None)

        # Show dataset status when selected
        def show_dataset_status(selected_dataset):
            if not selected_dataset:
                return "<div>No dataset selected</div>", [], "Home"

            context = get_cached_context()
            data_sources = context.get("data_sources", {})

            # Parse selection
            if "/" in selected_dataset:
                source_name, ds_name = [p.strip() for p in selected_dataset.split("/")]
                source_data = data_sources.get(source_name, {})
                dataset_info = source_data.get("datasets", {}).get(ds_name, {})
            else:
                source_name = selected_dataset
                source_data = data_sources.get(source_name, {})
                dataset_info = source_data

            # Get pipeline stages
            pipeline_stages = dataset_info.get("pipeline_stages", {})
            status = dataset_info.get("status", "unknown")

            # Count files and records
            total_files = 0
            total_records = 0
            for stage_name, stage_info in pipeline_stages.items():
                total_files += stage_info.get("total_files", 0)
                total_records += stage_info.get("total_rows", 0)

            # Status badge color
            status_color = "#10b981" if status == "ready" else "#6b7280"

            # Generate status card
            status_html = f'''
            <div class="md-card" style="padding: 20px; background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 16px;">
                    <div>
                        <div style="font-size: 18px; font-weight: 600; color: #1a1a1a; margin-bottom: 4px;">{selected_dataset}</div>
                        <div style="display: inline-block; background: {status_color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">{status.upper()}</div>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 16px;">
                    <div style="text-align: center; padding: 12px; background: white; border-radius: 8px;">
                        <div style="font-size: 20px; font-weight: 600; color: #667eea;">{total_files}</div>
                        <div style="font-size: 11px; color: #6b7280;">Files</div>
                    </div>
                    <div style="text-align: center; padding: 12px; background: white; border-radius: 8px;">
                        <div style="font-size: 20px; font-weight: 600; color: #10b981;">{total_records:,}</div>
                        <div style="font-size: 11px; color: #6b7280;">Records</div>
                    </div>
                    <div style="text-align: center; padding: 12px; background: white; border-radius: 8px;">
                        <div style="font-size: 20px; font-weight: 600; color: #f59e0b;">{len(pipeline_stages)}</div>
                        <div style="font-size: 11px; color: #6b7280;">Stages</div>
                    </div>
                </div>
            </div>
            '''

            # Build file list
            file_rows = []
            for stage_name, stage_info in pipeline_stages.items():
                files = stage_info.get("files", [])

                # DEFENSIVE: Handle both Format A (list) and Format B (int)
                if isinstance(files, list):
                    # Format A: Detailed file list from metadata path
                    for file_info in files[:10]:  # Limit to 10 files
                        file_rows.append([
                            file_info.get("file", "Unknown"),
                            file_info.get("format", "csv").upper(),
                            f"{file_info.get('size_bytes', 0) / 1024 / 1024:.2f} MB",
                            f"{file_info.get('rows', 0):,}",
                            "✓ Complete"
                        ])
                else:
                    # Format B: Aggregated stats from filesystem scan
                    total_files = stage_info.get("total_files", files if isinstance(files, int) else 0)
                    total_size = stage_info.get("total_size_bytes", stage_info.get("size_bytes", 0))
                    total_rows = stage_info.get("total_rows", 0)

                    if total_files > 0:
                        file_rows.append([
                            f"{stage_name} - {total_files} files",
                            "Multiple",
                            f"{total_size / 1024 / 1024:.2f} MB",
                            f"{total_rows:,}",
                            "✓ Complete"
                        ])

            return status_html, file_rows, f"Home / {selected_dataset}"

        # Wire up events
        demo.load(load_datasets, None, dataset_tree)
        dataset_tree.change(show_dataset_status, dataset_tree, [dataset_status, file_table, breadcrumb])

    return demo

if __name__ == "__main__":
    demo = create_dashboard()
    demo.launch()
""",

    "pipeline_explorer_m3_beautiful": """
import gradio as gr
from typing import Dict, List
import time

# Import M3 theme
from src.templates.m3_theme import get_m3_theme_css

# Lazy-load analyzer for dynamic data access
from src.analyzers.pipeline_context_analyzer import PipelineContextAnalyzer

# Pipeline summary
SUMMARY_DATA = {pipeline_data}

# Context cache
_CONTEXT_CACHE = None
_CACHE_TIMESTAMP = None
CACHE_TTL = 60

def get_cached_context():
    global _CONTEXT_CACHE, _CACHE_TIMESTAMP
    now = time.time()
    if _CONTEXT_CACHE is None or _CACHE_TIMESTAMP is None or (now - _CACHE_TIMESTAMP) > CACHE_TTL:
        # Use saved context which has pipeline stage metadata
        from shared_state import PipelineState
        _CONTEXT_CACHE = PipelineState.load_context(check_freshness=False)
        _CACHE_TIMESTAMP = now
    return _CONTEXT_CACHE

# Beautiful hexagon 3D pipeline CSS
HEXAGON_PIPELINE_CSS = '''
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

.pipeline-container {{{{
    font-family: 'Inter', sans-serif;
    padding: 40px 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    margin: 20px;
}}}}

.pipeline-stages {{{{
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 40px;
    flex-wrap: wrap;
    position: relative;
}}}}

.stage-hexagon {{{{
    position: relative;
    width: 140px;
    height: 140px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.95);
    clip-path: polygon(30% 0%, 70% 0%, 100% 50%, 70% 100%, 30% 100%, 0% 50%);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
}}}}

.stage-hexagon:hover {{{{
    transform: translateY(-8px) scale(1.05);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4), 0 0 0 2px rgba(255, 255, 255, 0.2);
}}}}

.stage-hexagon.complete {{{{
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
}}}}

.stage-hexagon.in-progress {{{{
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    color: white;
    animation: pulse 2s ease-in-out infinite;
}}}}

.stage-hexagon.pending {{{{
    background: linear-gradient(135deg, #e5e7eb 0%, #d1d5db 100%);
    color: #6b7280;
}}}}

@keyframes pulse {{{{
    0%, 100% {{{{ opacity: 1; }}}}
    50% {{{{ opacity: 0.7; }}}}
}}}}

.stage-icon {{{{
    font-size: 40px;
    margin-bottom: 8px;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}}}}

.stage-label {{{{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    text-align: center;
}}}}

.stage-badge {{{{
    position: absolute;
    bottom: -15px;
    left: 50%;
    transform: translateX(-50%);
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #10b981;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    font-weight: 600;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}}}}

.stage-connector {{{{
    width: 40px;
    height: 3px;
    background: rgba(255, 255, 255, 0.3);
    position: relative;
}}}}

.stage-connector::after {{{{
    content: '';
    position: absolute;
    right: -6px;
    top: -3px;
    width: 0;
    height: 0;
    border-left: 6px solid rgba(255, 255, 255, 0.3);
    border-top: 4px solid transparent;
    border-bottom: 4px solid transparent;
}}}}

.pipeline-title {{{{
    text-align: center;
    color: white;
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 30px;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}}}}

.pipeline-subtitle {{{{
    text-align: center;
    color: rgba(255, 255, 255, 0.9);
    font-size: 14px;
    font-weight: 400;
    margin-top: -20px;
    margin-bottom: 30px;
}}}}

.dataset-card {{{{
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin: 16px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    transition: all 0.2s ease;
}}}}

.dataset-card:hover {{{{
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    transform: translateY(-2px);
}}}}

.metric-card {{{{
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 10px;
    padding: 16px;
    text-align: center;
}}}}

.metric-value {{{{
    font-size: 32px;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}}}

.metric-label {{{{
    font-size: 12px;
    color: #6b7280;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 4px;
}}}}
'''

def create_dashboard():
    total_sources = SUMMARY_DATA.get("total_sources", 0)
    total_datasets = SUMMARY_DATA.get("total_datasets", 0)

    with gr.Blocks(theme=gr.themes.Soft(), css=get_m3_theme_css() + HEXAGON_PIPELINE_CSS) as demo:
        # Header
        gr.HTML('''
        <div class="md-header-gradient md-fade-in">
            <h1 class="md-header-title">⚙️ ETL Pipeline Explorer</h1>
            <p class="md-header-subtitle">Interactive Petroleum Data Pipeline Monitor</p>
        </div>
        ''')

        with gr.Row():
            # Left: Dataset Navigator
            with gr.Column(scale=1, min_width=280):
                gr.Markdown("### 📁 Datasets")

                dataset_selector = gr.Radio(
                    choices=[],
                    label="Select Dataset",
                    elem_classes=["md-fade-in"]
                )

                gr.HTML(f'''
                <div class="dataset-card" style="margin-top: 20px;">
                    <div class="metric-card">
                        <div class="metric-value">{{total_sources}}</div>
                        <div class="metric-label">Data Sources</div>
                    </div>
                    <div class="metric-card" style="margin-top: 12px;">
                        <div class="metric-value">{{total_datasets}}</div>
                        <div class="metric-label">Datasets Ready</div>
                    </div>
                </div>
                ''')

            # Right: Pipeline Visualization + File Browser
            with gr.Column(scale=3):
                # Per-dataset pipeline visualization (dynamic)
                pipeline_viz = gr.HTML('''
                <div class="pipeline-container">
                    <div class="pipeline-title">Select a dataset to view pipeline</div>
                </div>
                ''')

                # Stage selector
                with gr.Row():
                    stage_selector = gr.Radio(
                        choices=[],
                        label="📦 Pipeline Stage",
                        elem_classes=["md-fade-in"]
                    )

                # File browser
                gr.Markdown("### 📄 Files")
                files_table = gr.Dataframe(
                    headers=["File", "Format", "Size", "Records", "Status"],
                    datatype=["str", "str", "str", "str", "str"],
                    label="Files in Stage",
                    elem_classes=["md-fade-in"]
                )

                # File preview
                with gr.Accordion("🔍 File Preview", open=False):
                    file_info = gr.JSON(label="File Metadata")

        # Load datasets on startup
        def load_datasets():
            context = get_cached_context()
            data_sources = context.get("data_sources", {{}})
            dataset_list = []

            for source_name, source_data in data_sources.items():
                display_name = source_data.get("display_name", source_name)
                # Show all data sources that have pipeline stages
                if display_name and (source_data.get("parsed") or source_data.get("extracted") or source_data.get("downloads")):
                    dataset_list.append(display_name)

            return gr.Radio(choices=sorted(dataset_list), value=dataset_list[0] if dataset_list else None)

        # Show pipeline for selected dataset
        def show_pipeline(selected_dataset):
            if not selected_dataset:
                return '''
                <div class="pipeline-container">
                    <div class="pipeline-title">Select a dataset</div>
                </div>
                ''', gr.Radio(choices=[]), []

            context = get_cached_context()
            data_sources = context.get("data_sources", {{}})

            # Find the dataset
            dataset_info = None
            for source_name, source_data in data_sources.items():
                if source_data.get("display_name") == selected_dataset:
                    dataset_info = source_data
                    break

            if not dataset_info:
                return '''<div class="pipeline-container"><div class="pipeline-title">Dataset not found</div></div>''', gr.Radio(choices=[]), []

            # Get stage information
            stages_info = []
            stage_names = []
            for stage in ["downloads", "extracted", "parsed"]:
                stage_data = dataset_info.get(stage, {{}})
                if stage_data:
                    status = stage_data.get("status", "pending")
                    total_files = stage_data.get("total_files", 0)
                    stages_info.append((stage, status, total_files))
                    stage_names.append(stage.capitalize())

            # Build beautiful hexagon pipeline
            stage_icons = {{
                "downloads": "📥",
                "extracted": "📦",
                "parsed": "⚡"
            }}

            stage_html = '<div class="pipeline-container"><div class="pipeline-title">' + selected_dataset + ' Pipeline</div><div class="pipeline-subtitle">Click stages below to explore files</div><div class="pipeline-stages">'

            for i, (stage, status, files) in enumerate(stages_info):
                status_class = "complete" if status == "complete" else ("in-progress" if files > 0 else "pending")
                badge = "✓" if status == "complete" else str(files)

                stage_html += f'''
                <div class="stage-hexagon {{status_class}}">
                    <div class="stage-icon">{{stage_icons.get(stage, "📁")}}</div>
                    <div class="stage-label">{{stage.upper()}}</div>
                    <div class="stage-badge">{{badge}}</div>
                </div>
                '''

                if i < len(stages_info) - 1:
                    stage_html += '<div class="stage-connector"></div>'

            stage_html += '</div></div>'

            return stage_html, gr.Radio(choices=stage_names, value=stage_names[0] if stage_names else None), []

        # Show files for selected stage
        def show_files(selected_dataset, selected_stage):
            if not selected_dataset or not selected_stage:
                return []

            context = get_cached_context()
            data_sources = context.get("data_sources", {{}})

            dataset_info = None
            for source_name, source_data in data_sources.items():
                if source_data.get("display_name") == selected_dataset:
                    dataset_info = source_data
                    break

            if not dataset_info:
                return []

            stage = selected_stage.lower()
            stage_data = dataset_info.get(stage, {{}})
            files = stage_data.get("files", [])

            file_rows = []
            if isinstance(files, list):
                for file_info in files[:20]:
                    file_rows.append([
                        file_info.get("file", "Unknown"),
                        file_info.get("format", "csv").upper(),
                        f"{{file_info.get('size_bytes', 0) / 1024 / 1024:.2f}} MB",
                        f"{{file_info.get('rows', 0):,}}",
                        "✓ Complete"
                    ])
            else:
                total_files = stage_data.get("total_files", files if isinstance(files, int) else 0)
                total_size = stage_data.get("total_size_bytes", 0)
                total_rows = stage_data.get("total_rows", 0)

                if total_files > 0:
                    file_rows.append([
                        f"{{stage}} - all files",
                        "Multiple",
                        f"{{total_size / 1024 / 1024:.2f}} MB",
                        f"{{total_rows:,}}",
                        "✓ Complete"
                    ])

            return file_rows

        # Wire up events
        demo.load(load_datasets, None, dataset_selector)
        dataset_selector.change(show_pipeline, dataset_selector, [pipeline_viz, stage_selector, files_table])
        stage_selector.change(show_files, [dataset_selector, stage_selector], files_table)

    return demo

if __name__ == "__main__":
    demo = create_dashboard()
    demo.launch()
"""
}


# ============================================================================
# SNIPPET ASSEMBLER
# ============================================================================

class SnippetAssembler:
    """
    Assembles pre-validated code snippets instead of generating from scratch.

    Extreme Token Optimization:
    - Pattern matching: 100 tokens
    - Snippet assembly: 0 tokens (no LLM needed!)
    - Validation: 200 tokens
    - Total: 300 tokens vs 8,000+ for generation
    """

    def __init__(self, enable_gradient: bool = False):
        self.components = COMPONENTS
        self.interactions = INTERACTIONS
        self.patterns = PATTERNS
        self.semantic_scorer = None

        # Pattern mapping: virtual gradient patterns → real M3 implementations
        self.pattern_mappings = {
            "pipeline_navigation": "pipeline_monitoring_m3",
            "pipeline_monitoring": "pipeline_monitoring_m3",
            "data_exploration": "hierarchical_data_navigation_m3",
            "etl_monitoring": "pipeline_monitoring_m3",
            "data_pipeline": "pipeline_monitoring_m3"
        }

        # Optional gradient field enhancement (Phase 1)
        if enable_gradient:
            try:
                from src.templates.gradient_pattern_scorer import SemanticFieldScorer
                self.semantic_scorer = SemanticFieldScorer()
                print("[Gradient] Semantic field scoring enabled")
            except ImportError as e:
                print(f"[Gradient] Scorer not found, using base scoring: {e}")

    def get_pattern(self, pattern_name: str, **kwargs) -> str:
        """
        Get a complete pattern with variable substitution.

        Args:
            pattern_name: Pattern ID (e.g., 'pipeline_navigation')
            **kwargs: Variables to substitute (e.g., pipeline_data={...})

        Returns:
            Complete, working Gradio code
        """
        # Map virtual gradient patterns to real M3 implementations
        actual_pattern = self.pattern_mappings.get(pattern_name, pattern_name)

        if actual_pattern != pattern_name:
            print(f"  [Pattern Mapping] {pattern_name} → {actual_pattern}")

        if actual_pattern not in self.patterns:
            raise ValueError(f"Unknown pattern: {actual_pattern} (requested: {pattern_name})")

        template = self.patterns[actual_pattern]

        # Simple variable substitution
        for key, value in kwargs.items():
            template = template.replace(f"{{{key}}}", str(value))

        return template

    def assemble_dashboard(
        self,
        components: List[str],
        interactions: List[str],
        data: Dict = None
    ) -> str:
        """
        Assemble a custom dashboard from component snippets.

        This is the EXTREME optimization - no LLM generation, just string assembly!

        Args:
            components: List of component IDs to include
            interactions: List of interaction pattern IDs
            data: Data to pass to components

        Returns:
            Working Gradio code
        """
        # Build imports
        code = "import gradio as gr\n"
        code += "from typing import Dict, List, Any\n\n"

        # Add data
        if data:
            code += f"PIPELINE_DATA = {data}\n\n"

        # Build main function
        code += "def create_dashboard():\n"
        code += "    with gr.Blocks(theme=gr.themes.Soft()) as demo:\n"

        # Add components
        for comp_id in components:
            if comp_id in self.components:
                snippet = self.components[comp_id]
                # Indent for Blocks context
                indented = "        " + snippet.replace("\n", "\n        ")
                code += indented + "\n"

        # Add interactions
        code += "\n        # Event Handlers\n"
        for inter_id in interactions:
            if inter_id in self.interactions:
                snippet = self.interactions[inter_id]
                indented = "        " + snippet.replace("\n", "\n        ")
                code += indented + "\n"

        # Close function
        code += "    return demo\n\n"
        code += "if __name__ == '__main__':\n"
        code += "    demo = create_dashboard()\n"
        code += "    demo.launch()\n"

        return code

    def match_pattern(self, requirements: Dict) -> str:
        """
        Match user requirements to a pattern using specificity scoring (0 tokens).

        Scoring Logic:
        - More specific keyword matches = higher score
        - Hierarchical patterns score higher when design indicates multi-level structure
        - Generic patterns are fallback when no specific match found

        Architecture Compliance: 0 tokens (pure algorithmic matching, no LLM)

        Returns:
            Pattern ID with highest relevance score
        """
        screen_type = requirements.get('screen_type', '').lower()
        intent = requirements.get('intent', '').lower()

        # Combine for full text search
        search_text = f"{screen_type} {intent}"

        # Pattern scoring: keyword → points mapping
        pattern_scores = {}

        for pattern_id in self.patterns.keys():
            score = 0
            pattern_lower = pattern_id.lower()

            # SPECIFICITY SCORING (more keywords = more specific)

            # M3 BEAUTIFUL VARIANTS (highest priority - add +10 bonus)
            # This ensures M3 styled patterns are always preferred over basic ones
            m3_bonus = 10 if '_m3' in pattern_lower else 0
            score += m3_bonus

            # Hierarchical navigation patterns (highest priority for multi-level data)
            if 'hierarchical' in pattern_lower:
                score += 5  # Base score for hierarchical patterns
                if 'hierarchical' in search_text:
                    score += 3  # Exact match bonus
                if 'navigation' in search_text:
                    score += 2
                if 'source' in search_text or 'dataset' in search_text or 'stage' in search_text:
                    score += 2  # Multi-level indicators
                if 'folder' in search_text or 'file' in search_text:
                    score += 2

            # Breadcrumb patterns
            elif 'breadcrumb' in pattern_lower:
                score += 4
                if 'breadcrumb' in search_text:
                    score += 3
                if 'navigation' in search_text:
                    score += 2

            # Bidirectional navigation
            elif 'bidirectional' in pattern_lower:
                score += 4
                if 'back' in search_text or 'forward' in search_text or 'bidirectional' in search_text:
                    score += 3
                if 'navigation' in search_text:
                    score += 2

            # Folder navigation
            elif 'folder' in pattern_lower and 'navigation' in pattern_lower:
                score += 4
                if 'folder' in search_text:
                    score += 3
                if 'navigation' in search_text:
                    score += 2

            # Master-detail patterns
            elif 'master' in pattern_lower or 'detail' in pattern_lower:
                score += 3
                if 'master' in search_text or 'detail' in search_text:
                    score += 3
                if 'view' in search_text:
                    score += 1

            # Data grid patterns
            elif 'grid' in pattern_lower or 'table' in pattern_lower:
                score += 3
                if 'grid' in search_text or 'table' in search_text:
                    score += 3
                if 'data' in search_text:
                    score += 1

            # Dashboard patterns
            elif 'dashboard' in pattern_lower:
                score += 3
                if 'dashboard' in search_text:
                    score += 3
                if 'sidebar' in search_text and 'sidebar' in pattern_lower:
                    score += 2

            # Simple pipeline navigation (lowest priority - fallback)
            elif pattern_lower == 'pipeline_navigation':
                score += 1  # Very low base score
                if 'pipeline' in search_text:
                    score += 2
                if 'navigation' in search_text:
                    score += 1

            # Generic navigation patterns
            elif 'navigation' in pattern_lower:
                score += 2
                if 'navigation' in search_text:
                    score += 2

            # Apply gradient field augmentation if enabled (Phase 1)
            if self.semantic_scorer:
                score = self.semantic_scorer.augment_score(pattern_id, score, requirements)

            pattern_scores[pattern_id] = score

        # Return pattern with highest score
        if pattern_scores:
            best_pattern = max(pattern_scores.items(), key=lambda x: x[1])
            # Log top 5 scores for debugging
            top_scores = sorted(pattern_scores.items(), key=lambda x: x[1], reverse=True)[:5]
            print(f"  [Pattern Matching] Top scores: {dict(top_scores)}")
            print(f"  [Pattern Matching] Selected: {best_pattern[0]} (score: {best_pattern[1]})")
            return best_pattern[0]

        # Ultimate fallback
        return 'pipeline_navigation'


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    assembler = SnippetAssembler()

    # Example 1: Get complete pattern (0 tokens!)
    code = assembler.get_pattern(
        'pipeline_navigation',
        pipeline_data={"sources": {"rrc": {"datasets": {}}}}
    )
    print(f"Pattern code: {len(code)} chars")

    # Example 2: Assemble custom dashboard (0 tokens!)
    code = assembler.assemble_dashboard(
        components=['data_source_cards', 'file_browser'],
        interactions=['source_to_dataset_nav'],
        data={"sources": {}}
    )
    print(f"Custom dashboard: {len(code)} chars")

    # Example 3: Pattern matching (100 tokens via LLM)
    requirements = {'screen_type': 'pipeline_dashboard', 'intent': 'navigation'}
    pattern = assembler.match_pattern(requirements)
    print(f"Matched pattern: {pattern}")