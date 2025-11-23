import gradio as gr

def create_dashboard():
    with gr.Blocks() as demo:
        gr.Markdown("# Pipeline Monitor")

        sources = gr.Radio(
            choices=['fracfocus', 'fracfocus_chemical_data', 'rrc_completions_data', 'rrc_horizontal_drilling_permits', 'rrc_production', 'netl_edx', 'onepetro', 'rrc', 'twdb', 'usgs'],
            label="Data Sources"
        )

        output = gr.Textbox(label="Details")

        def show_info(source):
            return f"Selected: {source}"

        sources.change(show_info, [sources], [output])

    return demo

if __name__ == "__main__":
    demo = create_dashboard()
    demo.launch()
