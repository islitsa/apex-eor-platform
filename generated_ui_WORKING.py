import gradio as gr
from datetime import datetime

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

def create_source_card(name, data, selected=False):
    """Generate HTML for one data source card"""
    stage_html = create_stage_indicators(data["stages"])
    border_style = 'border: 2px solid #1976d2; box-shadow: 0 8px 16px rgba(25, 118, 210, 0.2);' if selected else ''

    return f'''
    <div class="md-card-elevated" style="{border_style}">
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

with gr.Blocks(
    theme=gr.themes.Default(),
    css="""
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

    .material-symbols-rounded {
        font-family: 'Material Symbols Rounded';
        font-weight: normal;
        font-style: normal;
        font-size: 24px;
    }

    .md-card-elevated {
        background: white;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        transition: box-shadow 150ms ease;
        margin-bottom: 16px;
    }

    .md-card-elevated:hover {
        box-shadow: 0 3px 6px rgba(0,0,0,0.16);
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
        margin: 0;
    }

    .card-subtitle {
        font-size: 14px;
        color: #666;
        margin: 4px 0 0 0;
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
    }

    .md-status-circle-success {
        background: #2e7d32;
        color: white;
    }

    .md-status-circle-error {
        background: #ba1a1a;
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
        color: #666;
        text-transform: uppercase;
    }

    .metric-value {
        font-size: 16px;
        color: #1c1b1f;
        margin-top: 2px;
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
        color: #666;
        text-transform: uppercase;
    }

    .metadata-value {
        font-size: 14px;
        color: #1c1b1f;
    }
    """,
    title="Pipeline Monitor"
) as demo:

    data_sources = get_data_sources()
    total_records = sum(source["records"] for source in data_sources.values())
    processed_sources = sum(1 for source in data_sources.values() if source["status"] == "success")

    # Header
    gr.HTML(f'''
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 24px; border-bottom: 1px solid #e7e0ec;">
        <div style="display: flex; align-items: center; gap: 16px;">
            <span class="material-symbols-rounded" style="font-size: 48px;">monitoring</span>
            <h1 style="margin: 0; font-size: 28px; font-weight: 700;">Pipeline Monitor</h1>
        </div>
        <div style="display: flex; gap: 32px;">
            <div style="text-align: center;">
                <div style="font-size: 24px; font-weight: 700; color: #1976d2;">{total_records:,}</div>
                <div style="font-size: 14px; color: #666;">Total Records</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 24px; font-weight: 700; color: #1976d2;">{processed_sources}/5</div>
                <div style="font-size: 14px; color: #666;">Sources Complete</div>
            </div>
        </div>
    </div>
    ''')

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Select Dataset")
            dataset_selector = gr.Radio(
                choices=list(data_sources.keys()),
                value=list(data_sources.keys())[0],
                label="",
                interactive=True
            )

        with gr.Column(scale=2):
            gr.Markdown("### Dataset Cards")
            cards_display = gr.HTML(
                "".join([create_source_card(name, data, name == list(data_sources.keys())[0])
                        for name, data in data_sources.items()])
            )

        with gr.Column(scale=1):
            gr.Markdown("### Dataset Details")
            dataset_info = gr.HTML(f'''
            <div class="metadata-grid">
                <span class="metadata-label">Type</span>
                <span class="metadata-value">{data_sources[list(data_sources.keys())[0]]["type"]}</span>

                <span class="metadata-label">Status</span>
                <span class="metadata-value">{data_sources[list(data_sources.keys())[0]]["status"].title()}</span>

                <span class="metadata-label">Files</span>
                <span class="metadata-value">{data_sources[list(data_sources.keys())[0]]["files"]:,}</span>

                <span class="metadata-label">Records</span>
                <span class="metadata-value">{data_sources[list(data_sources.keys())[0]]["records"]:,}</span>
            </div>
            ''')

            file_browser = gr.Dataframe(
                headers=["File", "Size", "Records"],
                label="Files",
                max_height=400
            )

    # Update function
    def update_selection(dataset_name):
        if not dataset_name or dataset_name not in data_sources:
            return gr.update(), gr.update(), gr.update()

        dataset = data_sources[dataset_name]

        # Update cards with selection
        new_cards = "".join([
            create_source_card(name, data, name == dataset_name)
            for name, data in data_sources.items()
        ])

        # Update details
        details_html = f'''
        <div class="metadata-grid">
            <span class="metadata-label">Type</span>
            <span class="metadata-value">{dataset["type"]}</span>

            <span class="metadata-label">Status</span>
            <span class="metadata-value">{dataset["status"].title()}</span>

            <span class="metadata-label">Files</span>
            <span class="metadata-value">{dataset["files"]:,}</span>

            <span class="metadata-label">Records</span>
            <span class="metadata-value">{dataset["records"]:,}</span>

            <span class="metadata-label">Size</span>
            <span class="metadata-value">{dataset["size"]}</span>

            <span class="metadata-label">Last Update</span>
            <span class="metadata-value">{dataset["last_update"]}</span>
        </div>
        '''

        # Mock file data
        files_data = []
        if dataset["files"] > 0:
            files_data = [
                [f"{dataset_name}/file1.csv", dataset["size"], f"{dataset['records']:,}"],
                [f"{dataset_name}/file2.csv", dataset["size"], f"{dataset['records']:,}"],
            ]

        return (
            gr.update(value=new_cards),
            gr.update(value=details_html),
            gr.update(value=files_data)
        )

    # Wire up the event
    dataset_selector.change(
        update_selection,
        inputs=[dataset_selector],
        outputs=[cards_display, dataset_info, file_browser]
    )

if __name__ == "__main__":
    demo.launch(server_port=7879, share=False)
