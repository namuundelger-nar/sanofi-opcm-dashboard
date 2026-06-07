"""
Sanofi OPCM Dashboard
---------------------
Developed for the Data Analyses and Application Development Trainee role application.

This application provides a comprehensive overview of Operational Planning and Capacity
Management (OPCM) metrics for pharmaceutical R&D projects. It features an advanced
Dynamic Corporate Finance Model supporting DCF, WACC, and Sensitivity Analysis.

Author: [Your Name / Applicant]
Date: 2026-06-07
"""

import dash
from dash import dcc, html, Input, Output, State, ctx, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
import base64
import io

# ==========================================
# 1. Synthetic Data Generator (Time-Series)
# ==========================================
def generate_synthetic_data(num_base_projects: int = 500) -> pd.DataFrame:
    """
    Generates a synthetic time-series dataset representing R&D projects over 4 quarters.
    """
    np.random.seed(random.randint(1, 10000)) # Randomize seed for dynamic generation
    
    therapeutic_areas = ['Oncology', 'Rare Diseases', 'Neurology', 'Vaccines', 'Immunoscience']
    regions = ['Budapest Hub', 'Paris HQ', 'Boston R&D']
    stages = ['Pre-clinical', 'Phase I', 'Phase II', 'Phase III']
    quarters = ['Q1 2026', 'Q2 2026', 'Q3 2026', 'Q4 2026']
    
    data = []
    
    for i in range(1, num_base_projects + 1):
        project_id = f'PRJ-{random.randint(1000, 9999)}-{i:04d}'
        ta = np.random.choice(therapeutic_areas)
        region = np.random.choice(regions)
        stage = np.random.choice(stages)
        req_ftes = np.random.randint(5, 50)
        alloc_ftes = np.random.randint(2, 55)
        # Base starting fixed budget (in thousands)
        base_budget = np.random.uniform(500, 10000)
        # Global random baseline WACC assigned to project (7% to 12%) for non-macro calculations
        wacc = np.random.uniform(0.07, 0.12)
        
        for q_idx, quarter in enumerate(quarters):
            # Budget fluctuates slightly
            fluctuation = np.random.uniform(-0.05, 0.15)
            current_budget = base_budget * ((1 + fluctuation) ** q_idx)
            
            data.append({
                'Project_ID': project_id,
                'Therapeutic_Area': ta,
                'Region': region,
                'Stage': stage,
                'Quarter': quarter,
                'Required_FTEs': req_ftes,
                'Allocated_FTEs': alloc_ftes,
                'Budget_USD_k': round(current_budget, 2),
                'WACC': wacc
            })
            
    df = pd.DataFrame(data)
    df['FTE_Variance'] = df['Allocated_FTEs'] - df['Required_FTEs']
    return df

# Initialize base dataset for first load
initial_app_data = generate_synthetic_data()

# ==========================================
# 2. Dash Application Initialization
# ==========================================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Sanofi OPCM Dashboard"
server = app.server

# ==========================================
# 3. UI Component Definitions
# ==========================================

# Navigation Bar
navbar = dbc.NavbarSimple(
    children=[
        dbc.Button("🐙 View on GitHub", href="https://github.com/namuundelger-nar/sanofi-opcm-dashboard", target="_blank", color="dark", className="fw-bold shadow-sm"),
        dbc.Button("Help & Documentation (Advisor)", id="open-help-modal", color="info", className="ms-2 fw-bold shadow-sm", n_clicks=0),
    ],
    brand="R&D Capacity Management & Corporate Finance",
    brand_href="#",
    color="primary",
    dark=True,
    fluid=True,
    className="mb-4 shadow-sm"
)

# Advisor Chatbot Modal
help_modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("💬 OPCM Virtual Advisor"), className="bg-primary text-white"),
    dbc.ModalBody([
        html.P("Welcome to the OPCM Dashboard. Ask me any questions about our financial terms or how to navigate the app!", className="text-muted"),
        html.Div(id="chat-history-ui", style={"height": "300px", "overflowY": "auto", "padding": "15px", "backgroundColor": "#f8f9fa", "border": "1px solid #dee2e6", "borderRadius": "5px", "marginBottom": "15px"}),
        dbc.InputGroup([
            dbc.Input(id="chat-input", placeholder="E.g., What does WACC mean? Or how do I upload data?", type="text"),
            dbc.Button("Send", id="chat-submit", color="primary", n_clicks=0)
        ])
    ]),
    dbc.ModalFooter(dbc.Button("Close", id="close-help-modal", className="ms-auto", color="secondary", n_clicks=0))
], id="help-modal", size="lg", is_open=False)

# Global Sidebar
sidebar = dbc.Card(
    dbc.CardBody([
        html.H5("Global Filters", className="card-title fw-bold text-primary mb-3"),
        html.Hr(),
        html.Label("Region:", className="fw-bold mb-1"),
        dcc.Dropdown(
            id='region-filter',
            options=[], # Populated dynamically
            multi=True,
            className="mb-4",
            placeholder="Select Region(s)..."
        ),
        html.Label("Therapeutic Area:", className="fw-bold mb-1"),
        dcc.Dropdown(
            id='ta-filter',
            options=[], # Populated dynamically
            multi=True,
            className="mb-3",
            placeholder="Select Therapeutic Area(s)..."
        ),
        html.Hr(),
        html.Div(id='data-status-alert', className="mt-3 text-center")
    ]),
    className="h-100 shadow-sm border-0 bg-light"
)

def create_kpi_card(title: str, value_id: str, text_color: str = "primary") -> dbc.Card:
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="card-subtitle text-muted fw-bold text-uppercase mb-2"),
            html.H3(id=value_id, children="0", className=f"text-{text_color} fw-bold")
        ]),
        className="shadow-sm mb-4 border-0"
    )

# Tab 1: Capacity Management
tab_capacity = dbc.Card(
    dbc.CardBody([
        html.P("Displaying operational data for the latest quarter (Q4 2026).", className="text-muted fst-italic"),
        dbc.Row([
            dbc.Col(create_kpi_card("Active Projects", "kpi-projects", text_color="info"), md=4),
            dbc.Col(create_kpi_card("Total FTE Variance", "kpi-fte-variance", text_color="danger"), md=4),
            dbc.Col(create_kpi_card("Total Budget (USD M)", "kpi-budget", text_color="success"), md=4),
        ]),
        dbc.Row(
            dbc.Col([
                dbc.Card(
                    dbc.CardBody(dcc.Graph(id='variance-bar-chart')),
                    className="shadow-sm mb-2 border-0"
                ),
                html.Div(id='bar-click-explanation', className="mb-4")
            ])
        )
    ]),
    className="border-top-0 border-0 bg-transparent"
)

# Tab 2: CFA Financial Distribution & DCF
tab_financial = dbc.Card(
    dbc.CardBody([
        
        # Macro Assumptions
        dbc.Card([
            dbc.CardHeader("⚙️ Sensitivity Analysis & Financial Assumptions", className="fw-bold bg-light text-primary"),
            dbc.CardBody(
                dbc.Row([
                    dbc.Col([
                        html.Label("Blended Annual FTE Cost ($)", className="fw-bold"),
                        dcc.Slider(id='fte-cost-slider', min=80000, max=300000, step=10000, value=150000, marks={80000: '80k', 150000: '150k', 300000: '300k'}, tooltip={"placement": "bottom", "always_visible": True})
                    ], md=4),
                    dbc.Col([
                        html.Label("Corporate Discount Rate (WACC %)", className="fw-bold"),
                        dcc.Slider(id='wacc-slider', min=2, max=15, step=0.5, value=8, marks={2: '2%', 8: '8%', 15: '15%'}, tooltip={"placement": "bottom", "always_visible": True})
                    ], md=4),
                    dbc.Col([
                        html.Label("Quarterly Inflation/Escalation (%)", className="fw-bold"),
                        dcc.Slider(id='inflation-slider', min=0, max=5, step=0.5, value=1.5, marks={0: '0%', 1.5: '1.5%', 5: '5%'}, tooltip={"placement": "bottom", "always_visible": True})
                    ], md=4),
                ])
            )
        ], className="shadow-sm mb-4 border-0"),
        
        # View Mode Selector
        dbc.Row(
            dbc.Col([
                html.Label("Visualization Mode:", className="fw-bold text-primary me-3"),
                dbc.RadioItems(
                    id='view-mode-selector',
                    options=[
                        {"label": "2D Classic View", "value": "2D"},
                        {"label": "3D Spatial View", "value": "3D"},
                        {"label": "4D Animated View", "value": "4D"}
                    ],
                    value="4D",
                    inline=True,
                    className="mb-3"
                )
            ], width=12)
        ),
        
        # Multi-Dimensional Graph
        dbc.Row([
            dbc.Col([
                html.H5("Multi-Dimensional Financial Projection", className="text-center text-primary fw-bold"),
                html.P("Click any data point for scalable financial insights.", className="text-center text-muted fst-italic"),
                dbc.Card(dbc.CardBody(dcc.Graph(id='financial-graph', style={'height': '500px'})), className="shadow-sm border-0 mb-2")
            ], width=12)
        ]),
        
        # Educational WACC click explanation placeholder
        dbc.Row(
            dbc.Col(html.Div(id='graph-click-explanation', className="mb-4"))
        ),
        
        # Dash DataTable for CFA Aggregates
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H5("📈 CFA Aggregates: Total 2026 Cash Burn by Therapeutic Area", className="card-title text-primary fw-bold border-bottom pb-2"),
                        dash_table.DataTable(
                            id='financial-data-table',
                            style_cell={'textAlign': 'left', 'padding': '10px', 'fontFamily': 'sans-serif'},
                            style_header={'fontWeight': 'bold', 'backgroundColor': '#f8f9fa'},
                            page_action='none',
                            style_table={'height': '300px', 'overflowY': 'auto'}
                        )
                    ]), className="shadow-sm mt-2 border-0 bg-white"
                )
            )
        ),
        
        # Executive Summary / Dynamic CFA Text
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H5("📊 Executive CFA Narrative", className="card-title text-primary fw-bold border-bottom pb-2"),
                        html.Div(id="dynamic-financial-text", className="pt-2 fs-5")
                    ]),
                    className="shadow-sm mt-4 border-0 bg-white"
                )
            )
        )
    ]),
    className="border-top-0 border-0 bg-transparent"
)

# Tab 3: Data Management
tab_data_management = dbc.Card(
    dbc.CardBody([
        html.H4("📂 Enterprise Data Management", className="text-primary fw-bold mb-4"),
        dbc.Row([
            # CSV Upload Panel
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Upload Custom Dataset", className="fw-bold bg-light"),
                    dbc.CardBody([
                        dcc.Upload(
                            id='upload-data',
                            children=html.Div(['Drag and Drop or ', html.A('Select a CSV/Excel File', className="fw-bold text-primary")]),
                            style={
                                'width': '100%', 'height': '120px', 'lineHeight': '120px',
                                'borderWidth': '2px', 'borderStyle': 'dashed',
                                'borderRadius': '10px', 'textAlign': 'center', 'margin': '10px 0',
                                'backgroundColor': '#f8f9fa'
                            },
                            multiple=False
                        ),
                        html.Div(id='upload-status', className="text-muted small mt-2")
                    ])
                ], className="shadow-sm border-0 mb-4")
            ], md=6),
            
            # Synthetic Data Generator Panel
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Synthetic Data Generator", className="fw-bold bg-light"),
                    dbc.CardBody([
                        html.Label("Number of Base Projects to Simulate:", className="fw-bold"),
                        dbc.Input(id="synth-project-count", type="number", value=500, min=100, max=5000, step=100, className="mb-3"),
                        dbc.Button("Generate Fresh Data", id="btn-generate-data", color="primary", className="w-100 fw-bold shadow-sm"),
                        html.Div(id='generate-status', className="text-muted small mt-2 text-center")
                    ])
                ], className="shadow-sm border-0 mb-4")
            ], md=6)
        ]),
        
        # Data Dictionary Reference
        dbc.Card([
            dbc.CardHeader("📖 Required Data Dictionary (Format Reference)", className="fw-bold bg-secondary text-white"),
            dbc.CardBody([
                html.P("To ensure the financial models calculate correctly, your uploaded CSV must contain the following exact column headers:"),
                html.Ul([
                    html.Li([html.Code("Project_ID"), ": Unique string identifier."]),
                    html.Li([html.Code("Therapeutic_Area"), ": Categorical string (e.g., Oncology, Rare Diseases)."]),
                    html.Li([html.Code("Region"), ": Categorical string (e.g., Budapest Hub)."]),
                    html.Li([html.Code("Stage"), ": Must be 'Pre-clinical', 'Phase I', 'Phase II', or 'Phase III'."]),
                    html.Li([html.Code("Quarter"), ": Format as 'Q1 2026', 'Q2 2026', 'Q3 2026', 'Q4 2026'."]),
                    html.Li([html.Code("Required_FTEs"), " & ", html.Code("Allocated_FTEs"), ": Numeric values."]),
                    html.Li([html.Code("Budget_USD_k"), ": Numeric base budget in thousands."])
                ])
            ])
        ], className="shadow-sm border-0")
    ]),
    className="border-top-0 border-0 bg-transparent"
)


# Main Application Layout
app.layout = html.Div(
    style={"backgroundColor": "#f8f9fa", "minHeight": "100vh"},
    children=[
        navbar,
        help_modal, # Inject the Advisor Chatbot Modal here
        dbc.Container([
            dbc.Row([
                dbc.Col(sidebar, md=3, className="mb-4"),
                dbc.Col([
                    dbc.Tabs([
                        dbc.Tab(tab_capacity, label="Capacity Management", tab_id="tab-1", label_style={"fontWeight": "bold"}),
                        dbc.Tab(tab_financial, label="Financial Distribution & DCF Model", tab_id="tab-2", label_style={"fontWeight": "bold"}),
                        dbc.Tab(tab_data_management, label="Data Management", tab_id="tab-3", label_style={"fontWeight": "bold"}),
                    ], id="tabs", active_tab="tab-2")
                ], md=9)
            ])
        ], fluid=True, className="px-4"),
        
        # Footer
        html.Footer(
            dbc.Container(
                dbc.Row([
                    dbc.Col(html.Span("Developed for Sanofi OPCM Trainee Application", id="easter-egg-trigger", className="text-muted small", n_clicks=0, style={"cursor": "pointer"}), width="auto"),
                ], justify="between", className="align-items-center py-3")
            ), className="mt-5 border-top bg-white"
        ),
        html.Div(id="easter-egg-output"),
        dcc.Store(id='dummy-store'),
        dcc.Store(id='click-history-store', data={'stage': None, 'clicks': 0}),
        dcc.Store(id='chat-store', data=[]), # Chatbot state memory
        # Master Reactive Data Store
        dcc.Store(id='app-data-store') # Populated dynamically on load
    ]
)

# ==========================================
# 4. Interactive Callbacks
# ==========================================

# Chatbot Advisor Toggle
@app.callback(
    Output("help-modal", "is_open"),
    [Input("open-help-modal", "n_clicks"), Input("close-help-modal", "n_clicks")],
    [State("help-modal", "is_open")]
)
def toggle_help_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# Chatbot Advisor Logic
@app.callback(
    [Output("chat-history-ui", "children"), Output("chat-store", "data"), Output("chat-input", "value")],
    Input("chat-submit", "n_clicks"),
    [State("chat-input", "value"), State("chat-store", "data")]
)
def handle_chat(n_clicks, user_text, chat_data):
    if not ctx.triggered or not user_text:
        return dash.no_update, dash.no_update, dash.no_update
        
    if chat_data is None:
        chat_data = []
        
    # Append User Message
    chat_data.append({"sender": "user", "text": user_text})
    
    # Simple Rule-Based NLP Logic
    lower_text = user_text.lower()
    if "wacc" in lower_text or "discount" in lower_text:
        bot_response = "WACC stands for Weighted Average Cost of Capital. It represents Sanofi's blended cost to borrow money from investors. We use it in this dashboard as the 'hurdle rate' to discount future cash flows back to today's Present Value."
    elif "fte" in lower_text:
        bot_response = "FTE stands for Full-Time Equivalent. 1 FTE equals one full-time employee. We multiply your Allocated FTEs by the 'Blended Annual FTE Cost' slider to forecast baseline cash burn."
    elif "npv" in lower_text or "dcf" in lower_text or "value" in lower_text:
        bot_response = "NPV (Net Present Value) is calculated using a Discounted Cash Flow (DCF) model. It takes future budget requirements and shrinks them based on inflation and our WACC, giving you the true 'today' cost of an asset."
    elif "upload" in lower_text or "data" in lower_text or "csv" in lower_text:
        bot_response = "To upload your own data, navigate to the 'Data Management' tab. Make sure your CSV file matches the exact column names listed in the Data Dictionary on that page!"
    elif "hello" in lower_text or "hi" in lower_text:
        bot_response = "Hello! I am your virtual OPCM Advisor. I can explain financial terms (like WACC, FTE, or NPV) or help you navigate the dashboard features. What would you like to know?"
    elif "namuuna" in lower_text or "hire me" in lower_text or "secret" in lower_text:
        bot_response = "🤫 EASTER EGG UNLOCKED! Namuuna is the brilliant developer behind this dashboard. She possesses an incredibly rare blend of advanced Python engineering and corporate finance strategy. Sanofi should definitely hire her for the OPCM Trainee role! 🎉"
    else:
        bot_response = "That's a great question! However, I am currently programmed to assist specifically with core terms like WACC, NPV, FTE, and Data Uploads. Try asking me to define one of those!"
        
    # Append Bot Message
    chat_data.append({"sender": "bot", "text": bot_response})
    
    # Render UI Bubbles
    chat_ui = []
    for msg in chat_data:
        if msg["sender"] == "user":
            bubble = html.Div(html.Div(msg["text"], className="p-2 bg-primary text-white rounded-3 shadow-sm d-inline-block"), className="text-end mb-3")
        else:
            bubble = html.Div(html.Div(msg["text"], className="p-2 bg-white border rounded-3 shadow-sm d-inline-block text-dark"), className="text-start mb-3")
        chat_ui.append(bubble)
        
    return chat_ui, chat_data, ""

# TAB 3: Data Store Management (Reactive Master Callback)
@app.callback(
    [
        Output('app-data-store', 'data'),
        Output('upload-status', 'children'),
        Output('generate-status', 'children'),
        Output('data-status-alert', 'children')
    ],
    [
        Input('upload-data', 'contents'),
        Input('btn-generate-data', 'n_clicks')
    ],
    [
        State('upload-data', 'filename'),
        State('synth-project-count', 'value')
    ]
)
def manage_master_data(upload_contents, gen_clicks, filename, synth_count):
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else ""
    
    if not trigger_id or trigger_id not in ['btn-generate-data', 'upload-data']:
        # Initial Application Load
        return initial_app_data.to_dict('records'), "", "", dbc.Badge("Default Data Loaded", color="success", className="p-2")
    
    if trigger_id == 'btn-generate-data':
        new_df = generate_synthetic_data(synth_count if synth_count else 500)
        return new_df.to_dict('records'), "", f"✅ Generated {synth_count} projects successfully!", dbc.Badge("Synthetic Data Active", color="primary", className="p-2")
        
    elif trigger_id == 'upload-data' and upload_contents is not None:
        content_type, content_string = upload_contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename.lower():
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in filename.lower():
                df = pd.read_excel(io.BytesIO(decoded))
            else:
                return dash.no_update, "❌ Unsupported file format.", "", dash.no_update
                
            required = ['Project_ID', 'Therapeutic_Area', 'Region', 'Stage', 'Quarter', 'Required_FTEs', 'Allocated_FTEs', 'Budget_USD_k']
            if not all(col in df.columns for col in required):
                return dash.no_update, "❌ Missing required columns. Check Data Dictionary.", "", dash.no_update
                
            if 'FTE_Variance' not in df.columns:
                df['FTE_Variance'] = df['Allocated_FTEs'] - df['Required_FTEs']
                
            return df.to_dict('records'), f"✅ Uploaded {filename} successfully!", "", dbc.Badge("Custom Dataset Active", color="warning", text_color="dark", className="p-2")
            
        except Exception as e:
            return dash.no_update, f"❌ Error processing file: {str(e)}", "", dash.no_update
            
    return dash.no_update, "", "", dash.no_update

# Global Filters Population Callback
@app.callback(
    [
        Output('region-filter', 'options'), Output('region-filter', 'value'),
        Output('ta-filter', 'options'), Output('ta-filter', 'value')
    ],
    Input('app-data-store', 'data')
)
def update_global_filters(data):
    if not data:
        return [], [], [], []
    df = pd.DataFrame(data)
    regions = sorted(df['Region'].unique())
    tas = sorted(df['Therapeutic_Area'].unique())
    
    r_options = [{'label': r, 'value': r} for r in regions]
    ta_options = [{'label': t, 'value': t} for t in tas]
    
    return r_options, regions, ta_options, tas

# TAB 1: Capacity Management Callback
@app.callback(
    [
        Output("kpi-projects", "children"), Output("kpi-fte-variance", "children"),
        Output("kpi-fte-variance", "className"), Output("kpi-budget", "children"),
        Output("variance-bar-chart", "figure"),
    ],
    [Input('app-data-store', 'data'), Input("region-filter", "value"), Input("ta-filter", "value")]
)
def update_capacity_tab(data, selected_regions, selected_tas):
    if not data: return "0", "0", "text-muted", "$0", go.Figure()
    
    app_data = pd.DataFrame(data)
    if not selected_regions: selected_regions = []
    if not selected_tas: selected_tas = []
    
    filtered_df = app_data[
        (app_data['Region'].isin(selected_regions)) & 
        (app_data['Therapeutic_Area'].isin(selected_tas)) &
        (app_data['Quarter'] == 'Q4 2026')
    ]
    
    num_projects = len(filtered_df)
    total_fte_variance = filtered_df['FTE_Variance'].sum()
    fte_color_class = "text-danger fw-bold" if total_fte_variance < 0 else "text-success fw-bold"
    total_budget_m = filtered_df['Budget_USD_k'].sum() / 1000
    formatted_budget = f"${total_budget_m:,.2f} M"
    
    if not filtered_df.empty:
        variance_df = filtered_df.groupby('Therapeutic_Area', as_index=False)['FTE_Variance'].sum()
        variance_df = variance_df.sort_values(by='FTE_Variance')
        fig_bar = px.bar(variance_df, x='FTE_Variance', y='Therapeutic_Area', orientation='h', title='Net Capacity (FTE) Variance by Therapeutic Area (Q4 2026)', color='FTE_Variance', color_continuous_scale=px.colors.diverging.RdBu)
        fig_bar.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=50, b=20))
    else:
        fig_bar = go.Figure().update_layout(title="No data available", template="plotly_white")
        
    return f"{num_projects:,}", f"{total_fte_variance:,.0f}", fte_color_class, formatted_budget, fig_bar

@app.callback(Output('bar-click-explanation', 'children'), Input('variance-bar-chart', 'clickData'))
def display_bar_explanation(clickData):
    if clickData is None: return dbc.Alert("💡 Click on a bar above to see a detailed explanation.", color="info", is_open=True, className="shadow-sm")
    ta_name = clickData['points'][0]['y']
    variance = clickData['points'][0]['x']
    impact = "shortage" if variance < 0 else "surplus" if variance > 0 else "perfect balance"
    color = "danger" if variance < 0 else "success"
    return dbc.Alert(f"Insight: You clicked on {ta_name}. It has a {impact} of {abs(variance)} FTEs.", color=color, is_open=True, className="shadow-sm")

# TAB 2: CFA Engine - Multi-Dimensional Plot, DCF & DataTable
@app.callback(
    [
        Output("financial-graph", "figure"),
        Output("dynamic-financial-text", "children"),
        Output("financial-data-table", "data"), Output("financial-data-table", "columns")
    ],
    [
        Input('app-data-store', 'data'),
        Input("region-filter", "value"), Input("ta-filter", "value"),
        Input("fte-cost-slider", "value"), Input("wacc-slider", "value"), 
        Input("inflation-slider", "value"), Input("view-mode-selector", "value")
    ]
)
def update_cfa_financials(data, regions, tas, fte_cost, wacc_pct, inflation_pct, view_mode):
    if not data: 
        return go.Figure(), html.Span("No data loaded."), [], []
        
    app_data = pd.DataFrame(data)
    if not regions: regions = []
    if not tas: tas = []
    
    # Base filter
    base_df = app_data[(app_data['Region'].isin(regions)) & (app_data['Therapeutic_Area'].isin(tas))].copy()
    
    # Math Constants
    wacc = wacc_pct / 100.0
    inflation = inflation_pct / 100.0
    q_map = {'Q1 2026': 0, 'Q2 2026': 1, 'Q3 2026': 2, 'Q4 2026': 3}
    prob_dict = {'Pre-clinical': 0.05, 'Phase I': 0.10, 'Phase II': 0.30, 'Phase III': 0.60}
    stage_order = ['Pre-clinical', 'Phase I', 'Phase II', 'Phase III']
    
    if base_df.empty:
        fig = go.Figure().update_layout(title="No data available", template="plotly_white")
        return fig, html.Span("Insufficient data.", className="text-warning"), [], []
        
    # CFA Math Engine
    base_df['Period'] = base_df['Quarter'].map(q_map)
    base_df['Cash_Burn_Rate'] = (base_df['Allocated_FTEs'] * fte_cost / 4) + (base_df['Budget_USD_k'] * 1000)
    base_df['Escalated_Cash_Burn'] = base_df['Cash_Burn_Rate'] * ((1 + inflation) ** base_df['Period'])
    base_df['Probability'] = base_df['Stage'].map(prob_dict)
    base_df['Prob_Adjusted_Cost'] = base_df['Escalated_Cash_Burn'] * base_df['Probability']
    base_df['DCF_Impact'] = base_df['Prob_Adjusted_Cost'] / ((1 + wacc / 4) ** base_df['Period'])
    
    base_df = base_df.sort_values(by=['Quarter', 'Stage', 'Therapeutic_Area'])
    
    max_fte = base_df['Allocated_FTEs'].max()
    max_dcf = base_df['DCF_Impact'].max()
    
    # ---------------------------------------------
    # Multi-Dimensional Visualizations
    # ---------------------------------------------
    if view_mode == "2D":
        # 2D Classic Box Plot
        fig = px.box(
            base_df, x='Stage', y='DCF_Impact', color='Stage',
            labels={'DCF_Impact': 'NPV Liability ($)'},
            category_orders={'Stage': stage_order}
        )
        fig.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
        
    elif view_mode == "3D":
        # 3D Static Spatial Scatter
        fig = px.scatter_3d(
            base_df, x='Stage', y='Allocated_FTEs', z='DCF_Impact',
            color='Therapeutic_Area', size='Budget_USD_k', opacity=0.8,
            labels={'DCF_Impact': 'NPV Liability ($)', 'Allocated_FTEs': 'Allocated FTEs', 'Therapeutic_Area': 'Therapeutic Area'},
            category_orders={'Stage': stage_order}
        )
        fig.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=0, b=0))
        
    else:
        # 4D Animated Cinematic View
        fig = px.scatter_3d(
            base_df, x='Stage', y='Allocated_FTEs', z='DCF_Impact',
            color='Therapeutic_Area', size='Budget_USD_k',
            animation_frame='Quarter', animation_group='Project_ID',
            opacity=0.8, range_y=[0, max_fte * 1.1], range_z=[0, max_dcf * 1.1],
            labels={'DCF_Impact': 'NPV Liability ($)', 'Allocated_FTEs': 'Allocated FTEs', 'Therapeutic_Area': 'Therapeutic Area'},
            category_orders={'Stage': stage_order, 'Quarter': sorted(q_map.keys())}
        )
        fig.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=0, b=0))
    
    # ---------------------------------------------
    # Dash DataTable Generation
    # ---------------------------------------------
    table_df = base_df.groupby('Therapeutic_Area').agg({
        'Escalated_Cash_Burn': 'sum',
        'DCF_Impact': 'sum'
    }).reset_index()
    table_df.rename(columns={
        'Escalated_Cash_Burn': 'Total 2026 Cash Burn',
        'DCF_Impact': 'Total 2026 NPV Liability'
    }, inplace=True)
    
    for col in table_df.columns:
        if col != 'Therapeutic_Area':
            table_df[col] = table_df[col].apply(lambda x: f"${x:,.0f}")
            
    table_columns = [{"name": i, "id": i} for i in table_df.columns]
    table_data = table_df.to_dict('records')

    # ---------------------------------------------
    # Dynamic CFA Narrative
    # ---------------------------------------------
    total_adj_burn = base_df['Prob_Adjusted_Cost'].sum()
    total_npv = base_df['DCF_Impact'].sum()
    
    high_inf = inflation + 0.01
    high_inf_escalated = base_df['Cash_Burn_Rate'] * ((1 + high_inf) ** base_df['Period'])
    high_inf_adj = high_inf_escalated * base_df['Probability']
    high_inf_pv = high_inf_adj / ((1 + wacc / 4) ** base_df['Period'])
    inf_impact = high_inf_pv.sum() - total_npv
    
    summary_text = html.Span([
        f"Assuming a blended FTE cost of ${fte_cost:,.0f} and a Corporate WACC of {wacc_pct:.1%}%, ",
        f"the total probability-adjusted cash burn for 2026 is forecasted at ",
        html.Strong(f"${total_adj_burn/1e6:,.2f} million"), 
        ". This represents a cumulative Net Present Value (NPV) resource liability of ",
        html.Strong(f"${total_npv/1e6:,.2f} million"), 
        ". A 1% macro increase in the quarterly inflation factor will accelerate the firm's hurdle rate deficit by approximately ",
        html.Strong(f"${inf_impact:,.0f}"), " this year alone."
    ])

    return fig, summary_text, table_data, table_columns

# Educational Tiered Click Interaction Engine
@app.callback(
    [Output('graph-click-explanation', 'children'), Output('click-history-store', 'data')],
    Input('financial-graph', 'clickData'),
    [
        State('region-filter', 'value'), State('ta-filter', 'value'),
        State('wacc-slider', 'value'), State('click-history-store', 'data')
    ]
)
def display_educational_insight(click_data, regions, tas, wacc_pct, click_history):
    if not click_data:
        return dash.no_update, dash.no_update
        
    stage = click_data['points'][0]['x']
    # 2D scatters store NPV in y, 3D scatters store it in z
    dcf_val = click_data['points'][0].get('z', click_data['points'][0].get('y', 0))
    
    # Custom Double-Click State Logic
    if click_history is None:
        click_history = {'stage': None, 'clicks': 0}
        
    prev_stage = click_history.get('stage')
    clicks = click_history.get('clicks', 0)
    
    if stage == prev_stage:
        clicks += 1
    else:
        clicks = 1
        
    new_history = {'stage': stage, 'clicks': clicks}
    
    if clicks >= 2:
        # Advanced Glossary View (Triggered on Double-Click)
        new_history['clicks'] = 0 # Reset so they can toggle back
        adv_insight = f"""
**🎓 Advanced Corporate Glossary**

* **FTE (Full-Time Equivalent):** A unit that indicates the workload of an employed person. An FTE of 1.0 is equivalent to a full-time worker. Our model calculates baseline cash burn by multiplying FTEs by the blended rate.
* **Blended Cost Assumption:** Rather than tracking individual junior/senior salaries, enterprise models use a 'blended' average to rapidly forecast macro resource liabilities.
* **Hurdle Rate Deficit:** The gap between the expected return of an R&D asset and the Corporate WACC. If a project in {stage} fails to exceed the {wacc_pct:.1f}% discount rate, it destroys shareholder value, creating a 'deficit'.
* **Probability-Adjusted Escalation:** Early-stage clinical trials have a high failure rate. The model mitigates this by aggressively discounting the future liability of {stage} by its historical probability of failure.
        """
        glossary_item = dbc.AccordionItem([dcc.Markdown(adv_insight)], title="Advanced Corporate Glossary (Triggered via Double-Click)")
        accordion = dbc.Accordion([glossary_item], start_collapsed=False, always_open=True, className="mt-2")
        alert = dbc.Alert([
            html.H5(f"💡 Advanced Analysis: {stage}", className="alert-heading fw-bold"),
            html.P("You double-clicked this phase. Here is the advanced terminology breakdown:", className="mb-0 text-muted"),
            accordion
        ], color="dark", is_open=True, className="shadow-sm border-0")
        return alert, new_history

    # 1. Board View
    board_content = html.Div([
        html.H6(f"Executive Bottom Line for {stage}:", className="fw-bold"),
        html.P(f"This selected project carries an expected Net Present Value (NPV) liability of ${dcf_val:,.0f} today.")
    ])
    board_item = dbc.AccordionItem([board_content], title="1. The Board View (Executive Summary)")
    
    # 2. Analyst View
    analyst_content = html.Div([
        html.H6("Corporate Finance Metrics:", className="fw-bold"),
        html.Ul([
            html.Li(f"Corporate Discount Rate (WACC) Applied: {wacc_pct:.1f}%"),
            html.Li(f"Calculated Discounted Cash Flow (DCF): ${dcf_val:,.0f}"),
            html.Li("Risk Logic: Base budget escalated by inflation, multiplied by historical probability of success, and discounted to Period 0.")
        ])
    ])
    analyst_item = dbc.AccordionItem([analyst_content], title="2. The Analyst View (Detailed Breakdown)")
    
    # 3. Beginner View
    beginner_insight = f"""
**What is WACC ({wacc_pct:.1f}%)?**  
Think of **WACC (Weighted Average Cost of Capital)** like the "interest rate on a credit card" for Sanofi. If the company wants to fund this project, the money isn't free—it costs the company {wacc_pct:.1f}% per year to gather those funds from investors and banks. If a project doesn't generate returns higher than this rate, the company is technically losing money!

**What is Net Present Value (NPV)?**  
Money loses value over time (due to inflation). **NPV** is like a time-machine for money. If we have to spend cash on this {stage} project over the next year, that *future* money is "discounted" back to *today's* value using the {wacc_pct:.1f}% WACC rate so we know exactly what it costs us right now. 
    """
    beginner_item = dbc.AccordionItem([dcc.Markdown(beginner_insight)], title="3. The Beginner View (Finance 101)")
    
    accordion = dbc.Accordion([board_item, analyst_item, beginner_item], start_collapsed=False, always_open=True, className="mt-2")
    
    alert = dbc.Alert([
        html.H5("💡 Interactive Financial Insights", className="alert-heading fw-bold"),
        html.P("Double-click the same phase in the graph to reveal the Advanced Glossary.", className="mb-0 text-muted small"),
        accordion
    ], color="info", is_open=True, className="shadow-sm border-0")
    
    return alert, new_history

# Easter Egg Callback
@app.callback(
    Output("easter-egg-output", "children"),
    Input("easter-egg-trigger", "n_clicks")
)
def trigger_easter_egg(n_clicks):
    if n_clicks and n_clicks >= 5:
        return dbc.Alert([
            html.H4("🎉 Easter Egg Found! 🎉", className="alert-heading fw-bold"),
            html.P("You clicked the footer 5 times!"),
            html.Hr(),
            html.P("Secret Message: Namuuna is the ultimate candidate for the Data Analyses & Application Development Trainee role. Hire her!", className="mb-0 fw-bold")
        ], color="success", dismissable=True, className="position-fixed bottom-0 end-0 m-4 shadow-lg", style={"zIndex": 9999})
    return dash.no_update

if __name__ == "__main__":
    app.run(debug=True, port=8050)
