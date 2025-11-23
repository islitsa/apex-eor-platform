import gradio as gr
from src.templates.m3_theme import get_m3_theme_css
from datetime import datetime
import json

# Data extracted from user intent
data_sources = {
    "fracfocus": {
        "type": "Chemical Data",
        "icon": "science",
        "stages": [
            {"name": "download", "status": "complete"},
            {"name": "parse", "status": "error"},
            {"name": "validate", "status": "pending"},
            {"name": "load", "status": "pending"}
        ],
        "files": 0,
        "records": 0,
        "status": "error",
        "directory_structure": {
            "downloads": {"type": "folder", "files": []},
            "extracted": {"type": "folder", "files": []},
            "parsed": {"type": "folder", "files": []}
        }
    },
    "fracfocus/Chemical_data": {
        "type": "Chemical Data",
        "icon": "science",
        "stages": [
            {"name": "download", "status": "complete"},
            {"name": "parse", "status": "complete"},
            {"name": "validate", "status": "complete"},
            {"name": "load", "status": "complete"}
        ],
        "files": 16,
        "records": 7255562,
        "status": "complete",
        "directory_structure": {
            "downloads": {"type": "folder", "files": ["chemical_data_1.zip", "chemical_data_2.zip"]},
            "extracted": {"type": "folder", "files": ["chemical_data_1.csv", "chemical_data_2.csv"]},
            "parsed": {"type": "folder", "files": [
                {"name": "chemicals_2020.csv", "size": "45.2 MB", "records": 1200000, "columns": ["api", "chemical_name", "concentration"]},
                {"name": "chemicals_2021.csv", "size": "52.1 MB", "records": 1355562, "columns": ["api", "chemical_name", "concentration"]},
                {"name": "chemicals_2022.csv", "size": "48.8 MB", "records": 1300000, "columns": ["api", "chemical_name", "concentration"]}
            ]}
        }
    },
    "rrc/completions_data": {
        "type": "Industrial Data",
        "icon": "factory",
        "stages": [
            {"name": "download", "status": "complete"},
            {"name": "parse", "status": "complete"},
            {"name": "validate", "status": "complete"},
            {"name": "load", "status": "complete"}
        ],
        "files": 29,
        "records": 541053,
        "status": "complete",
        "directory_structure": {
            "parsed": {"type": "folder", "files": [
                {"name": "completions_2023.csv", "size": "12.4 MB", "records": 180000, "columns": ["well_id", "completion_date", "method"]},
                {"name": "completions_2022.csv", "size": "11.8 MB", "records": 175053, "columns": ["well_id", "completion_date", "method"]}
            ]}
        }
    },
    "rrc/horizontal_drilling_permits": {
        "type": "Industrial Data", 
        "icon": "factory",
        "stages": [
            {"name": "download", "status": "complete"},
            {"name": "parse", "status": "complete"},
            {"name": "validate", "status": "complete"},
            {"name": "load", "status": "complete"}
        ],
        "files": 1,
        "records": 168239,
        "status": "complete",
        "directory_structure": {
            "parsed": {"type": "folder", "files": [
                {"name": "permits_2023.csv", "size": "8.2 MB", "records": 168239, "columns": ["permit_id", "operator", "location"]}
            ]}
        }
    },
    "rrc/production": {
        "type": "Industrial Data",
        "icon": "oil_barrel", 
        "stages": [
            {"name": "download", "status": "complete"},
            {"name": "parse", "status": "complete"},
            {"name": "validate", "status": "complete"},
            {"name": "load", "status": "complete"}
        ],
        "files": 16,
        "records": 216079924,
        "status": "complete",
        "directory_structure": {
            "parsed": {"type": "folder", "files": [
                {"name": "production_2023.csv", "size": "1.2 GB", "records": 54000000, "columns": ["well_id", "date", "oil_bbls", "gas_mcf"]},
                {"name": "production_2022.csv", "size": "1.1 GB", "records": 52079924, "columns": ["well_id", "date", "oil_bbls", "gas_mcf"]}
            ]}
        }
    },
    "NETL EDX": {
        "type": "Research Data",
        "icon": "database",
        "stages": [
            {"name": "download", "status": "pending"},
            {"name": "parse", "status": "pending"},
            {"name": "validate", "status": "pending"},
            {"name": "load", "status": "pending"}
        ],
        "files": 0,
        "records": 0,
        "status": "not_processed",
        "directory_structure": {}
    },
    "ONEPETRO": {
        "type": "Research Data",
        "icon": "database",
        "stages": [
            {"name": "download", "status": "pending"},
            {"name": "parse", "status": "pending"},
            {"name": "validate", "status": "pending"},
            {"name": "load", "status": "pending"}
        ],
        "files": 0,
        "records": 0,
        "status": "not_processed",
        "directory_structure": {}
    },
    "rrc": {
        "type": "Industrial Data",
        "icon": "factory",
        "stages": [
            {"name": "download", "status": "pending"},
            {"name": "parse", "status": "pending"},
            {"name": "validate", "status": "pending"},
            {"name": "load", "status": "pending"}
        ],
        "files": 0,
        "records": 0,
        "status": "not_processed",
        "directory_structure": {}
    },
    "TWDB": {
        "type": "Water Data",
        "icon": "water_drop",
        "stages": [
            {"name": "download", "status": "pending"},
            {"name": "parse", "status": "pending"},
            {"name": "validate", "status": "pending"},
            {"name": "load", "status": "pending"}
        ],
        "files": 0,
        "records": 0,
        "status": "not_processed",
        "directory_structure": {}
    },
    "usgs": {
        "type": "Geological Data",
        "icon": "database",
        "stages": [
            {"name": "download", "status": "pending"},
            {"name": "parse", "status": "pending"},
            {"name": "validate", "status": "pending"},
            {"name": "load", "status": "pending"}
        ],
        "files": 0,
        "records": 0,
        "status": "not_processed",
        "directory_structure": {}
    }
}

def create_global_metrics():
    total_records = sum(source["records"] for source in data_sources.values())
    total_files = sum(source["files"] for source in data_sources.values())
    active_datasets = sum(1 for source in data_sources.values() if source["status"] == "complete")
    
    return f'''
    <div style="background: #1565C0; color: white; padding: 24px; margin-bottom: 32px; border-radius: 8px;">
        <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto;">
            <div style="display: flex; gap: 48px; align-items: center;">
                <div style="text-align: center;">
                    <div style="font-size: 32px; font-weight: bold; line-height: 1;">{total_records:,}</div>
                    <div style="font-size: 14px; opacity: 0.9;">Records</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 32px; font-weight: bold; line-height: 1;">{total_files}</div>
                    <div style="font-size: 14px; opacity: 0.9;">Files</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 32px; font-weight: bold; line-height: 1;">{active_datasets}</div>
                    <div style="font-size: 14px; opacity: 0.9;">Active Datasets</div>
                </div>
            </div>
            <div style="text-align: right; font-size: 14px; opacity: 0.9;">
                <span class="material-symbols-rounded" style="font-size: 16px; vertical-align: middle;">refresh</span>
                Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
            </div>
        </div>
    </div>
    '''

def create_stage_indicators(stages):
    stage_icons = {
        "download": "file_download",
        "extract": "transform", 
        "parse": "code",
        "validate": "task_alt",
        "load": "cloud_upload"
    }
    
    return "".join([
        f'''<div class="md-status-circle-{stage["status"]}" style="display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; margin-right: 8px;">
            <span class="material-symbols-rounded" style="font-size: 16px;">{stage_icons.get(stage["name"], "circle")}</span>
        </div>'''
        for stage in stages
    ])

def create_dataset_card(name, info, is_selected=False):
    status_class = f"md-status-card-{info['status']}" if info['status'] != 'not_processed' else "md-card-outlined"
    selected_style = "border: 2px solid #1565C0; background: #f8f9ff;" if is_selected else ""
    
    return f'''
    <div class="{status_class}" style="margin-bottom: 24px; padding: 24px; border-radius: 8px; {selected_style}">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
            <div>
                <h3 style="margin: 0 0 8px 0; font-size: 20px; font-weight: bold; display: flex; align-items: center; gap: 8px;">
                    <span class="material-symbols-rounded">{info["icon"]}</span>
                    {name}
                </h3>
                <div style="color: #666; font-size: 14px;">{info["type"]}</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 16px; font-weight: bold; color: #1565C0;">{info["records"]:,} records</div>
                <div style="font-size: 14px; color: #666;">{info["files"]} files</div>
            </div>
        </div>
        
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 16px;">
            <span style="font-size: 14px; font-weight: 500; margin-right: 8px;">Pipeline:</span>
            {create_stage_indicators(info["stages"])}
        </div>
        
        <div style="font-size: 12px; color: #888;">
            Status: {info["status"].replace("_", " ").title()}
        </div>
    </div>
    '''

def create_dataset_cards_html(selected_dataset=None):
    return "".join([
        create_dataset_card(name, info, name == selected_dataset)
        for name, info in data_sources.items()
    ])

def get_files_for_dataset(dataset_name):
    if dataset_name not in data_sources:
        return []
    
    structure = data_sources[dataset_name]["directory_structure"]
    files_data = []
    
    for folder_name, folder_info in structure.items():
        if folder_info.get("type") == "folder" and "files" in folder_info:
            for file_item in folder_info["files"]:
                if isinstance(file_item, dict):
                    files_data.append([
                        f"{folder_name}/{file_item['name']}", 
                        file_item.get('size', 'Unknown'),
                        f"{file_item.get('records', 0):,}"
                    ])
                else:
                    files_data.append([f"{folder_name}/{file_item}", "Unknown", "Unknown"])
    
    return files_data

def get_file_preview(file_path):
    # Extract dataset and file info from path
    parts = file_path.split('/')
    if len(parts) < 2:
        return "No preview available", []
    
    folder, filename = parts[0], parts[1]
    
    # Find the file in data sources
    for dataset_name, dataset_info in data_sources.items():
        structure = dataset_info.get("directory_structure", {})
        if folder in structure:
            folder_files = structure[folder].get("files", [])
            for file_item in folder_files:
                if isinstance(file_item, dict) and file_item.get("name") == filename:
                    columns = file_item.get("columns", [])
                    sample_data = []
                    
                    # Generate sample data based on columns
                    if columns:
                        sample_data = [
                            ["Sample Row 1"] + ["Sample data..."] * (len(columns) - 1),
                            ["Sample Row 2"] + ["Sample data..."] * (len(columns) - 1),
                            ["Sample Row 3"] + ["Sample data..."] * (len(columns) - 1)
                        ]
                    
                    metadata = f"""
                    **File:** {filename}
                    **Size:** {file_item.get('size', 'Unknown')}
                    **Records:** {file_item.get('records', 0):,}
                    **Columns:** {len(columns)}
                    """
                    
                    return metadata, [columns] + sample_data if columns else []
    
    return "File not found", []

def create_dashboard():
    with gr.Blocks(theme=gr.themes.Default(), css=get_m3_theme_css()) as demo:
        # Global metrics header
        gr.HTML(create_global_metrics())
        
        # Main dashboard title
        gr.HTML('''
        <div style="max-width: 1200px; margin: 0 auto 32px auto;">
            <h1 style="font-size: 32px; font-weight: bold; margin: 0; display: flex; align-items: center; gap: 12px;">
                <span class="material-symbols-rounded md-48">database</span>
                Pipeline Status Dashboard
            </h1>
        </div>
        ''')
        
        with gr.Row(equal_height=True):
            with gr.Column(scale=1):
                # Dataset cards (left side)
                dataset_cards = gr.HTML(create_dataset_cards_html())
                
            with gr.Column(scale=1):
                # Interactive file browser (right side)
                gr.HTML('<h2 style="margin: 0 0 16px 0; font-size: 24px; font-weight: bold;">File Explorer</h2>')
                
                dataset_selector = gr.Radio(
                    choices=list(data_sources.keys()),
                    label="Select Dataset to Explore",
                    value=list(data_sources.keys())[0]
                )
                
                with gr.Accordion("Directory Structure", open=True):
                    file_browser = gr.Dataframe(
                        headers=["File Path", "Size", "Records"],
                        label="Files in Dataset",
                        max_height=400,
                        interactive=False
                    )
                
                with gr.Accordion("File Preview", open=False):
                    file_selector = gr.Textbox(
                        label="Enter file path to preview (e.g., parsed/chemicals_2020.csv)",
                        placeholder="parsed/filename.csv"
                    )
                    
                    file_metadata = gr.Markdown("Select a file to view metadata")
                    
                    file_preview = gr.Dataframe(
                        label="File Contents Preview",
                        max_height=300
                    )
        
        # Event handlers
        def update_files_and_cards(dataset_name):
            files = get_files_for_dataset(dataset_name)
            cards_html = create_dataset_cards_html(dataset_name)
            return gr.update(value=files), gr.update(value=cards_html)
        
        def preview_file(file_path):
            metadata, preview_data = get_file_preview(file_path)
            return gr.update(value=metadata), gr.update(value=preview_data)
        
        # Wire up events
        dataset_selector.change(
            update_files_and_cards,
            inputs=[dataset_selector],
            outputs=[file_browser, dataset_cards]
        )
        
        file_selector.submit(
            preview_file,
            inputs=[file_selector],
            outputs=[file_metadata, file_preview]
        )
        
        # Initialize with first dataset
        demo.load(
            lambda: get_files_for_dataset(list(data_sources.keys())[0]),
            outputs=[file_browser]
        )
    
    return demo

if __name__ == "__main__":
    demo = create_dashboard()
    demo.launch(server_port=None, share=False)