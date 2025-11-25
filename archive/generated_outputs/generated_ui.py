import gradio as gr
from src.templates.m3_theme import get_m3_theme_css
from typing import Dict, List, Tuple
import json

# Data extracted from user intent
DATA_SOURCES = {
    "fracfocus": {
        "type": "Chemical Data",
        "icon": "science",
        "stages": [
            {"name": "download", "status": "complete"},
            {"name": "extract", "status": "complete"},
            {"name": "parse", "status": "error"},
            {"name": "validate", "status": "pending"},
            {"name": "load", "status": "pending"}
        ],
        "files": 0,
        "records": 0,
        "size": "0 MB",
        "last_update": "2024-01-15 14:30",
        "subdirectories": {
            "downloads": {"files": [], "status": "complete"},
            "extracted": {"files": [], "status": "complete"},
            "parsed": {"files": [], "status": "error"}
        }
    },
    "fracfocus / Chemical_data": {
        "type": "Chemical Data",
        "icon": "biotech",
        "stages": [
            {"name": "download", "status": "complete"},
            {"name": "extract", "status": "complete"},
            {"name": "parse", "status": "complete"},
            {"name": "validate", "status": "complete"},
            {"name": "load", "status": "complete"}
        ],
        "files": 16,
        "records": 7255562,
        "size": "1.2 GB",
        "last_update": "2024-01-15 16:45",
        "subdirectories": {
            "downloads": {"files": ["chemical_data_2023.zip", "chemical_data_2024.zip"], "status": "complete"},
            "extracted": {"files": ["chemical_data_2023.csv", "chemical_data_2024.csv"], "status": "complete"},
            "parsed": {"files": ["chem_001.csv", "chem_002.csv", "chem_003.csv"], "status": "complete"}
        }
    },
    "rrc / completions_data": {
        "type": "Production Data",
        "icon": "factory",
        "stages": [
            {"name": "download", "status": "complete"},
            {"name": "extract", "status": "complete"},
            {"name": "parse", "status": "complete"},
            {"name": "validate", "status": "complete"},
            {"name": "load", "status": "complete"}
        ],
        "files": 29,
        "records": 541053,
        "size": "89 MB",
        "last_update": "2024-01-15 15:20",
        "subdirectories": {
            "downloads": {"files": ["completions_q1.zip", "completions_q2.zip"], "status": "complete"},
            "extracted": {"files": ["completions_q1.csv", "completions_q2.csv"], "status": "complete"},
            "parsed": {"files": ["comp_001.csv", "comp_002.csv"], "status": "complete"}
        }
    },
    "rrc / horizontal_drilling_permits": {
        "type": "Permits Data",
        "icon": "factory",
        "stages": [
            {"name": "download", "status": "complete"},
            {"name": "extract", "status": "complete"},
            {"name": "parse", "status": "complete"},
            {"name": "validate", "status": "complete"},
            {"name": "load", "status": "complete"}
        ],
        "files": 1,
        "records": 168239,
        "size": "25 MB",
        "last_update": "2024-01-15 13:15",
        "subdirectories": {
            "downloads": {"files": ["permits_2024.zip"], "status": "complete"},
            "extracted": {"files": ["permits_2024.csv"], "status": "complete"},
            "parsed": {"files": ["permits_parsed.csv"], "status": "complete"}
        }
    },
    "rrc / production": {
        "type": "Production Data",
        "icon": "oil_barrel",
        "stages": [
            {"name": "download", "status": "complete"},
            {"name": "extract", "status": "complete"},
            {"name": "parse", "status": "complete"},
            {"name": "validate", "status": "complete"},
            {"name": "load", "status": "complete"}
        ],
        "files": 16,
        "records": 216079924,
        "size": "8.7 GB",
        "last_update": "2024-01-15 17:00",
        "subdirectories": {
            "downloads": {"files": ["prod_2023_q1.zip", "prod_2023_q2.zip"], "status": "complete"},
            "extracted": {"files": ["prod_2023_q1.csv", "prod_2023_q2.csv"], "status": "complete"},
            "parsed": {"files": ["260663.csv", "260664.csv", "260665.csv"], "status": "complete"}
        }
    },
    "NETL EDX": {
        "type": "Research Data",
        "icon": "biotech",
        "stages": [
            {"name": "download", "status": "pending"},
            {"name": "extract", "status": "pending"},
            {"name": "parse", "status": "pending"},
            {"name": "validate", "status": "pending"},
            {"name": "load", "status": "pending"}
        ],
        "files": 0,
        "records": 0,
        "size": "0 MB",
        "last_update": "Not processed",
        "subdirectories": {}
    },
    "ONEPETRO": {
        "type": "Research Data",
        "icon": "oil_barrel",
        "stages": [
            {"name": "download", "status": "pending"},
            {"name": "extract", "status": "pending"},
            {"name": "parse", "status": "pending"},
            {"name": "validate", "status": "pending"},
            {"name": "load", "status": "pending"}
        ],
        "files": 0,
        "records": 0,
        "size": "0 MB",
        "last_update": "Not processed",
        "subdirectories": {}
    },
    "rrc": {
        "type": "Regulatory Data",
        "icon": "factory",
        "stages": [
            {"name": "download", "status": "pending"},
            {"name": "extract", "status": "pending"},
            {"name": "parse", "status": "pending"},
            {"name": "validate", "status": "pending"},
            {"name": "load", "status": "pending"}
        ],
        "files": 0,
        "records": 0,
        "size": "0 MB",
        "last_update": "Not processed",
        "subdirectories": {}
    },
    "TWDB": {
        "type": "Water Data",
        "icon": "water_drop",
        "stages": [
            {"name": "download", "status": "pending"},
            {"name": "extract", "status": "pending"},
            {"name": "parse", "status": "pending"},
            {"name": "validate", "status": "pending"},
            {"name": "load", "status": "pending"}
        ],
        "files": 0,
        "records": 0,
        "size": "0 MB",
        "last_update": "Not processed",
        "subdirectories": {}
    },
    "usgs": {
        "type": "Geological Data",
        "icon": "database",
        "stages": [
            {"name": "download", "status": "pending"},
            {"name": "extract", "status": "pending"},
            {"name": "parse", "status": "pending"},
            {"name": "validate", "status": "pending"},
            {"name": "load", "status": "pending"}
        ],
        "files": 0,
        "records": 0,
        "size": "0 MB",
        "last_update": "Not processed",
        "subdirectories": {}
    }
}

def create_stage_indicator(stages: List[Dict]) -> str:
    """Generate pipeline stage indicators with Material Symbols."""
    stage_icons = {
        "download": "file_download",
        "extract": "transform",
        "parse": "code",
        "validate": "check_circle",
        "load": "cloud_upload"
    }
    
    stage_html = []
    for stage in stages:
        status = stage["status"]
        icon = stage_icons.get(stage["name"], "circle")
        
        if status == "complete":
            circle_class = "md-status-circle-success"
            symbol = "done"
        elif status == "error":
            circle_class = "md-status-circle-error"
            symbol = "error"
        elif status == "processing":
            circle_class = "md-status-circle-info"
            symbol = "pending"
        else:
            circle_class = "md-status-circle"
            symbol = icon
            
        stage_html.append(f'''
            <div class="{circle_class}" title="{stage['name'].title()}">
                <span class="material-symbols-rounded">{symbol}</span>
            </div>
        ''')
    
    return '<div class="pipeline-stages">' + "".join(stage_html) + '</div>'

def create_status_badge(stages: List[Dict]) -> str:
    """Generate status badge based on pipeline stages."""
    if all(s["status"] == "complete" for s in stages):
        return '<span class="md-badge-success">Complete</span>'
    elif any(s["status"] == "error" for s in stages):
        return '<span class="md-badge-error">Failed</span>'
    elif any(s["status"] == "processing" for s in stages):
        return '<span class="md-badge-info">Processing</span>'
    else:
        return '<span class="md-badge">Not Started</span>'

def create_source_card(name: str, data: Dict, is_selected: bool = False) -> str:
    """Generate HTML for one data source card."""
    card_class = "md-card-elevated selected-card" if is_selected else "md-card-elevated"
    
    return f'''
    <div class="{card_class}" data-dataset="{name}">
        <div class="card-header">
            <div class="card-title">
                <span class="material-symbols-rounded">{data["icon"]}</span>
                <h3>{name}</h3>
            </div>
            {create_status_badge(data["stages"])}
        </div>
        
        {create_stage_indicator(data["stages"])}
        
        <div class="metrics-grid">
            <div class="metric">
                <span class="metric-label">Files</span>
                <span class="metric-value">{data["files"]:,}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Records</span>
                <span class="metric-value">{data["records"]:,}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Size</span>
                <span class="metric-value">{data["size"]}</span>
            </div>
        </div>
        
        <div class="last-update">
            <span class="material-symbols-rounded">schedule</span>
            <span>Last update: {data["last_update"]}</span>
        </div>
    </div>
    '''

def create_dashboard_cards(selected_dataset: str = None) -> str:
    """Generate all dataset cards with selection highlighting."""
    cards = [
        create_source_card(name, data, name == selected_dataset)
        for name, data in DATA_SOURCES.items()
    ]
    
    total_records = sum(data["records"] for data in DATA_SOURCES.values())
    
    header = f'''
    <div class="dashboard-header">
        <h1>
            <span class="material-symbols-rounded md-48">database</span>
            Pipeline Monitoring Dashboard
        </h1>
        <div class="summary-stats">
            <div class="stat">
                <span class="stat-value">{len(DATA_SOURCES)}</span>
                <span class="stat-label">Datasets</span>
            </div>
            <div class="stat">
                <span class="stat-value">{total_records:,}</span>
                <span class="stat-label">Total Records</span>
            </div>
        </div>
    </div>
    '''
    
    return header + '<div class="cards-container">' + "".join(cards) + '</div>'

def get_file_data(dataset_name: str, subdirectory: str = None) -> List[List]:
    """Get file data for the selected dataset and subdirectory."""
    if dataset_name not in DATA_SOURCES:
        return []
    
    data = DATA_SOURCES[dataset_name]
    
    if subdirectory and subdirectory in data["subdirectories"]:
        files = data["subdirectories"][subdirectory]["files"]
        return [[f, "1.2 MB", "10,000"] for f in files]  # Mock data
    else:
        # Show subdirectories
        subdirs = list(data["subdirectories"].keys())
        return [[f"📁 {subdir}/", "-", "-"] for subdir in subdirs]

def get_breadcrumb(dataset_name: str, subdirectory: str = None) -> str:
    """Generate breadcrumb navigation."""
    if subdirectory:
        return f"{dataset_name} / {subdirectory}"
    return dataset_name

def create_dashboard():
    """Create the main dashboard interface."""
    
    with gr.Blocks(
        theme=gr.themes.Default(),
        css=get_m3_theme_css() + """
        .dashboard-header {
            text-align: center;
            margin-bottom: 32px;
            padding: 24px;
            background: var(--md-sys-color-surface-variant);
            border-radius: 16px;
        }
        
        .dashboard-header h1 {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 16px;
            margin: 0 0 16px 0;
            font-size: 2.5rem;
            font-weight: 700;
        }
        
        .summary-stats {
            display: flex;
            justify-content: center;
            gap: 48px;
        }
        
        .stat {
            text-align: center;
        }
        
        .stat-value {
            display: block;
            font-size: 2rem;
            font-weight: 700;
            color: var(--md-sys-color-primary);
        }
        
        .stat-label {
            font-size: 0.875rem;
            color: var(--md-sys-color-on-surface-variant);
        }
        
        .cards-container {
            display: flex;
            flex-direction: column;
            gap: 24px;
        }
        
        .md-card-elevated {
            padding: 24px;
            border-radius: 16px;
            background: var(--md-sys-color-surface);
            box-shadow: var(--md-elevation-2);
            transition: all 0.2s ease;
        }
        
        .selected-card {
            border: 2px solid var(--md-sys-color-primary);
            box-shadow: var(--md-elevation-3);
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 20px;
        }
        
        .card-title {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .card-title h3 {
            margin: 0;
            font-size: 1.5rem;
            font-weight: 600;
        }
        
        .pipeline-stages {
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
            align-items: center;
        }
        
        .md-status-circle-success,
        .md-status-circle-error,
        .md-status-circle-info,
        .md-status-circle {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
        }
        
        .md-status-circle-success {
            background: var(--md-sys-color-primary);
            color: var(--md-sys-color-on-primary);
        }
        
        .md-status-circle-error {
            background: var(--md-sys-color-error);
            color: var(--md-sys-color-on-error);
        }
        
        .md-status-circle-info {
            background: var(--md-sys-color-tertiary);
            color: var(--md-sys-color-on-tertiary);
        }
        
        .md-status-circle {
            background: var(--md-sys-color-surface-variant);
            color: var(--md-sys-color-on-surface-variant);
            border: 2px solid var(--md-sys-color-outline);
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 16px;
        }
        
        .metric {
            text-align: center;
        }
        
        .metric-label {
            display: block;
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--md-sys-color-on-surface-variant);
            margin-bottom: 4px;
        }
        
        .metric-value {
            display: block;
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--md-sys-color-on-surface);
        }
        
        .last-update {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.875rem;
            color: var(--md-sys-color-on-surface-variant);
        }
        
        .breadcrumb {
            font-size: 0.875rem;
            color: var(--md-sys-color-on-surface-variant);
            margin-bottom: 16px;
            padding: 8px 16px;
            background: var(--md-sys-color-surface-variant);
            border-radius: 8px;
        }
        """,
        title="Pipeline Monitoring Dashboard"
    ) as demo:
        
        with gr.Row(equal_height=True):
            with gr.Column(scale=1):
                cards_display = gr.HTML(
                    value=create_dashboard_cards(),
                    label="Dataset Overview"
                )
            
            with gr.Column(scale=1):
                gr.Markdown("### 📁 File Explorer")
                
                dataset_selector = gr.Dropdown(
                    choices=list(DATA_SOURCES.keys()),
                    value=list(DATA_SOURCES.keys())[0],
                    label="Select Dataset",
                    interactive=True
                )
                
                breadcrumb_display = gr.HTML(
                    value=f'<div class="breadcrumb">{list(DATA_SOURCES.keys())[0]}</div>'
                )
                
                with gr.Accordion("Directory Structure", open=True):
                    file_browser = gr.Dataframe(
                        value=get_file_data(list(DATA_SOURCES.keys())[0]),
                        headers=["Name", "Size", "Records"],
                        label="Files and Directories",
                        max_height=400,
                        interactive=False
                    )
                
                with gr.Accordion("File Preview", open=False):
                    file_preview = gr.Dataframe(
                        value=[],
                        headers=["Column", "Type", "Sample"],
                        label="File Metadata",
                        max_height=300,
                        interactive=False
                    )
        
        # Event handlers
        def update_display(dataset_name):
            files = get_file_data(dataset_name)
            breadcrumb = f'<div class="breadcrumb">{get_breadcrumb(dataset_name)}</div>'
            cards = create_dashboard_cards(dataset_name)
            
            return (
                gr.update(value=files),
                gr.update(value=breadcrumb),
                gr.update(value=cards)
            )
        
        dataset_selector.change(
            update_display,
            inputs=[dataset_selector],
            outputs=[file_browser, breadcrumb_display, cards_display]
        )
    
    return demo

if __name__ == "__main__":
    demo = create_dashboard()
    demo.launch(server_port=None, share=False)