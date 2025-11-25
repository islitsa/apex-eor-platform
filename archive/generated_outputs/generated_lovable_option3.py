import gradio as gr
from src.templates.m3_theme import get_m3_theme_css

def create_source_card(source_name, data_type, stages, icon='database'):
    """Create a reusable data source card component"""
    
    # Generate stage pills HTML
    stage_pills_html = ""
    for i, stage in enumerate(stages):
        stage_pills_html += f'''
        <div class="stage-pill">
            <div class="md-status-circle-complete">
                <span class="material-symbols-rounded">check_circle</span>
            </div>
            <span class="stage-name">{stage}</span>
        </div>
        '''
        
        # Add connector line between stages (except after last stage)
        if i < len(stages) - 1:
            stage_pills_html += '<div class="stage-connector"></div>'
    
    return f'''
    <div class="md-card-elevated source-card">
        <div class="source-header">
            <div class="source-title">
                <span class="material-symbols-rounded">database</span>
                <h3>{source_name}</h3>
            </div>
            <div class="dataset-counter">
                <div class="md-badge-info">6 datasets</div>
            </div>
        </div>
        
        <div class="source-subtitle">
            <span class="material-symbols-rounded data-type-icon">science</span>
            <span class="data-type-label">{data_type}</span>
        </div>
        
        <div class="stages-container">
            <div class="stages-flow">
                {stage_pills_html}
            </div>
        </div>
        
        <div class="status-banner">
            <span class="material-symbols-rounded">task_alt</span>
            <span>All stages complete</span>
        </div>
    </div>
    '''

def create_dashboard():
    """Create the complete data pipeline dashboard"""
    
    # Extract data from user request
    data_sources = [
        {
            'name': 'FracFocus',
            'type': 'Chemical Data',
            'stages': ['Download', 'Extracted', 'Parsed']
        }
    ]
    
    # Generate HTML for all data sources
    sources_html = ""
    for source in data_sources:
        sources_html += create_source_card(
            source['name'], 
            source['type'], 
            source['stages']
        )
    
    # Complete dashboard HTML
    dashboard_html = f'''
    <div class="dashboard-container">
        <div class="dashboard-header">
            <h1 class="dashboard-title">
                <span class="material-symbols-rounded md-48">database</span>
                Data Pipeline Overview
            </h1>
        </div>
        
        <div class="sources-section">
            {sources_html}
        </div>
    </div>
    '''
    
    return dashboard_html

def get_dashboard_css():
    """Custom CSS for the data pipeline dashboard"""
    return """
    /* Material Symbols Font */
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');
    
    .material-symbols-rounded {
        font-family: 'Material Symbols Rounded';
        font-weight: normal;
        font-style: normal;
        font-size: 24px;
        line-height: 1;
        letter-spacing: normal;
        text-transform: none;
        display: inline-block;
        white-space: nowrap;
        word-wrap: normal;
        direction: ltr;
        -webkit-font-feature-settings: 'liga';
        -webkit-font-smoothing: antialiased;
    }
    
    .md-48 { font-size: 48px !important; }
    .md-64 { font-size: 64px !important; }
    
    /* Dashboard Layout */
    .dashboard-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 40px 24px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .dashboard-header {
        text-align: center;
        margin-bottom: 80px;
    }
    
    .dashboard-title {
        font-size: 48px;
        font-weight: 700;
        color: #1a1a1a;
        margin: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 16px;
    }
    
    .dashboard-title .material-symbols-rounded {
        color: #2563eb;
    }
    
    /* Source Cards */
    .md-card-elevated {
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.2s ease;
        border: 1px solid #f1f5f9;
    }
    
    .md-card-elevated:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        transform: translateY(-2px);
    }
    
    .source-card {
        padding: 32px;
        margin-bottom: 32px;
    }
    
    .source-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 16px;
    }
    
    .source-title {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .source-title h3 {
        font-size: 24px;
        font-weight: 700;
        color: #1a1a1a;
        margin: 0;
    }
    
    .source-title .material-symbols-rounded {
        color: #2563eb;
        font-size: 28px;
    }
    
    .dataset-counter {
        flex-shrink: 0;
    }
    
    .md-badge-info {
        background: #eff6ff;
        color: #1d4ed8;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .md-badge-info:hover {
        background: #dbeafe;
        transform: scale(1.05);
    }
    
    .source-subtitle {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 32px;
    }
    
    .data-type-icon {
        color: #2563eb;
        font-size: 20px;
    }
    
    .data-type-label {
        font-size: 16px;
        font-weight: 500;
        color: #2563eb;
    }
    
    /* Stages Flow */
    .stages-container {
        margin-bottom: 24px;
    }
    
    .stages-flow {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0;
        flex-wrap: wrap;
    }
    
    .stage-pill {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
        min-width: 120px;
        padding: 16px;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .stage-pill:hover {
        transform: scale(1.05);
    }
    
    .md-status-circle-complete {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        background: #dcfce7;
        border: 2px solid #16a34a;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
    }
    
    .md-status-circle-complete .material-symbols-rounded {
        color: #16a34a;
        font-size: 32px;
    }
    
    .stage-pill:hover .md-status-circle-complete {
        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
    }
    
    .stage-name {
        font-size: 14px;
        font-weight: 700;
        color: #374151;
        text-align: center;
    }
    
    .stage-connector {
        width: 40px;
        height: 2px;
        background: #16a34a;
        margin: 0 -8px;
        z-index: 1;
        animation: drawLine 0.5s ease-out;
    }
    
    @keyframes drawLine {
        from { width: 0; }
        to { width: 40px; }
    }
    
    /* Status Banner */
    .status-banner {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 8px;
        padding: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
        color: #15803d;
        font-weight: 500;
    }
    
    .status-banner .material-symbols-rounded {
        color: #16a34a;
        font-size: 20px;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .dashboard-title {
            font-size: 36px;
            flex-direction: column;
            gap: 12px;
        }
        
        .source-header {
            flex-direction: column;
            gap: 16px;
            align-items: flex-start;
        }
        
        .stages-flow {
            flex-direction: column;
            gap: 16px;
        }
        
        .stage-connector {
            width: 2px;
            height: 40px;
            transform: rotate(90deg);
        }
        
        .source-card {
            padding: 24px;
        }
    }
    """

# Create Gradio interface
with gr.Blocks(
    theme=gr.themes.Default(),
    css=get_m3_theme_css() + get_dashboard_css(),
    title="Data Pipeline Dashboard"
) as demo:
    
    gr.HTML(create_dashboard())

if __name__ == "__main__":
    demo.launch(
        server_port=None,
        share=False,
        show_error=True
    )