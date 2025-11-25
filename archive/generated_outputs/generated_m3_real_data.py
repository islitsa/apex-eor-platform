
import gradio as gr
from typing import Dict, List
import time

# Import M3 theme
from src.templates.m3_theme import get_m3_theme_css

# Lazy-load analyzer for dynamic data access
from src.analyzers.pipeline_context_analyzer import PipelineContextAnalyzer

# Pipeline summary (lightweight - no full data embedded!)
SUMMARY_DATA = {'source_names': ['fracfocus', 'NETL EDX', 'ONEPETRO', 'rrc', 'TWDB', 'usgs'], 'total_sources': 6, 'total_datasets': 5, 'processing_count': 0}

# Context cache to avoid re-scanning filesystem on every interaction
_CONTEXT_CACHE = None
_CACHE_TIMESTAMP = None
CACHE_TTL = 60  # seconds

def get_cached_context():
    """Get pipeline context with caching to avoid repeated filesystem scans"""
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
        gr.HTML("""
        <div class="md-header-gradient md-fade-in">
            <h1 class="md-header-title">⚙️ ETL Pipeline Monitor</h1>
            <p class="md-header-subtitle">Monitor your petroleum data ingestion pipeline</p>
        </div>
        """)

        # ETL Pipeline Stage Visualization
        gr.HTML("""
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
        """)

        with gr.Row():
            # Left sidebar: ETL Pipeline Metrics
            with gr.Column(scale=1, min_width=250):
                gr.HTML("""
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
                """.format(total_sources, total_datasets, processing_count))

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
                gr.HTML("""
                <div class="md-card md-card-filled" style="margin: 16px 0;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 14px; color: var(--md-on-surface-variant); font-weight: 500;">📍 Current Path:</span>
                        <span id="breadcrumb-path" style="font-size: 14px; color: var(--md-primary); font-weight: 600;">Home</span>
                    </div>
                </div>
                """)

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
