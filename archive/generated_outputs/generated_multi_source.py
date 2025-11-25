import gradio as gr
from src.templates.m3_theme import get_m3_theme_css

def create_source_card(source_name, data_type, icon, stages):
    """Create a reusable data source card component"""
    
    # Generate stage circles with connecting lines
    stage_circles = []
    for i, stage in enumerate(stages):
        connector = "" if i == 0 else '<div class="pipeline-connector"></div>'
        
        stage_circles.append(f'''
            {connector}
            <div class="pipeline-stage">
                <div class="md-status-circle-success" title="Completed at 2024-01-15 14:30:00">
                    <span class="material-symbols-rounded">done</span>
                </div>
                <span class="stage-label">{stage}</span>
            </div>
        ''')
    
    stages_html = ''.join(stage_circles)
    
    return f'''
        <div class="md-card-elevated source-card">
            <div class="source-header">
                <div class="source-title">
                    <span class="material-symbols-rounded source-icon">{icon}</span>
                    <h3>{source_name}</h3>
                </div>
                <span class="data-type-label">
                    <span class="material-symbols-rounded data-icon">{get_data_type_icon(data_type)}</span>
                    {data_type}
                </span>
            </div>
            
            <div class="pipeline-container">
                <div class="pipeline-flow">
                    {stages_html}
                </div>
            </div>
        </div>
    '''

def get_data_type_icon(data_type):
    """Map data types to appropriate Material Symbols icons"""
    icon_map = {
        "Chemical Data": "science",
        "Laboratory Data": "biotech", 
        "Water Data": "water_drop"
    }
    return icon_map.get(data_type, "database")

def create_dashboard():
    """Create the complete data pipeline dashboard"""
    
    # Data source configuration
    data_sources = [
        {
            "name": "Fracfocus",
            "type": "Chemical Data", 
            "icon": "database",
            "stages": ["Download", "Extract", "Parse"]
        },
        {
            "name": "NETL EDX",
            "type": "Laboratory Data",
            "icon": "database", 
            "stages": ["Download", "Extract", "Parse"]
        },
        {
            "name": "USGS",
            "type": "Water Data",
            "icon": "database",
            "stages": ["Download", "Extract", "Parse"]
        }
    ]
    
    # Generate source cards
    sources_html = ""
    for source in data_sources:
        sources_html += create_source_card(
            source['name'], 
            source['type'], 
            source['icon'],
            source['stages']
        )
    
    # Complete dashboard HTML
    dashboard_html = f'''
        <div class="dashboard-container">
            <div class="dashboard-header">
                <h1 class="m3-title-large">
                    <span class="material-symbols-rounded header-icon">database</span>
                    Data Sources
                </h1>
                <div class="md-badge-success status-badge">
                    <span class="material-symbols-rounded">check_circle</span>
                    All Complete
                </div>
            </div>
            
            <div class="sources-grid">
                {sources_html}
            </div>
        </div>
    '''
    
    # Custom CSS for the dashboard
    custom_css = '''
        .dashboard-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 32px;
        }
        
        .dashboard-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 40px;
        }
        
        .dashboard-header h1 {
            display: flex;
            align-items: center;
            gap: 16px;
            margin: 0;
            font-size: 32px;
            font-weight: 700;
            color: var(--md-sys-color-on-surface);
        }
        
        .header-icon {
            font-size: 32px !important;
            color: var(--md-sys-color-primary);
        }
        
        .status-badge {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 12px 20px;
            background: var(--md-sys-color-secondary-container);
            color: var(--md-sys-color-on-secondary-container);
            border-radius: 24px;
            font-size: 14px;
            font-weight: 500;
            animation: pulse-success 2s infinite;
        }
        
        @keyframes pulse-success {
            0%, 100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4); }
            50% { box-shadow: 0 0 0 8px rgba(34, 197, 94, 0); }
        }
        
        .sources-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 24px;
        }
        
        .source-card {
            padding: 32px;
            border-radius: 12px;
            background: var(--md-sys-color-surface);
            border: 2px solid var(--md-sys-color-outline-variant);
            transition: all 0.2s ease;
        }
        
        .source-card:hover {
            transform: scale(1.01);
            box-shadow: var(--md-elevation-4);
        }
        
        .source-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }
        
        .source-title {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        
        .source-title h3 {
            margin: 0;
            font-size: 24px;
            font-weight: 700;
            color: var(--md-sys-color-on-surface);
        }
        
        .source-icon {
            font-size: 28px !important;
            color: var(--md-sys-color-primary);
        }
        
        .data-type-label {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 16px;
            color: var(--md-sys-color-on-surface-variant);
        }
        
        .data-icon {
            font-size: 20px !important;
        }
        
        .pipeline-container {
            background: var(--md-sys-color-surface-variant);
            padding: 20px;
            border-radius: 8px;
        }
        
        .pipeline-flow {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0;
        }
        
        .pipeline-stage {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 12px;
        }
        
        .pipeline-connector {
            width: 60px;
            height: 2px;
            background: var(--md-sys-color-outline);
            margin: 0 8px;
        }
        
        .md-status-circle-success {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background: var(--md-sys-color-tertiary);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .md-status-circle-success:hover {
            background: var(--md-sys-color-tertiary-container);
            transform: scale(1.1);
        }
        
        .md-status-circle-success .material-symbols-rounded {
            color: var(--md-sys-color-on-tertiary);
            font-size: 24px !important;
        }
        
        .stage-label {
            font-size: 16px;
            font-weight: 500;
            color: var(--md-sys-color-on-surface);
            text-align: center;
        }
        
        /* Material Symbols Icons */
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
        
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,1,0');
    '''
    
    return dashboard_html, custom_css

def main():
    """Main application entry point"""
    
    dashboard_html, custom_css = create_dashboard()
    
    with gr.Blocks(
        css=get_m3_theme_css() + custom_css,
        title="Data Pipeline Dashboard",
        theme=gr.themes.Default()
    ) as demo:
        
        gr.HTML(
            value=dashboard_html,
            elem_classes=["dashboard-main"]
        )
    
    return demo

if __name__ == "__main__":
    demo = main()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True,
        share=False
    )