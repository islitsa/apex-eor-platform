
import gradio as gr
from typing import Dict, List
import time

# Import M3 theme
from src.templates.m3_theme import get_m3_theme_css

# Lazy-load analyzer for dynamic data access
from src.analyzers.pipeline_context_analyzer import PipelineContextAnalyzer

# Pipeline summary
SUMMARY_DATA = {'source_names': ['fracfocus', 'NETL EDX', 'ONEPETRO', 'rrc', 'TWDB', 'usgs'], 'total_sources': 6, 'total_datasets': 0}

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

.pipeline-container {{
    font-family: 'Inter', sans-serif;
    padding: 40px 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    margin: 20px;
}}

.pipeline-stages {{
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 40px;
    flex-wrap: wrap;
    position: relative;
}}

.stage-hexagon {{
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
}}

.stage-hexagon:hover {{
    transform: translateY(-8px) scale(1.05);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4), 0 0 0 2px rgba(255, 255, 255, 0.2);
}}

.stage-hexagon.complete {{
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
}}

.stage-hexagon.in-progress {{
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    color: white;
    animation: pulse 2s ease-in-out infinite;
}}

.stage-hexagon.pending {{
    background: linear-gradient(135deg, #e5e7eb 0%, #d1d5db 100%);
    color: #6b7280;
}}

@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.7; }}
}}

.stage-icon {{
    font-size: 40px;
    margin-bottom: 8px;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}}

.stage-label {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    text-align: center;
}}

.stage-badge {{
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
}}

.stage-connector {{
    width: 40px;
    height: 3px;
    background: rgba(255, 255, 255, 0.3);
    position: relative;
}}

.stage-connector::after {{
    content: '';
    position: absolute;
    right: -6px;
    top: -3px;
    width: 0;
    height: 0;
    border-left: 6px solid rgba(255, 255, 255, 0.3);
    border-top: 4px solid transparent;
    border-bottom: 4px solid transparent;
}}

.pipeline-title {{
    text-align: center;
    color: white;
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 30px;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}}

.pipeline-subtitle {{
    text-align: center;
    color: rgba(255, 255, 255, 0.9);
    font-size: 14px;
    font-weight: 400;
    margin-top: -20px;
    margin-bottom: 30px;
}}

.dataset-card {{
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin: 16px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    transition: all 0.2s ease;
}}

.dataset-card:hover {{
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    transform: translateY(-2px);
}}

.metric-card {{
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 10px;
    padding: 16px;
    text-align: center;
}}

.metric-value {{
    font-size: 32px;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

.metric-label {{
    font-size: 12px;
    color: #6b7280;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 4px;
}}
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
                        <div class="metric-value">{total_sources}</div>
                        <div class="metric-label">Data Sources</div>
                    </div>
                    <div class="metric-card" style="margin-top: 12px;">
                        <div class="metric-value">{total_datasets}</div>
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
            data_sources = context.get("data_sources", {})
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
            data_sources = context.get("data_sources", {})

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
                stage_data = dataset_info.get(stage, {})
                if stage_data:
                    status = stage_data.get("status", "pending")
                    total_files = stage_data.get("total_files", 0)
                    stages_info.append((stage, status, total_files))
                    stage_names.append(stage.capitalize())

            # Build beautiful hexagon pipeline
            stage_icons = {
                "downloads": "📥",
                "extracted": "📦",
                "parsed": "⚡"
            }

            stage_html = '<div class="pipeline-container"><div class="pipeline-title">' + selected_dataset + ' Pipeline</div><div class="pipeline-subtitle">Click stages below to explore files</div><div class="pipeline-stages">'

            for i, (stage, status, files) in enumerate(stages_info):
                status_class = "complete" if status == "complete" else ("in-progress" if files > 0 else "pending")
                badge = "✓" if status == "complete" else str(files)

                stage_html += f'''
                <div class="stage-hexagon {status_class}">
                    <div class="stage-icon">{stage_icons.get(stage, "📁")}</div>
                    <div class="stage-label">{stage.upper()}</div>
                    <div class="stage-badge">{badge}</div>
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
            data_sources = context.get("data_sources", {})

            dataset_info = None
            for source_name, source_data in data_sources.items():
                if source_data.get("display_name") == selected_dataset:
                    dataset_info = source_data
                    break

            if not dataset_info:
                return []

            stage = selected_stage.lower()
            stage_data = dataset_info.get(stage, {})
            files = stage_data.get("files", [])

            file_rows = []
            if isinstance(files, list):
                for file_info in files[:20]:
                    file_rows.append([
                        file_info.get("file", "Unknown"),
                        file_info.get("format", "csv").upper(),
                        f"{file_info.get('size_bytes', 0) / 1024 / 1024:.2f} MB",
                        f"{file_info.get('rows', 0):,}",
                        "✓ Complete"
                    ])
            else:
                total_files = stage_data.get("total_files", files if isinstance(files, int) else 0)
                total_size = stage_data.get("total_size_bytes", 0)
                total_rows = stage_data.get("total_rows", 0)

                if total_files > 0:
                    file_rows.append([
                        f"{stage} - all files",
                        "Multiple",
                        f"{total_size / 1024 / 1024:.2f} MB",
                        f"{total_rows:,}",
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
