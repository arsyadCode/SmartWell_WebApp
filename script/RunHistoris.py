import pandas as pd
import os, webbrowser
from dash import dcc, html, Input, Output, State, ALL, callback, Dash
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import base64

csv_file = "Data/monthly_rate_per_day_combined_with_pi.csv"
df = pd.read_csv(csv_file)
df['MDATE'] = pd.to_datetime(df['MDATE'], format='%m/%d/%Y')

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Smart Well Monitoring - Universitas Pertamina"

Objects = {}
for name in df['Universal'].unique():
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
                value=[sub] if 'Platform L' == sub else [],
                inline=True,
                labelStyle={'display': 'flex', 'marginBottom': '19px', 'gap': '15px', 'alignItems': 'center', 'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'},
                inputStyle={'transform': 'scale(1.5)', 'borderRadius': '6px'}
            )


            detail_elements = dcc.Checklist(
                options=[{'label': detail, 'value': detail} for detail in details],
                id={'type':'detail-checkbox', 'name': f'checkbox-{main}-{sub}-details'},
                value=['B-L-18'] if 'B-L-18' in details else [],
                inline=True,
                labelStyle={'display': 'flex', 'marginBottom': '19px', 'gap': '15px', 'alignItems': 'center', 'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'},
                inputStyle={'transform': 'scale(1.5)', 'borderRadius': '6px'}
            )
            
            sub_elements.append(html.Div([sub_checkbox, html.Div(detail_elements, style={'marginLeft': '32px'})]))
        
        elements.append(html.Div([main_checkbox, html.Div(sub_elements, style={'marginLeft': '32px'})]))
    return elements

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
    html.Div(style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center'}, children=[
        html.Div(style={'width': "100%", 'alignItems': 'start', 'display': 'flex', 'paddingLeft': '370px'}, children=[    
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
        ]),
        html.Div(style={'display': 'flex','justifyContent': 'center', 'width': "100rem", 'padding': '20px', 'gap': '30px'}, children=[
            html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '10px', 'width': '25rem', 'alignItems': 'end'}, children=[
                html.Div(className='feature-container', style={'border': '1px solid #3F849B', 'padding': '0', 'borderRadius': '16px', 'width': '174px', 'height': '130px'}, children=[
                    html.H1('Skala Rate', className='Feature-title', style={'color': 'white', 'fontWeight': '700', 'fontSize': '16px', 'padding': '8px 17px', 'backgroundColor': '#3F849B', 'borderRadius': '10px'}),
                    html.Div(style={'padding': '10px 25px'}, children=[
                        dcc.RadioItems(
                            id="dropdown-scale",
                            options=[
                                {'label': 'Linear', 'value': 'linear'},
                                {'label': 'Logaritmik', 'value': 'log'},
                            ],
                            value='linear', 
                            labelStyle={'display': 'flex', 'marginBottom': '9.5px', 'gap': '15px', 'alignItems': 'center', 'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'},
                            inputStyle={'transform': 'scale(1.5)', 'borderRadius': '6px'}
                        ),
                    ])
                ]),
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
                html.Div(className='feature-container', style={'border': '1px solid #3F849B', 'padding': '0', 'borderRadius': '16px', 'width': '174px', 'height': '163px'}, children=[
                    html.H1('Object', className='Feature-title', style={'color': 'white', 'fontWeight': '700', 'fontSize': '16px', 'padding': '8px 17px', 'backgroundColor': '#3F849B', 'borderRadius': '10px'}),
                    html.Div(style={'padding': '10px 25px'}, children=[
                        dcc.Checklist(
                            id='plot-type',
                            options=[
                                {'label': 'Gas Rate', 'value': 'Gas'},
                                {'label': 'Water Rate', 'value': 'Water'},
                                {'label': 'Oil Rate', 'value': 'Oil'},
                            ],
                            value=['Gas', 'Water', 'Oil'], 
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
                                {'label': 'Single Plot', 'value': 'single'},
                                {'label': 'Multi-Plot', 'value': 'multi', 'disabled': True},
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
                    value='B-L-18',
                    children=[],
                    content_style={'textAlign':'center'}
                ),
                html.Div(style={'border': '1px solid grey', 'padding': '21px', 'borderBottomLeftRadius': '30px', 'borderBottomRightRadius': '30px', 'borderTopRightRadius': '30px', 'width': '100%'}, children=[
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='combined-graph', config={"displayModeBar": False}), width=12),
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
                                id='dropdown-well', 
                                options=[{'label': value, 'value': value} for value in sorted(df['Universal'].unique())],
                                value=sorted(df['Universal'].unique())[0],
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
])

def save_file(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    file_path = os.path.join(csv_file)
    with open(file_path, "wb") as f:
        f.write(decoded)

@app.callback(
    Output("upload-modal", "style"),
    Output("page-reloader", 'href'),
    Input("open-upload-button", "n_clicks"), 
    Input("close-upload-button", "n_clicks"),
    Input('file-upload', 'contents'),
    State('file-upload', 'filename')
)
def toggle_upload_modal(open_clicks, close_clicks, contents, filename):
    default_style = {
        'lineHeight': '60px',
        'borderWidth': '1px', 'borderStyle': 'dashed',
        'borderRadius': '5px', 'textAlign': 'center', 'zIndex': 999, 'backgroundColor': "rgba(0,0,0,0,0.5)",
        'position': 'absolute', 'top': 0, 'bottom': 0, 'left': 0, 'right': 0, 'alignItems': 'center', 'justifyContent': 'center'
    }
    if contents is not None:
        save_file(contents, filename)
        return {**default_style, 'display': 'none'}, "/"
    if open_clicks > close_clicks:
        return {**default_style, 'display': 'flex'}, None
    return {**default_style, 'display': 'none'}, None

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
    Output('dropdown-well', 'value'),
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

@app.callback(
    Output('combined-graph', 'figure'),
    [
     Input('dropdown-well', 'value'),
     Input('dropdown-scale', 'value'),
    ],
     Input('legend-status', 'value'),
     Input('plot-type', 'value'),
)
def update_graph(selected_well, y_axis_type, legend_status, plot_type):
    show_legend = 'on' in legend_status
    gas = 'Gas' in plot_type
    water = 'Water' in plot_type
    oil = 'Oil' in plot_type

    filtered_df = df[df['Universal'] == selected_well]

    fig = go.Figure()

    if(oil):
        fig.add_trace(go.Scatter(
            x=filtered_df['MDATE'],
            y=filtered_df['OIL_per_day'],
            mode='lines',
            name='Oil Rate (stbd)(bbl/d)',
            line=dict(color='green', width=1.5),
            hovertemplate='Oil Rate: %{y:.2f} bbl/d<extra></extra>',
        ))
    if(water):
        fig.add_trace(go.Scatter(
            x=filtered_df['MDATE'],
            y=filtered_df['WATER_per_day'],
            mode='lines',
            name='Water Rate (stbd)(bbl/d)',
            line=dict(color='blue', width=1.5),
            hovertemplate='Water Rate: %{y:.2f} bbl/d<extra></extra>',
        ))
    if(gas):
        fig.add_trace(go.Scatter(
            x=filtered_df['MDATE'],
            y=filtered_df['GAS_per_day'],
            mode='lines',
            name='Gas Rate (mmscfd)(cf/d)',
            line=dict(color='red', width=1.5),
            yaxis='y2',
            hovertemplate='Gas Rate: %{y:.2f} mmscfd<extra></extra>',
        ))

    fig.update_layout(
        xaxis=dict(title='Year'),
        yaxis=dict(title=y_axis_type + ' rate', type=y_axis_type),
        yaxis2=dict(title=y_axis_type + ' rate', overlaying='y', side='right', type=y_axis_type),
        legend=dict(
            orientation='h', 
            x=0.5, 
            xanchor='center', 
            y=1.1,
            visible=show_legend
        ),
        hovermode='x unified',
        template='simple_white',
        margin=dict(l=40, r=40, t=50, b=50),
    )

    return fig

if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        webbrowser.open_new("http://127.0.0.1:8050/")
    app.run_server(debug=True, dev_tools_ui=False)