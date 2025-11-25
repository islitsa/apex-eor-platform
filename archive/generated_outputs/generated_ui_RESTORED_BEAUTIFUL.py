import gradio as gr
from datetime import datetime, timedelta
import random

def get_m3_theme_css():
    return """
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');
    
    :root {
        --md-sys-color-primary: #1976d2;
        --md-sys-color-on-primary: #ffffff;
        --md-sys-color-surface: #ffffff;
        --md-sys-color-on-surface: #1c1b1f;
        --md-sys-color-on-surface-variant: #49454f;
        --md-sys-color-surface-variant: #e7e0ec;
        --md-sys-color-error: #ba1a1a;
        --md-sys-color-success: #2e7d32;
        --md-elevation-1: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        --md-elevation-2: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23);
    }
    
    .material-symbols-rounded {
        font-family: 'Material Symbols Rounded';
        font-weight: normal;
        font-style: normal;
        font-size: 24px;
        line-height: 1;
        letter-spacing: normal;
        text-transform: none;
        display: inline-block;
        white-space: nowrap;
        word-wrap: normal;
        direction: ltr;
        -webkit-font-feature-settings: 'liga';
        -webkit-font-smoothing: antialiased;
    }
    
    .md-48 { font-size: 48px; }
    .md-64 { font-size: 64px; }
    
    .dashboard-container {
        display: grid;
        grid-template-columns: 280px 1fr 320px;
        grid-template-rows: 64px 1fr;
        grid-template-areas: 
            "header header header"
            "sidebar main preview";
        height: 100vh;
        gap: 0;
        font-family: 'Roboto', sans-serif;
    }
    
    .dashboard-header {
        grid-area: header;
        background: var(--md-sys-color-surface);
        border-bottom: 1px solid var(--md-sys-color-surface-variant);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 32px;
        box-shadow: var(--md-elevation-1);
    }
    
    .header-title {
        display: flex;
        align-items: center;
        gap: 16px;
        font-size: 28px;
        font-weight: 700;
        color: var(--md-sys-color-on-surface);
    }
    
    .header-stats {
        display: flex;
        align-items: center;
        gap: 32px;
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-value {
        font-size: 24px;
        font-weight: 700;
        color: var(--md-sys-color-primary);
        display: block;
    }
    
    .stat-label {
        font-size: 14px;
        color: var(--md-sys-color-on-surface-variant);
    }
    
    .dashboard-sidebar {
        grid-area: sidebar;
        background: var(--md-sys-color-surface);
        border-right: 1px solid var(--md-sys-color-surface-variant);
        padding: 24px 16px;
        overflow-y: auto;
    }
    
    .dashboard-main {
        grid-area: main;
        padding: 24px;
        overflow-y: auto;
        background: #fafafa;
    }
    
    .dashboard-preview {
        grid-area: preview;
        background: var(--md-sys-color-surface);
        border-left: 1px solid var(--md-sys-color-surface-variant);
        padding: 24px;
        overflow-y: auto;
    }
    
    .cards-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
        gap: 24px;
    }
    
    .md-card-elevated {
        background: var(--md-sys-color-surface);
        border-radius: 16px;
        padding: 20px;
        box-shadow: var(--md-elevation-1);
        transition: box-shadow 150ms ease;
        min-height: 140px;
        cursor: pointer;
    }
    
    .md-card-elevated:hover {
        box-shadow: var(--md-elevation-2);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
    }
    
    .card-title {
        font-size: 20px;
        font-weight: 700;
        color: var(--md-sys-color-on-surface);
        margin: 0;
    }
    
    .card-subtitle {
        font-size: 14px;
        color: var(--md-sys-color-on-surface-variant);
        margin: 4px 0 16px 0;
    }
    
    .pipeline-stages {
        display: flex;
        gap: 8px;
        margin-bottom: 16px;
        align-items: center;
    }
    
    .stage-indicator {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        position: relative;
    }
    
    .md-status-circle-success {
        background: var(--md-sys-color-success);
        color: white;
    }
    
    .md-status-circle-pending {
        background: #ff9800;
        color: white;
    }
    
    .md-status-circle-error {
        background: var(--md-sys-color-error);
        color: white;
    }
    
    .md-status-circle-inactive {
        background: #e0e0e0;
        color: #9e9e9e;
    }
    
    .stage-connector {
        width: 24px;
        height: 2px;
        background: #e0e0e0;
    }
    
    .metrics-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
    }
    
    .metric-item {
        display: flex;
        flex-direction: column;
    }
    
    .metric-label {
        font-size: 12px;
        font-weight: 500;
        color: var(--md-sys-color-on-surface-variant);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value {
        font-size: 16px;
        font-weight: 400;
        color: var(--md-sys-color-on-surface);
        margin-top: 2px;
    }
    
    .tree-node {
        margin-bottom: 4px;
    }
    
    .tree-item {
        display: flex;
        align-items: center;
        padding: 8px 12px;
        border-radius: 8px;
        cursor: pointer;
        transition: background-color 150ms ease;
        font-size: 14px;
    }
    
    .tree-item:hover {
        background: rgba(25, 118, 210, 0.08);
    }
    
    .tree-item.selected {
        background: rgba(25, 118, 210, 0.12);
        color: var(--md-sys-color-primary);
    }
    
    .tree-icon {
        margin-right: 8px;
        font-size: 18px;
    }
    
    .preview-header {
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .metadata-grid {
        display: grid;
        grid-template-columns: auto 1fr;
        gap: 8px 16px;
        margin-bottom: 24px;
    }
    
    .metadata-label {
        font-size: 12px;
        font-weight: 500;
        color: var(--md-sys-color-on-surface-variant);
        text-transform: uppercase;
    }
    
    .metadata-value {
        font-size: 14px;
        color: var(--md-sys-color-on-surface);
    }
    
    .search-input {
        width: 100%;
        padding: 12px 16px;
        border: 1px solid var(--md-sys-color-surface-variant);
        border-radius: 8px;
        font-size: 14px;
        margin-bottom: 16px;
    }
    
    .breadcrumb {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 16px;
        font-size: 14px;
        color: var(--md-sys-color-on-surface-variant);
    }
    
    .breadcrumb-item {
        cursor: pointer;
    }
    
    .breadcrumb-item:hover {
        color: var(--md-sys-color-primary);
    }
    """

def get_data_sources():
    """Mock data based on the user's requirements"""
    return {
        "fracfocus": {
            "type": "Chemical Data",
            "icon": "science",
            "stages": [
                {"name": "download", "status": "success"},
                {"name": "extract", "status": "success"},
                {"name": "parse", "status": "error"},
                {"name": "validate", "status": "inactive"},
                {"name": "load", "status": "inactive"}
            ],
            "files": 0,
            "records": 0,
            "size": "0 MB",
            "last_update": "2024-01-15 14:30:00",
            "status": "error"
        },
        "fracfocus/Chemical_data": {
            "type": "Chemical Data",
            "icon": "biotech",
            "stages": [
                {"name": "download", "status": "success"},
                {"name": "extract", "status": "success"},
                {"name": "parse", "status": "success"},
                {"name": "validate", "status": "success"},
                {"name": "load", "status": "success"}
            ],
            "files": 16,
            "records": 7255562,
            "size": "1.2 GB",
            "last_update": "2024-01-15 16:45:00",
            "status": "success"
        },
        "rrc/completions_data": {
            "type": "Production Data",
            "icon": "factory",
            "stages": [
                {"name": "download", "status": "success"},
                {"name": "extract", "status": "success"},
                {"name": "parse", "status": "success"},
                {"name": "validate", "status": "success"},
                {"name": "load", "status": "success"}
            ],
            "files": 29,
            "records": 541053,
            "size": "89 MB",
            "last_update": "2024-01-15 15:20:00",
            "status": "success"
        },
        "rrc/horizontal_drilling_permits": {
            "type": "Permits Data",
            "icon": "factory",
            "stages": [
                {"name": "download", "status": "success"},
                {"name": "extract", "status": "success"},
                {"name": "parse", "status": "success"},
                {"name": "validate", "status": "success"},
                {"name": "load", "status": "success"}
            ],
            "files": 1,
            "records": 168239,
            "size": "24 MB",
            "last_update": "2024-01-15 13:15:00",
            "status": "success"
        },
        "rrc/production": {
            "type": "Production Data",
            "icon": "oil_barrel",
            "stages": [
                {"name": "download", "status": "success"},
                {"name": "extract", "status": "success"},
                {"name": "parse", "status": "success"},
                {"name": "validate", "status": "success"},
                {"name": "load", "status": "success"}
            ],
            "files": 16,
            "records": 216079924,
            "size": "8.7 GB",
            "last_update": "2024-01-15 17:00:00",
            "status": "success"
        },
        "NETL EDX": {
            "type": "Research Data",
            "icon": "database",
            "stages": [
                {"name": "download", "status": "inactive"},
                {"name": "extract", "status": "inactive"},
                {"name": "parse", "status": "inactive"},
                {"name": "validate", "status": "inactive"},
                {"name": "load", "status": "inactive"}
            ],
            "files": 0,
            "records": 0,
            "size": "0 MB",
            "last_update": "Not processed",
            "status": "pending"
        },
        "ONEPETRO": {
            "type": "Research Data",
            "icon": "database",
            "stages": [
                {"name": "download", "status": "inactive"},
                {"name": "extract", "status": "inactive"},
                {"name": "parse", "status": "inactive"},
                {"name": "validate", "status": "inactive"},
                {"name": "load", "status": "inactive"}
            ],
            "files": 0,
            "records": 0,
            "size": "0 MB",
            "last_update": "Not processed",
            "status": "pending"
        },
        "rrc": {
            "type": "Regulatory Data",
            "icon": "factory",
            "stages": [
                {"name": "download", "status": "inactive"},
                {"name": "extract", "status": "inactive"},
                {"name": "parse", "status": "inactive"},
                {"name": "validate", "status": "inactive"},
                {"name": "load", "status": "inactive"}
            ],
            "files": 0,
            "records": 0,
            "size": "0 MB",
            "last_update": "Not processed",
            "status": "pending"
        },
        "TWDB": {
            "type": "Water Data",
            "icon": "water_drop",
            "stages": [
                {"name": "download", "status": "inactive"},
                {"name": "extract", "status": "inactive"},
                {"name": "parse", "status": "inactive"},
                {"name": "validate", "status": "inactive"},
                {"name": "load", "status": "inactive"}
            ],
            "files": 0,
            "records": 0,
            "size": "0 MB",
            "last_update": "Not processed",
            "status": "pending"
        },
        "usgs": {
            "type": "Geological Data",
            "icon": "database",
            "stages": [
                {"name": "download", "status": "inactive"},
                {"name": "extract", "status": "inactive"},
                {"name": "parse", "status": "inactive"},
                {"name": "validate", "status": "inactive"},
                {"name": "load", "status": "inactive"}
            ],
            "files": 0,
            "records": 0,
            "size": "0 MB",
            "last_update": "Not processed",
            "status": "pending"
        }
    }

def create_stage_indicators(stages):
    """Create pipeline stage indicators with connectors"""
    stage_icons = {
        "download": "download",
        "extract": "transform", 
        "parse": "code",
        "validate": "check_circle",
        "load": "cloud_upload"
    }
    
    indicators = []
    for i, stage in enumerate(stages):
        icon = stage_icons.get(stage["name"], "circle")
        status_class = f"md-status-circle-{stage['status']}"
        
        indicators.append(f'''
            <div class="stage-indicator {status_class}">
                <span class="material-symbols-rounded">{icon}</span>
            </div>
        ''')
        
        if i < len(stages) - 1:
            indicators.append('<div class="stage-connector"></div>')
    
    return "".join(indicators)

def create_source_card(name, data):
    """Generate HTML for one data source card"""
    stage_html = create_stage_indicators(data["stages"])
    
    return f'''
    <div class="md-card-elevated" onclick="selectDataset('{name}')">
        <div class="card-header">
            <span class="material-symbols-rounded">{data["icon"]}</span>
            <div>
                <h3 class="card-title">{name}</h3>
                <p class="card-subtitle">{data["type"]}</p>
            </div>
        </div>
        
        <div class="pipeline-stages">
            {stage_html}
        </div>
        
        <div class="metrics-grid">
            <div class="metric-item">
                <span class="metric-label">Files</span>
                <span class="metric-value">{data["files"]:,}</span>
            </div>
            <div class="metric-item">
                <span class="metric-label">Records</span>
                <span class="metric-value">{data["records"]:,}</span>
            </div>
            <div class="metric-item">
                <span class="metric-label">Size</span>
                <span class="metric-value">{data["size"]}</span>
            </div>
            <div class="metric-item">
                <span class="metric-label">Last Update</span>
                <span class="metric-value">{data["last_update"]}</span>
            </div>
        </div>
    </div>
    '''

def create_tree_node(name, icon="folder", depth=0, selectable=True):
    """Generate HTML for one tree node"""
    indent = depth * 20
    click_handler = f"onclick=\"selectTreeItem('{name}')\"" if selectable else ""
    
    return f'''
    <div class="tree-node" style="padding-left: {indent}px">
        <div class="tree-item" {click_handler}>
            <span class="material-symbols-rounded tree-icon">{icon}</span>
            <span>{name}</span>
        </div>
    </div>
    '''

def create_dashboard():
    data_sources = get_data_sources()
    total_records = sum(source["records"] for source in data_sources.values())
    processed_sources = sum(1 for source in data_sources.values() if source["status"] == "success")
    
    # Generate cards using comprehension
    cards_html = "".join([
        create_source_card(name, data) 
        for name, data in data_sources.items()
    ])
    
    # Generate tree nodes using comprehension
    tree_html = "".join([
        create_tree_node(name, data["icon"]) 
        for name, data in data_sources.items()
    ])
    
    dashboard_html = f'''
    <div class="dashboard-container">
        <div class="dashboard-header">
            <div class="header-title">
                <span class="material-symbols-rounded md-48">monitoring</span>
                Pipeline Monitor
            </div>
            <div class="header-stats">
                <div class="stat-item">
                    <span class="stat-value">{total_records:,}</span>
                    <span class="stat-label">Total Records</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">{processed_sources}/10</span>
                    <span class="stat-label">Sources Complete</span>
                </div>
                <div class="stat-item">
                    <span class="material-symbols-rounded md-48" style="color: var(--md-sys-color-success)">done</span>
                </div>
            </div>
        </div>
        
        <div class="dashboard-sidebar">
            <input type="text" class="search-input" placeholder="Search datasets..." />
            <div class="tree-container">
                {tree_html}
            </div>
        </div>
        
        <div class="dashboard-main">
            <div class="cards-grid">
                {cards_html}
            </div>
        </div>
        
        <div class="dashboard-preview">
            <div class="preview-header">
                <span class="material-symbols-rounded">description</span>
                Dataset Details
            </div>
            <p style="color: var(--md-sys-color-on-surface-variant); font-size: 14px;">
                Select a dataset to view detailed information, file structure, and data preview.
            </p>
        </div>
    </div>
    
    <script>
        function selectDataset(name) {{
            console.log('Selected dataset:', name);
            // Update preview panel with dataset details
        }}
        
        function selectTreeItem(name) {{
            console.log('Selected tree item:', name);
            // Update tree selection and preview
        }}
    </script>
    '''
    
    with gr.Blocks(
        theme=gr.themes.Default(),
        css=get_m3_theme_css(),
        title="Pipeline Monitor"
    ) as demo:
        
        # Main dashboard HTML
        gr.HTML(dashboard_html)
        
        # Interactive components for functionality
        with gr.Row(visible=False):  # Hidden controls for interactivity
            selected_dataset = gr.Textbox(label="Selected Dataset")
            dataset_selector = gr.Radio(
                choices=list(data_sources.keys()),
                label="Dataset Navigation",
                visible=False
            )
            
            file_browser = gr.Dataframe(
                headers=["File", "Size", "Records", "Last Modified"],
                label="Files",
                visible=False,
                max_height=400
            )
            
            file_preview = gr.Dataframe(
                label="Data Preview",
                visible=False,
                max_height=300
            )
        
        # Event handlers for interactivity
        def update_file_browser(dataset_name):
            if not dataset_name:
                return gr.update(visible=False)
            
            # Mock file data
            files_data = [
                ["data_2024_01.csv", "45 MB", "125,432", "2024-01-15 14:30"],
                ["data_2024_02.csv", "52 MB", "142,891", "2024-01-15 15:45"],
                ["data_2024_03.csv", "38 MB", "98,234", "2024-01-15 16:20"]
            ]
            
            return gr.update(value=files_data, visible=True)
        
        def update_preview(dataset_name):
            if not dataset_name:
                return gr.update(visible=False)
            
            # Mock preview data
            preview_data = [
                ["2024-01-01", "TX", "Chemical A", "1250.5"],
                ["2024-01-01", "TX", "Chemical B", "890.2"],
                ["2024-01-02", "OK", "Chemical A", "1100.8"]
            ]
            
            return gr.update(
                value=preview_data,
                headers=["Date", "State", "Chemical", "Amount"],
                visible=True
            )
        
        # Wire up interactivity
        dataset_selector.change(
            update_file_browser,
            inputs=[dataset_selector],
            outputs=[file_browser]
        )
        
        dataset_selector.change(
            update_preview,
            inputs=[dataset_selector],
            outputs=[file_preview]
        )
    
    return demo

if __name__ == "__main__":
    demo = create_dashboard()
    demo.launch(server_port=None, share=False)