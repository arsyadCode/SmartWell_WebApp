import dash, os, webbrowser
from dash import dcc, html, Output, Input, State
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash.dependencies import ALL

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title="Smart Well Monitoring", suppress_callback_exceptions=True)
server = app.server

# Load data from CSV files
df = pd.read_csv("Data/monthly_rate_per_day_combined_with_pi.csv")
df2 = pd.read_csv("Data/pi_sensor_per_month.csv")
dfPlot = pd.read_csv("Data/combined_view.csv")

# Convert date columns to datetime format
df['MDATE'] = pd.to_datetime(df['MDATE'], format='%m/%d/%Y')
df2['START_TIME'] = pd.to_datetime(df2['START_TIME'], format='%Y-%m-%d')
dfPlot['DATE_STAMP'] = pd.to_datetime(dfPlot['DATE_STAMP'], format='%d/%m/%Y %H:%M')

# Dropdown options
dropdown_options = sorted(df['Universal'].unique())

Objects = {}
for name in dropdown_options:
    parents = name.split("-")
    main, sub, detail = parents[0], parents[1], parents[2]

    field_key = f"{main}ekapai Field"
    platform_key = f"Platform {sub}"

    if field_key not in Objects:
        Objects[field_key] = {}
    if platform_key not in Objects[field_key]:
        Objects[field_key][platform_key] = []

    Objects[field_key][platform_key].append(name)

def create_nested_checkboxes(structure):
    elements = []
    
    for main, subs in structure.items():
        main_checkbox = html.Div([
            dcc.Checklist(
                options=[{'label': main, 'value': main}],
                value=[main],
                id={'type': 'main-checkbox', 'name': f'checkbox-{main}'},
                inline=True,
                labelStyle={'display': 'flex', 'marginBottom': '19px', 'gap': '15px', 'alignItems': 'center', 'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'},
                inputStyle={'transform': 'scale(1.5)', 'borderRadius': '6px'}
            )
        ], style={'marginLeft': '8px'})
        
        sub_elements = []
        for sub, details in subs.items():
            sub_checkbox = dcc.Checklist(
                options=[{'label': sub, 'value': sub}],
                id={'type': 'sub-checkbox', 'name': f'checkbox-{main}-{sub}'},
                value=[sub] if 'Platform '+dropdown_options[0].split('-')[1] == sub else [],
                inline=True,
                labelStyle={'display': 'flex', 'marginBottom': '19px', 'gap': '15px', 'alignItems': 'center', 'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'},
                inputStyle={'transform': 'scale(1.5)', 'borderRadius': '6px'}
            )


            detail_elements = dcc.Checklist(
                options=[{'label': detail, 'value': detail} for detail in details],
                id={'type':'detail-checkbox', 'name': f'checkbox-{main}-{sub}-details'},
                value=[dropdown_options[0]] if dropdown_options[0] in details else [],
                inline=True,
                labelStyle={'display': 'flex', 'marginBottom': '19px', 'gap': '15px', 'alignItems': 'center', 'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'},
                inputStyle={'transform': 'scale(1.5)', 'borderRadius': '6px'}
            )
            
            sub_elements.append(html.Div([sub_checkbox, html.Div(detail_elements, style={'marginLeft': '32px'})]))
        
        elements.append(html.Div([main_checkbox, html.Div(sub_elements, style={'marginLeft': '32px'})]))
    return elements

# App Layout
app.layout = html.Div([
    html.Header([
        html.Nav([
            html.Nav([
                html.Div([
                    html.Div([
                        html.Img(src="assets/logo.png", style={'width': '50px', 'height': '38.19px'}),
                        html.Div([
                            html.H1("WENNI", style={'fontWeight': '600', 'fontSize': "20px", 'color': '#006CB8', 'lineHeight': "25.2px"}),
                            html.P("Well Forecast and Monitoring", style={'fontWeight': '400', 'fontSize': "14px", 'color': '#9B9797', 'lineHeight': '17.64px'})
                        ], style={'flexDirection': 'column'})
                    ], style={'display': 'flex', 'alignItems': 'center', 'gap': '13.11px', 'paddingTop': '27px'}),
                    html.Img(src="assets/PHM.png", style={'width': '174px'})
                ], style={'backgroundColor': 'white', 'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'width': '100%', 'paddingLeft': '37px', 'paddingRight': '37px', 'borderBottomLeftRadius': "20px", 'borderBottomRightRadius': '20px'})
            ], style={'backgroundColor': '#C3304A', 'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'width': '100%', 'paddingBottom': '20px', 'borderBottomLeftRadius': "20px", 'borderBottomRightRadius': '20px'}),
            html.Nav([
                html.Div([
                    html.P("Historical", style={"fontWeight": "800", "fontSize": '16px', "color": 'white'}),
                    html.P("DCA", style={"fontWeight": "400", 'fontSize': '16px', "color": 'white'}),
                    html.P('Forecast', style={"fontWeight": "400", "fontSize": '16px', "color": 'white'})
                ], style={'display': 'flex', 'alignItems': 'center', 'gap': '71px', 'paddingLeft': '35px'}),
                html.Div([
                    html.H1('Admin 1', style={"fontWeight": "700", 'fontSize': '16px', "color": 'white'}),
                    html.P('Role Admin', style={"fontWeight": "400", "fontSize": '14px', "color": 'white'})
                ], style={'display': 'flex', 'flexDirection': 'column', 'gap':'1px', 'paddingRight': '35px'})
            ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-between', 'width': '100%', 'paddingLeft': '76px', 'paddingRight': '76px', 'paddingTop': '30px', 'paddingBottom': '30px'})
        ], style={'backgroundColor': '#3F849B', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'space-between', 'alignItems': 'center', 'width': '100%'})
    ], style={'width': '100%', 'display': "flex", 'flexDirection': 'column'}),
    html.Div(style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'width': "100%", 'paddingBottom': '20px'}, children=[
        html.Div([    
            html.Button(children=[
                html.Img(src="assets/upload.png", style={'width': '18px', 'height': '15.65px'}),
                html.H1("Upload File", style={'fontSize': '16px', 'fontWeight': '500', 'color': '#3F849B'})
            ], id="open-upload-button", n_clicks=0, style={'marginTop': '50px', 'display': 'flex', 'gap': '8px', 'justifyItems': 'center', 'border': 'none', 'backgroundColor': 'transparent'}),
            html.Div(
                id="upload-modal",
                children=[
                    html.Div([
                        dcc.Upload(
                            id="file-upload",
                            children=[
                                html.Img(src="assets/uploadv2.png"),
                                html.H6("Browse file (.csv) or (.xlsx) to upload")
                            ],
                            style={
                                'width': '779px', 'height': '286px', 'lineHeight': '60px', 'display': 'flex', 'flexDirection': 'column',
                                'borderWidth': '1px', 'borderStyle': 'dashed', 'borderColor': '#B6B2B2',
                                'borderRadius': '15px', 'textAlign': 'center', 'alignItems': 'center', 'justifyItems': 'center', 'justifyContent': 'center'
                            },
                            multiple=False
                        ),
                        html.Button("Close", id="close-upload-button", n_clicks=0, style={'width': '100%', 'height': '63px', 'backgroundColor': '#3F849B', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'color': '#F9F9F9', 'fontSize': '16px', 'fontWeight': '500', 'border': 'none', 'borderRadius': '12px'})
                    ], style={'padding': '44px', 'backgroundColor': 'white', 'borderRadius': '5px', 'border': '1px solid #3F849B', 'display': 'flex', 'flexDirection': 'column', 'gap': '12px'}),
                ],
                style={
                    'display': 'none',
                    'position': 'fixed', 'top': '0', 'left': '0', 'width': '100%', 'height': '100%',
                    'backgroundColor': 'rgba(0, 0, 0, 0.5)', 'alignItems': 'center', 'justifyContent': 'center'
                }
            ),
            html.Div(style={'display': 'flex', 'gap': 28, 'paddingTop': '17px'}, children=[
                html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '10px'}, children=[
                    html.Div(className='feature-container', style={'border': '1px solid #3F849B', 'padding': '0', 'borderRadius': '16px', 'width': '174px', 'height': '93px'}, children=[
                        html.H1('Legend', className='Feature-title', style={'color': 'white', 'fontWeight': '700', 'fontSize': '16px', 'padding': '8px 17px', 'backgroundColor': '#3F849B', 'borderRadius': '10px'}),
                        html.Div(style={'padding': '10px 25px'}, children=[
                            dcc.Checklist(
                                id='legend-status',
                                options=[
                                    {'label': 'Enable', 'value': 'on'},
                                ],
                                value=['on'], 
                                labelStyle={'display': 'flex', 'marginBottom': '9.5px', 'gap': '15px', 'alignItems': 'center', 'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'},
                                inputStyle={'transform': 'scale(1.5)', 'borderRadius': '6px'}
                            ),
                        ]),
                    ]),
                    html.Div(className='feature-container', style={'border': '1px solid #3F849B', 'padding': '0', 'borderRadius': '16px', 'width': '174px', 'height': '223px'}, children=[
                        html.H1('Object', className='Feature-title', style={'color': 'white', 'fontWeight': '700', 'fontSize': '16px', 'padding': '8px 17px', 'backgroundColor': '#3F849B', 'borderRadius': '10px'}),
                        html.Div(style={'padding': '10px 25px'}, children=[
                            dcc.Checklist(
                                id="figures-checklist",
                                options=[
                                    {'label': "Oil Rate", 'value': "Oil Rate"},
                                    {'label': "Water Rate", 'value': "Water Rate"},
                                    {'label': "Gas Rate", 'value': "Gas Rate"},
                                    {'label': "WHP Rate", 'value': "WHP Rate"},
                                    {'label': "WHT Rate", 'value': "WHT Rate"}
                                ],
                                value=["Oil Rate", "Water Rate", "Gas Rate", "WHP Rate", "WHT Rate"],
                                labelStyle={'display': 'flex', 'marginBottom': '9.5px', 'gap': '15px', 'alignItems': 'center', 'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'},
                                inputStyle={'transform': 'scale(1.5)', 'borderRadius': '6px'}
                            ),
                        ])
                    ]),
                    html.Div(className='feature-container', style={'border': '1px solid #3F849B', 'padding': '0', 'borderRadius': '16px', 'width': '174px', 'height': '130px'}, children=[
                        html.H1('Plot Area', className='Feature-title', style={'color': 'white', 'fontWeight': '700', 'fontSize': '16px', 'padding': '8px 17px', 'backgroundColor': '#3F849B', 'borderRadius': '10px'}),
                        html.Div(style={'padding': '10px 25px'}, children=[
                            dcc.RadioItems(
                                id="",
                                options=[
                                    {'label': 'Single Plot', 'value': 'single', 'disabled': True},
                                    {'label': 'Multi-Plot', 'value': 'multi'},
                                ],
                                value='single', 
                                labelStyle={'display': 'flex', 'marginBottom': '9.5px', 'gap': '15px', 'alignItems': 'center', 'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'},
                                inputStyle={'transform': 'scale(1.5)', 'borderRadius': '6px'},
                            ),
                        ])
                    ]),
                ]),
                html.Div(style={"width": '50rem'}, children=[
                    dcc.Tabs(id='tab-container',
                        value=dropdown_options[0],
                        children=[],
                        content_style={'textAlign':'center'}
                    ),
                    html.Div(style={'border': '1px solid grey', 'padding': '21px', 'borderBottomLeftRadius': '30px', 'borderBottomRightRadius': '30px', 'borderTopRightRadius': '30px', 'width': '100%'}, children=[
                        dbc.Row([
                            html.Div(id="graphs-container", style={'margin': '20px'}),
                        ]),
                    ])            
                ]),
                html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '10px', 'width': '25rem'}, children=[
                    html.Div(className='feature-container', style={'border': '1px solid #3F849B', 'padding': '0', 'borderRadius': '16px', 'width': '229px', 'minHeight': '40px'}, children=[
                        html.H1('Objects', className='Feature-title', style={'color': 'white', 'fontWeight': '700', 'fontSize': '16px', 'padding': '8px 17px', 'backgroundColor': '#3F849B', 'borderRadius': '10px'}),
                        html.Div(style={'padding': '10px', 'display': 'flex', 'flexDirection': 'column', 'gap': '10px'}, children=[
                            html.Div(style={'fontWeight': '400', 'fontSize': '14px', 'color': '#616161', 'display': 'none'}, children=[
                                html.Label('Select Well:', style={'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'}),
                                dcc.Dropdown(
                                    id='well-dropdown', 
                                    options=[{'label': well, 'value': well} for well in dropdown_options],
                                    value=dropdown_options[0],
                                    clearable=False,
                                )
                            ]),
                            html.Div(children=create_nested_checkboxes(Objects))
                        ])
                    ]), 
                ]),
                dcc.Location(id="page-reloader", refresh=True)
            ]),
        ]),
    ]),
])

@app.callback(
    Output({'type': 'sub-checkbox', 'name': ALL}, 'labelStyle'),
    Output({'type': 'sub-checkbox', 'name': ALL}, 'value'),
    Input({'type': 'main-checkbox', 'name': ALL}, 'value'),
    State({'type': 'sub-checkbox', 'name': ALL}, 'labelStyle'),
    State({'type': 'sub-checkbox', 'name': ALL}, 'value')
)
def update_sub_checkboxes(main_checked, sub_label_style, value):
    defaultStyle = {'display': 'flex', 'marginBottom': '19px', 'gap': '15px', 'align-items': 'center', 'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'}
    if main_checked[0] != [] :
        return [defaultStyle for _ in sub_label_style], value
    else:
        return [{'display': 'none'} for _ in sub_label_style], [[] for _ in value]

@app.callback(
    Output({'type': 'detail-checkbox', 'name': ALL}, 'labelStyle'),
    Input({'type': 'sub-checkbox', 'name': ALL}, 'value')
)
def update_detail_checkboxes(sub_checked):
    default_style = {'display': 'flex', 'marginBottom': '19px', 'gap': '15px', 'align-items': 'center', 'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'}
    style = []
    for items in sub_checked:
        if items != []:
            style.append(default_style)
        else: 
            style.append({'display': 'none'})
    return style

@app.callback(
    Output('well-dropdown', 'value'),
    Input('tab-container', 'value'),
)
def showData(tab_container):
    return tab_container

@app.callback(
    Output('tab-container', 'children'),
    Input({'type': 'detail-checkbox', 'name': ALL}, 'value'),
)
def update_tabs(selected_items):
    tabs = []
    items = [*selected_items[0], *selected_items[1]]
    for value in items:
        tab_button = dcc.Tab(
            label=value,
            value=value,
            style={'border': '1px solid #909090',  'backgroundColor': 'white', 'width': '141px',  'height': '39px',  'borderTopLeftRadius': '10px',  'borderTopRightRadius': '10px', 'display': 'flex', 'alignItems': 'center', 'justifyItems': 'center', 'display': 'flex', 'alignItems': 'center', 'justifyItems': 'center'},                   
            selected_style={ 'border': '1px solid #909090',  'backgroundColor': '#BFF2DA', 'width': '141px',  'height': '39px',  'borderTopLeftRadius': '10px',  'borderTopRightRadius': '10px', 'display': 'flex', 'alignItems': 'center', 'justifyItems': 'center', 'textAlign':'center'},
        )               
        tabs.insert(0, tab_button)
    return tabs

# Function to create individual figures
def create_figure(x, y, x2, y2, ylabel, color, show_legend):
    fig = go.Figure()

    # Add main data line
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode='lines',
        line=dict(color=color, width=1.5),
        name="Monthly production data",
        showlegend=show_legend
    ))

    # Add test and sensor data
    fig.add_trace(go.Scatter(
        x=x2, y=y2,
        mode='markers',
        marker=dict(color='red', size=8),
        name="Test and sensor data",
        showlegend=show_legend
    ))

    # Update layout
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title=ylabel,
        legend_title="Legend",
        template="simple_white",
        hovermode="x"
    )

    return fig

# Callback to update figures
@app.callback(
    Output("graphs-container", "children"),
    [Input("well-dropdown", "value"),
     Input("figures-checklist", "value")],
     Input('legend-status', 'value'),
)
def update_graphs(selected_well, selected_figures, legend_status):
    show_legend = 'on' in legend_status
    selected_data = df[df['Universal'] == selected_well]
    selected_data2 = df2[df2['Universal'] == selected_well]
    plot_data = dfPlot[dfPlot['Universal'] == selected_well]

    figures = []

    if "Oil Rate" in selected_figures:
        fig = create_figure(
            selected_data['MDATE'], selected_data['OIL_per_day'],
            plot_data['DATE_STAMP'], plot_data['CORR_OIL_RATE_STBD'],
            "Oil Rate (bbl/d)", "darkgoldenrod", show_legend
        )
        figures.append(dcc.Graph(figure=fig))

    if "Water Rate" in selected_figures:
        fig = create_figure(
            selected_data['MDATE'], selected_data['WATER_per_day'],
            plot_data['DATE_STAMP'], plot_data['CORR_WTR_RATE_STBD'],
            "Water Rate (bbl/d)", "dodgerblue", show_legend
        )
        figures.append(dcc.Graph(figure=fig))

    if "Gas Rate" in selected_figures:
        fig = create_figure(
            selected_data['MDATE'], selected_data['GAS_per_day'],
            plot_data['DATE_STAMP'], plot_data['CORR_GAS_RES_RATE_MMSCFD'],
            "Gas Rate (mmscfd)", "darkturquoise", show_legend
        )
        figures.append(dcc.Graph(figure=fig))

    if "WHP Rate" in selected_figures:
        fig = create_figure(
            selected_data2['START_TIME'], selected_data2['WHP'],
            plot_data['DATE_STAMP'], plot_data['WHP_BARG'],
            "WHP Rate (barg)", "darkslateblue", show_legend
        )
        figures.append(dcc.Graph(figure=fig))

    if "WHT Rate" in selected_figures:
        fig = create_figure(
            selected_data2['START_TIME'], selected_data2['WHT'],
            plot_data['DATE_STAMP'], plot_data['WHT_DEG_C'],
            "WHT Rate (°C)", "darkslateblue", show_legend
        )
        figures.append(dcc.Graph(figure=fig))

    return figures

# Run Dash app
if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        webbrowser.open_new("http://127.0.0.1:8050/")
    app.run_server(debug=True, dev_tools_ui=False)