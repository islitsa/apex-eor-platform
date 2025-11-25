
import gradio as gr
from typing import Dict, List

# Pipeline data structure
PIPELINE_DATA = { 'sources': { 'NETL EDX': {'datasets': {}, 'display_name': 'Netl Edx', 'status': 'active'},
               'ONEPETRO': {'datasets': {}, 'display_name': 'Onepetro', 'status': 'active'},
               'TWDB': {'datasets': {}, 'display_name': 'Twdb', 'status': 'active'},
               'fracfocus': { 'datasets': { 'Chemical_data': { 'display_name': 'Chemical Data',
                                                               'last_updated': 'N/A',
                                                               'records': 0,
                                                               'status': 'unknown'}},
                              'display_name': 'Fracfocus',
                              'status': 'active'},
               'rrc': { 'datasets': { 'completions_data': { 'display_name': 'Completions Data',
                                                            'last_updated': 'N/A',
                                                            'records': 0,
                                                            'status': 'unknown'},
                                      'horizontal_drilling_permits': { 'display_name': 'Horizontal '
                                                                                       'Drilling '
                                                                                       'Permits',
                                                                       'last_updated': 'N/A',
                                                                       'records': 0,
                                                                       'status': 'unknown'},
                                      'production': { 'display_name': 'Production',
                                                      'last_updated': 'N/A',
                                                      'records': 0,
                                                      'status': 'unknown'}},
                        'display_name': 'Rrc',
                        'status': 'active'},
               'usgs': { 'datasets': { 'produced_water': { 'display_name': 'Produced Water',
                                                           'last_updated': 'N/A',
                                                           'records': 0,
                                                           'status': 'unknown'}},
                         'display_name': 'Usgs',
                         'status': 'active'}}}

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
            details = f"**Dataset:** {dataset_name}\n\n"
            details += f"**Records:** {dataset.get('records', 'N/A'):,}\n"
            details += f"**Status:** {dataset.get('status', 'Unknown')}\n"
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
