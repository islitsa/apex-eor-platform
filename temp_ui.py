import gradio as gr
import pandas as pd
import time
from datetime import datetime

# Mock data functions for the 4 data sources
def fetch_rrc_production():
    """Fetch RRC Production data"""
    try:
        # Mock data - replace with actual API call
        data = {
            'Well_ID': ['WELL_001', 'WELL_002', 'WELL_003', 'WELL_004', 'WELL_005'],
            'Production_Date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
            'Oil_BBL': [1250, 1180, 1340, 1420, 1380],
            'Gas_MCF': [2150, 2080, 2340, 2420, 2280],
            'Water_BBL': [450, 520, 380, 340, 400]
        }
        return pd.DataFrame(data)
    except Exception as e:
        return pd.DataFrame({'Error': [f'Failed to fetch production data: {str(e)}']})

def fetch_rrc_permits():
    """Fetch RRC Permits data"""
    try:
        data = {
            'Permit_ID': ['PRM_001', 'PRM_002', 'PRM_003', 'PRM_004', 'PRM_005'],
            'Operator': ['ABC Energy', 'XYZ Oil Co', 'Delta Drilling', 'Omega Corp', 'Beta Resources'],
            'Well_Name': ['Eagle Point 1H', 'Maverick 2H', 'Thunder Ridge 3H', 'Storm Valley 4H', 'Lightning 5H'],
            'Status': ['Approved', 'Pending', 'Approved', 'Under Review', 'Approved'],
            'Issue_Date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19']
        }
        return pd.DataFrame(data)
    except Exception as e:
        return pd.DataFrame({'Error': [f'Failed to fetch permits data: {str(e)}']})

def fetch_rrc_completions():
    """Fetch RRC Completions data"""
    try:
        data = {
            'Completion_ID': ['CMP_001', 'CMP_002', 'CMP_003', 'CMP_004', 'CMP_005'],
            'Well_ID': ['WELL_001', 'WELL_002', 'WELL_003', 'WELL_004', 'WELL_005'],
            'Completion_Date': ['2024-01-10', '2024-01-11', '2024-01-12', '2024-01-13', '2024-01-14'],
            'Stages': [18, 22, 20, 24, 19],
            'Total_Fluid_BBL': [15000, 18000, 16500, 20000, 17200]
        }
        return pd.DataFrame(data)
    except Exception as e:
        return pd.DataFrame({'Error': [f'Failed to fetch completions data: {str(e)}']})

def fetch_fracfocus():
    """Fetch FracFocus data"""
    try:
        data = {
            'API_Number': ['42-123-12345', '42-123-12346', '42-123-12347', '42-123-12348', '42-123-12349'],
            'Operator': ['ABC Energy', 'XYZ Oil Co', 'Delta Drilling', 'Omega Corp', 'Beta Resources'],
            'Chemical_Name': ['Water', 'Sand', 'Guar Gum', 'Hydrochloric Acid', 'Potassium Chloride'],
            'Purpose': ['Base Fluid', 'Proppant', 'Gelling Agent', 'Acid', 'Clay Stabilizer'],
            'Percentage': [88.5, 8.2, 1.8, 0.9, 0.6]
        }
        return pd.DataFrame(data)
    except Exception as e:
        return pd.DataFrame({'Error': [f'Failed to fetch FracFocus data: {str(e)}']})

def refresh_all_data(filter_state):
    """Refresh all data sources"""
    try:
        # Fetch all data sources
        production_data = fetch_rrc_production()
        permits_data = fetch_rrc_permits()
        completions_data = fetch_rrc_completions()
        fracfocus_data = fetch_fracfocus()
        
        # Update status
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_msg = f"[OK] Data refreshed successfully at {current_time}"
        
        return production_data, permits_data, completions_data, fracfocus_data, status_msg
        
    except Exception as e:
        error_df = pd.DataFrame({'Error': [f'Data refresh failed: {str(e)}']})
        status_msg = f"[ERROR] Data refresh failed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return error_df, error_df, error_df, error_df, status_msg

def filter_data_by_operator(production_df, permits_df, completions_df, fracfocus_df, selected_operator):
    """Filter all datasets by operator"""
    try:
        if selected_operator == "All Operators":
            return production_df, permits_df, completions_df, fracfocus_df
        
        # Filter permits and fracfocus by operator (they have Operator column)
        filtered_permits = permits_df[permits_df['Operator'] == selected_operator] if 'Operator' in permits_df.columns else permits_df
        filtered_fracfocus = fracfocus_df[fracfocus_df['Operator'] == selected_operator] if 'Operator' in fracfocus_df.columns else fracfocus_df
        
        # For production and completions, return original data (no Operator column in mock data)
        return production_df, filtered_permits, completions_df, filtered_fracfocus
        
    except Exception as e:
        error_df = pd.DataFrame({'Error': [f'Filtering failed: {str(e)}']})
        return error_df, error_df, error_df, error_df

# Material Design 3 CSS injection
md3_css = """
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
    .dashboard-container {
        font-family: 'Roboto', sans-serif;
        background-color: #fef7ff;
        padding: 16px;
    }
    .data-card {
        background: white;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        margin: 8px;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .data-card:hover {
        box-shadow: 0 14px 28px rgba(0,0,0,0.25), 0 10px 10px rgba(0,0,0,0.22);
    }
    .card-title {
        color: #1c1b1f;
        font-size: 1.25rem;
        font-weight: 500;
        padding: 16px 16px 8px 16px;
        margin: 0;
    }
    .refresh-btn {
        background-color: #6750a4 !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 10px 24px !important;
        font-weight: 500 !important;
    }
    .status-indicator {
        padding: 8px 16px;
        border-radius: 8px;
        margin: 8px 0;
        font-family: monospace;
        font-size: 14px;
    }
    .status-success {
        background-color: #d1e7dd;
        color: #0f5132;
        border: 1px solid #badbcc;
    }
    .status-error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c2c7;
    }
</style>
"""

# Create the Gradio interface
def create_dashboard():
    with gr.Blocks(
        title="Oil & Gas Data Dashboard",
        theme=gr.themes.Soft(),
        css="""
            .gradio-container {
                max-width: 1400px !important;
            }
            .dataframe {
                font-size: 12px !important;
            }
        """
    ) as demo:
        
        # Inject Material Design 3 CSS
        gr.HTML(md3_css)
        
        # Initialize state
        data_state = gr.State({
            'production': pd.DataFrame(),
            'permits': pd.DataFrame(), 
            'completions': pd.DataFrame(),
            'fracfocus': pd.DataFrame()
        })
        
        filter_state = gr.State({
            'operator': 'All Operators'
        })
        
        # Header
        gr.HTML("""
            <div class="dashboard-container">
                <h1 style="text-align: center; color: #1c1b1f; font-weight: 500; margin: 16px 0;">
                    Oil & Gas Data Dashboard
                </h1>
            </div>
        """)
        
        # Controls Row
        with gr.Row():
            with gr.Column(scale=2):
                operator_filter = gr.Dropdown(
                    choices=["All Operators", "ABC Energy", "XYZ Oil Co", "Delta Drilling", "Omega Corp", "Beta Resources"],
                    value="All Operators",
                    label="Filter by Operator",
                    elem_classes=["filter-dropdown"]
                )
            with gr.Column(scale=1):
                refresh_btn = gr.Button(
                    "Refresh All Data",
                    variant="primary",
                    elem_classes=["refresh-btn"]
                )
            with gr.Column(scale=2):
                status_display = gr.HTML(
                    '<div class="status-indicator">Ready to load data...</div>',
                    elem_id="status-indicator"
                )
        
        # Data Display Grid - 2x2 layout for 4 data sources
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML('<h3 class="card-title">RRC Production Data</h3>')
                production_display = gr.DataFrame(
                    elem_id="production-table",
                    elem_classes=["data-card"]
                )
                
            with gr.Column(scale=1):
                gr.HTML('<h3 class="card-title">RRC Permits Data</h3>')
                permits_display = gr.DataFrame(
                    elem_id="permits-table", 
                    elem_classes=["data-card"]
                )
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML('<h3 class="card-title">RRC Completions Data</h3>')
                completions_display = gr.DataFrame(
                    elem_id="completions-table",
                    elem_classes=["data-card"]
                )
                
            with gr.Column(scale=1):
                gr.HTML('<h3 class="card-title">FracFocus Data</h3>')
                fracfocus_display = gr.DataFrame(
                    elem_id="fracfocus-table",
                    elem_classes=["data-card"]
                )
        
        # Event Handling
        
        # Refresh button click event
        refresh_btn.click(
            fn=refresh_all_data,
            inputs=[filter_state],
            outputs=[
                production_display,
                permits_display, 
                completions_display,
                fracfocus_display,
                status_display
            ]
        )
        
        # Operator filter change event
        operator_filter.change(
            fn=lambda operator, prod_df, perm_df, comp_df, frac_df: filter_data_by_operator(
                prod_df, perm_df, comp_df, frac_df, operator
            ),
            inputs=[
                operator_filter,
                production_display,
                permits_display,
                completions_display, 
                fracfocus_display
            ],
            outputs=[
                production_display,
                permits_display,
                completions_display,
                fracfocus_display
            ]
        )
        
        # Load initial data on startup
        demo.load(
            fn=lambda: refresh_all_data({}),
            inputs=[],
            outputs=[
                production_display,
                permits_display,
                completions_display, 
                fracfocus_display,
                status_display
            ]
        )
    
    return demo

# Launch the dashboard
if __name__ == "__main__":
    dashboard = create_dashboard()
    dashboard.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )