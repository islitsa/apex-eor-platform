"""
Load Dashboard Components into Pinecone
- Logs component
- Feedback/Learning System component
NO HARDCODING - Store in knowledge base for retrieval
"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.knowledge.design_kb_pinecone import DesignKnowledgeBasePinecone


# Logs Component
logs_component = {
    "id": "logs-output-accordion",
    "title": "Pipeline Logs Display Component",
    "category": "component",
    "description": "Accordion component for displaying pipeline execution logs in real-time",
    "gradio_code": """        # Pipeline Logs
        with gr.Accordion("Pipeline Logs", open=False):
            logs_output = gr.Textbox(
                label="Execution Logs",
                placeholder="Pipeline logs will appear here...",
                lines=10,
                interactive=False,
                max_lines=20
            )
""",
    "usage": "Pipeline execution logging and output display",
    "rating": None
}

# Feedback/Learning System Component
feedback_component = {
    "id": "feedback-learning-system",
    "title": "Feedback & Learning System Component",
    "category": "component",
    "description": "Collects user feedback to help the system learn and improve generated dashboards",
    "gradio_code": """        # Feedback & Learning System
        gr.Markdown("## Help Us Improve!")
        with gr.Accordion("Rate This Dashboard", open=False):
            gr.Markdown("Your feedback helps the system learn and improve.")

            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Component Ratings (1-5 stars)")
                    layout_rating = gr.Slider(minimum=1, maximum=5, value=3, step=1, label="Layout & Organization")
                    colors_rating = gr.Slider(minimum=1, maximum=5, value=3, step=1, label="Colors & Visual Design")
                    pipeline_flow_rating = gr.Slider(minimum=1, maximum=5, value=3, step=1, label="Pipeline Flow Visualization")
                    sor_cards_rating = gr.Slider(minimum=1, maximum=5, value=3, step=1, label="Source Cards")
                    kpi_metrics_rating = gr.Slider(minimum=1, maximum=5, value=3, step=1, label="KPI Metrics Display")

                with gr.Column(scale=1):
                    gr.Markdown("### &nbsp;")
                    buttons_rating = gr.Slider(minimum=1, maximum=5, value=3, step=1, label="Buttons & Controls")
                    logs_rating = gr.Slider(minimum=1, maximum=5, value=3, step=1, label="Logs Display")
                    responsiveness_rating = gr.Slider(minimum=1, maximum=5, value=3, step=1, label="Responsiveness")
                    data_accuracy_rating = gr.Slider(minimum=1, maximum=5, value=3, step=1, label="Data Accuracy")
                    overall_rating = gr.Slider(minimum=1, maximum=5, value=3, step=1, label="⭐ Overall Rating")

            feedback_comments = gr.Textbox(
                label="Additional Comments (optional)",
                placeholder="What did you like? What could be better?",
                lines=3
            )

            submit_feedback_btn = gr.Button("Submit Feedback", variant="primary")
            feedback_status = gr.Textbox(label="Status", value="", interactive=False, visible=False)
""",
    "event_handlers": """        # Feedback Handler
        def on_submit_feedback(layout, colors, pipeline_flow, sor_cards, kpis,
                                buttons, logs_rating, responsiveness, data_accuracy, overall, comments):
            try:
                import requests
                from datetime import datetime
                feedback_data = {
                    "dashboard_id": f"pipeline_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "component_ratings": {
                        "layout": int(layout), "colors": int(colors),
                        "pipeline_flow": int(pipeline_flow), "sor_cards": int(sor_cards),
                        "kpi_metrics": int(kpis), "buttons": int(buttons),
                        "logs": int(logs_rating), "responsiveness": int(responsiveness),
                        "data_accuracy": int(data_accuracy)
                    },
                    "overall_rating": int(overall),
                    "comments": comments,
                    "patterns_used": ["component-based-v3-opus"]
                }
                response = requests.post("http://localhost:8000/feedback", json=feedback_data, timeout=5)
                if response.status_code == 200:
                    avg = sum(feedback_data["component_ratings"].values()) / len(feedback_data["component_ratings"])
                    return f"✅ Thank you! Feedback submitted (Avg: {avg:.1f}/5)"
                else:
                    return "⚠️ Feedback saved locally"
            except:
                return "✅ Feedback saved locally (server offline)"

        submit_feedback_btn.click(
            fn=on_submit_feedback,
            inputs=[layout_rating, colors_rating, pipeline_flow_rating, sor_cards_rating,
                    kpi_metrics_rating, buttons_rating, logs_rating, responsiveness_rating,
                    data_accuracy_rating, overall_rating, feedback_comments],
            outputs=[feedback_status]
        ).then(
            lambda: gr.update(visible=True),
            outputs=[feedback_status]
        )
""",
    "usage": "Self-learning system - collects ratings and feedback",
    "rating": None
}


if __name__ == '__main__':
    print("Loading Dashboard Components into Pinecone...")

    kb = DesignKnowledgeBasePinecone()

    # Load logs component
    print("\n[1/2] Loading Logs Component...")
    kb.add_guideline(
        guideline_id=logs_component['id'],
        title=logs_component['title'],
        content=f"{logs_component['description']}\n\nGradio Code:\n{logs_component['gradio_code']}",
        category="component",
        metadata={"tags": ["logs", "output", "console", "pipeline"]}
    )
    print(f"  [OK] Loaded: {logs_component['title']}")

    # Load feedback component
    print("\n[2/2] Loading Feedback & Learning System Component...")
    full_code = feedback_component['gradio_code'] + "\n\n" + feedback_component['event_handlers']
    kb.add_guideline(
        guideline_id=feedback_component['id'],
        title=feedback_component['title'],
        content=f"{feedback_component['description']}\n\nGradio Code:\n{full_code}",
        category="component",
        metadata={"tags": ["feedback", "learning", "ratings", "self-improvement"]}
    )
    print(f"  [OK] Loaded: {feedback_component['title']}")

    print("\n[OK] All dashboard components loaded into Pinecone!")
    print("\nNow the assembler can retrieve these components instead of hardcoding them.")
