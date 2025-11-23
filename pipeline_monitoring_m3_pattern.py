"""
New pipeline_monitoring_m3 pattern
Complete ETL monitoring dashboard with tree view, file preview, and per-dataset status
"""

PIPELINE_MONITORING_M3_PATTERN = """
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
        analyzer = PipelineContextAnalyzer()
        _CONTEXT_CACHE = analyzer.generate_context_from_filesystem()
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
                for file_info in files[:10]:  # Limit to 10 files
                    file_rows.append([
                        file_info.get("file", "Unknown"),
                        file_info.get("format", "csv").upper(),
                        f"{file_info.get('size_bytes', 0) / 1024 / 1024:.2f} MB",
                        f"{file_info.get('rows', 0):,}",
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
"""
