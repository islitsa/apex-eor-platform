import gradio as gr
from src.templates.m3_theme import get_m3_theme_css

def create_dashboard():
    """Create a production-ready data pipeline dashboard"""

    dashboard_html = """
    <div style="max-width: 1200px; margin: 0 auto; padding: 32px;">
        <!-- Main Header -->
        <div style="margin-bottom: 48px;">
            <h1 class="m3-title-large" style="font-size: 2.5rem; font-weight: 700; color: var(--md-sys-color-on-surface); margin-bottom: 8px;">
                Data Pipeline Dashboard
            </h1>
            <p class="m3-body-large" style="color: var(--md-sys-color-on-surface-variant); font-size: 1.1rem;">
                Monitor and track your data processing workflows
            </p>
        </div>

        <!-- Data Sources Section -->
        <div style="margin-bottom: 40px;">
            <h2 class="m3-title-medium" style="font-size: 1.75rem; font-weight: 600; color: var(--md-sys-color-on-surface); margin-bottom: 24px;">
                <span class="material-symbols-rounded" style="font-size: 2rem; vertical-align: text-bottom; margin-right: 12px;">database</span>
                Data Sources
            </h2>

            <!-- FracFocus Data Source Card -->
            <div class="md-card-elevated" style="padding: 32px; margin-bottom: 24px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px;">
                    <div style="display: flex; align-items: center; gap: 16px;">
                        <div class="md-status-circle-complete">
                            <span class="material-symbols-rounded md-48" style="color: white;">check_circle</span>
                        </div>
                        <div>
                            <h3 class="m3-title-medium" style="font-size: 1.5rem; font-weight: 600; color: var(--md-sys-color-on-surface); margin: 0;">
                                Fracfocus
                            </h3>
                            <p class="m3-body-medium" style="color: var(--md-sys-color-on-surface-variant); margin: 4px 0 0 0;">
                                <span style="font-weight: 600;">Data Type:</span> Chemical Data
                            </p>
                        </div>
                    </div>
                    <div class="md-badge-success" style="font-weight: 600;">
                        All Complete
                    </div>
                </div>

                <!-- Pipeline Stages -->
                <div style="margin-top: 32px;">
                    <h4 class="m3-label-large" style="font-weight: 600; color: var(--md-sys-color-on-surface); margin-bottom: 20px; font-size: 1.1rem;">
                        Pipeline Stages
                    </h4>

                    <!-- Stages Container -->
                    <div style="display: flex; align-items: center; gap: 24px; flex-wrap: wrap;">

                        <!-- Download Stage -->
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div class="md-status-circle-success">
                                <span class="material-symbols-rounded" style="color: white; font-size: 32px;">done</span>
                            </div>
                            <div>
                                <div class="m3-label-medium" style="font-weight: 600; color: var(--md-sys-color-on-surface);">
                                    Download
                                </div>
                                <div class="m3-body-small" style="color: var(--md-sys-color-success); font-weight: 500;">
                                    Complete
                                </div>
                            </div>
                        </div>

                        <!-- Arrow -->
                        <span class="material-symbols-rounded" style="color: var(--md-sys-color-outline); font-size: 1.5rem;">arrow_forward</span>

                        <!-- Extract Stage -->
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div class="md-status-circle-success">
                                <span class="material-symbols-rounded" style="color: white; font-size: 32px;">done</span>
                            </div>
                            <div>
                                <div class="m3-label-medium" style="font-weight: 600; color: var(--md-sys-color-on-surface);">
                                    Extracted
                                </div>
                                <div class="m3-body-small" style="color: var(--md-sys-color-success); font-weight: 500;">
                                    Complete
                                </div>
                            </div>
                        </div>

                        <!-- Arrow -->
                        <span class="material-symbols-rounded" style="color: var(--md-sys-color-outline); font-size: 1.5rem;">arrow_forward</span>

                        <!-- Parse Stage -->
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div class="md-status-circle-success">
                                <span class="material-symbols-rounded" style="color: white; font-size: 32px;">done</span>
                            </div>
                            <div>
                                <div class="m3-label-medium" style="font-weight: 600; color: var(--md-sys-color-on-surface);">
                                    Parsed
                                </div>
                                <div class="m3-body-small" style="color: var(--md-sys-color-success); font-weight: 500;">
                                    Complete
                                </div>
                            </div>
                        </div>

                    </div>
                </div>

                <!-- Summary Stats -->
                <div style="margin-top: 32px; padding-top: 24px; border-top: 1px solid var(--md-sys-color-outline-variant);">
                    <div style="display: flex; gap: 32px; align-items: center; flex-wrap: wrap;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span class="material-symbols-rounded" style="color: var(--md-sys-color-success); font-size: 1.25rem;">task_alt</span>
                            <span class="m3-body-medium" style="color: var(--md-sys-color-on-surface-variant);">
                                <span style="font-weight: 600;">Status:</span> Pipeline Complete
                            </span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span class="material-symbols-rounded" style="color: var(--md-sys-color-on-surface-variant); font-size: 1.25rem;">storage</span>
                            <span class="m3-body-medium" style="color: var(--md-sys-color-on-surface-variant);">
                                <span style="font-weight: 600;">Stages:</span> 3/3 Complete
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """

    with gr.Blocks(css=get_m3_theme_css(), title="Data Pipeline Dashboard") as demo:
        gr.HTML(dashboard_html)

    return demo

if __name__ == "__main__":
    demo = create_dashboard()
    demo.launch()
