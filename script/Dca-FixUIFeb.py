import dash
import os, webbrowser, base64
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import curve_cum_function as ccf
from dash import dcc, html, dash_table, callback_context
from dash.dependencies import Input, Output, State, ALL
from datetime import date
import tempfile

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'DCA'
UPLOAD_DIRECTORY = os.path.join(os.path.dirname(__file__), '../Data')
excel_file = './Data/show_data.xlsx'
xls = pd.ExcelFile(excel_file)
sheet_names = xls.sheet_names

Objects = {}
for name in sheet_names:
    parents = name.split("-")
    main, sub, detail = parents[0], parents[1], parents[2]

    field_key = f"{main}ase Field"
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
                labelStyle={'display': 'flex', 'marginBottom': '19px', 'gap': '15px', 'alignItems': 'center', 'fontWeight': '400', 'fontSize': '18px', 'color': '#616161'},
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
                labelStyle={'display': 'flex', 'marginBottom': '19px', 'gap': '15px', 'alignItems': 'center', 'fontWeight': '400', 'fontSize': '16px', 'color': '#616161'},
                inputStyle={'transform': 'scale(1.5)', 'borderRadius': '6px'}
            )


            detail_elements = dcc.Checklist(
                options=[{'label': detail, 'value': detail} for detail in details],
                id={'type':'detail-checkbox', 'name': f'checkbox-{main}-{sub}-details'},
                value=['B-L-18'] if 'B-L-18' in details else [],
                inline=True,
                labelStyle={'display': 'flex', 'marginBottom': '19px', 'gap': '15px', 'alignItems': 'center', 'fontWeight': '400', 'fontSize': '16px', 'color': '#616161'},
                inputStyle={'transform': 'scale(1.5)', 'borderRadius': '6px'}
            )
            
            sub_elements.append(html.Div([sub_checkbox, html.Div(detail_elements, style={'marginLeft': '32px'})]))
        
        elements.append(html.Div([main_checkbox, html.Div(sub_elements, style={'marginLeft': '32px'})]))
    return elements

table_data = pd.DataFrame(columns=["Well Name", "Start Date", "End Date", "b", "Reserves", "Cut Off Date"])
selected_b_value = 0.5

app.layout = html.Div([
    html.Header([
        html.Nav([
            html.Nav([
                html.Div([
                    # html.Div([
                    #     html.Img(src="assets/logo.png", style={'width': '50px', 'height': '38.19px'}),
                    #     html.Div([
                    #         html.H1("WENNI", style={'fontWeight': '600', 'fontSize': "20px", 'color': '#006CB8', 'lineHeight': "25.2px"}),
                    #         html.P("Well Forecast and Monitoring", style={'fontWeight': '400', 'fontSize': "14px", 'color': '#9B9797', 'lineHeight': '17.64px'})
                    #     ], style={'flexDirection': 'column'})
                    # ], style={'display': 'flex', 'alignItems': 'center', 'gap': '13.11px', 'paddingTop': '27px'}),
                    html.Img(src="assets/PHM.png", style={'width': '174px'})
                ], style={'backgroundColor': 'white', 'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'width': '100%', 'paddingLeft': '37px', 'paddingRight': '37px', 'borderBottomLeftRadius': "20px", 'borderBottomRightRadius': '20px'})
            ], style={'backgroundColor': '#C3304A', 'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'width': '100%', 'paddingBottom': '20px', 'borderBottomLeftRadius': "20px", 'borderBottomRightRadius': '20px'}),
            html.Nav([
                html.Div([
                    html.P("Historical", style={"fontWeight": "400", "fontSize": '16px', "color": 'white'}),
                    html.P("DCA", style={"fontWeight": "800", 'fontSize': '16px', "color": 'white'}),
                    html.P('ML', style={"fontWeight": "400", "fontSize": '16px', "color": 'white'})
                ], style={'display': 'flex', 'alignItems': 'center', 'gap': '71px', 'paddingLeft': '35px'}),
                html.Div([
                    # html.H1('Admin 1', style={"fontWeight": "700", 'fontSize': '16px', "color": 'white'}),
                    html.P('User', style={"fontWeight": "700", "fontSize": '16px', "color": 'white'})
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
                    html.Div(className='feature-container', style={'border': '1px solid #3F849B', 'padding': '0', 'borderRadius': '16px', 'width': '180px', 'height': '123px'}, children=[
                        html.H1('Plot Type', className='Feature-title', style={'color': 'white', 'fontWeight': '700', 'fontSize': '18px', 'padding': '8px 17px', 'backgroundColor': '#3F849B', 'borderRadius': '10px'}),
                        html.Div(style={'padding': '10px 25px'}, children=[
                            dcc.Checklist(
                                id='plot-type',
                                options=[
                                    {'label': 'Scatter', 'value': 'scatter'},
                                    {'label': 'Line', 'value': 'line'},
                                ],
                                value=['scatter', 'line'], 
                                labelStyle={'display': 'flex', 'marginBottom': '6px', 'gap': '15px', 'alignItems': 'center', 'fontWeight': '400', 'fontSize': '16px', 'color': '#616161'},
                                inputStyle={'transform': 'scale(1.5)', 'borderRadius': '6px'}
                            ),
                        ])
                    ]),
                    html.Div(className='feature-container', style={'border': '1px solid #3F849B', 'padding': '0', 'borderRadius': '16px', 'width': '180px', 'height': '93px'}, children=[
                        html.H1('Legend', className='Feature-title', style={'color': 'white', 'fontWeight': '700', 'fontSize': '18px', 'padding': '8px 17px', 'backgroundColor': '#3F849B', 'borderRadius': '10px'}),
                        html.Div(style={'padding': '10px 25px'}, children=[
                            dcc.Checklist(
                                id='legend-status',
                                options=[
                                    {'label': 'Enable', 'value': 'on'},
                                ],
                                value=['on'], 
                                labelStyle={'display': 'flex', 'marginBottom': '6px', 'gap': '15px', 'alignItems': 'center', 'fontWeight': '400', 'fontSize': '16px', 'color': '#616161'},
                                inputStyle={'transform': 'scale(1.5)', 'borderRadius': '6px'}
                            ),
                        ])
                    ]),
                    html.Div(className='feature-container', style={'border': '1px solid #3F849B', 'padding': '0', 'borderRadius': '16px', 'width': '180px', 'height': '153px'}, children=[
                        html.H1('Models', className='Feature-title', style={'color': 'white', 'fontWeight': '700', 'fontSize': '18px', 'padding': '8px 17px', 'backgroundColor': '#3F849B', 'borderRadius': '10px'}),
                        html.Div(style={'padding': '10px 25px'}, children=[
                            dcc.RadioItems(
                                id="selected-b-options",
                                options=[
                                    {'label': 'Exponential', 'value': 0},
                                    {'label': 'Hyperbolic', 'value': 0.5},
                                    {'label': 'Harmonic', 'value': 1},
                                ],
                                value=selected_b_value, 
                                labelStyle={'display': 'flex', 'marginBottom': '6px', 'gap': '15px', 'alignItems': 'center', 'fontWeight': '400', 'fontSize': '16px', 'color': '#616161'},
                                inputStyle={'transform': 'scale(1.5)', 'borderRadius': '6px'}
                            ),
                        ])
                    ]),
                    html.Div(className='feature-container', style={'border': '1px solid #3F849B', 'padding': '0', 'borderRadius': '16px', 'width': '180px', 'minHeight': '123px'}, children=[
                        html.H1('Settings', className='Feature-title', style={'color': 'white', 'fontWeight': '700', 'fontSize': '18px', 'padding': '8px 17px', 'backgroundColor': '#3F849B', 'borderRadius': '10px'}),
                        html.Div(style={'padding': '10px', 'display': 'flex', 'flexDirection': 'column', 'gap': '10px'}, children=[
                            html.Div(style={'width': '100%'}, children=[
                                html.Label('Start Forecast Date:', style={'fontWeight': '400', 'fontSize': '16px', 'color': '#616161'}),
                                dcc.DatePickerSingle(
                                    id='foil-date-picker',
                                    date=date(2024, 4, 1),
                                    display_format='DD/MM/YYYY', 
                                    # style={ 'border': '1px solid #616161', 'borderRadius': '6px', 'width': '145px', 'height': '30px', 'color': 'black', 'overflow': 'hidden', 'display': 'flex', 'alignItems': 'center' },
                                )
                            ]),
                            html.Div(style={'fontWeight': '400', 'fontSize': '16px', 'color': '#616161'}, children=[
                                html.Label('Forecast Months:', style={'fontWeight': '400', 'fontSize': '16px', 'color': '#616161'}),
                                dcc.Input(
                                    id='months-end-date', 
                                    type='number', 
                                    value=120, 
                                    min=1, 
                                    style={'border': '1px solid #616161', 'borderRadius': '6px', 'width': '145px', 'height': '30px', 'color': 'black', 'overflow': 'hidden', 'display': 'flex', 'alignItems': 'center'}
                                )
                            ]),
                            # html.Div(style={'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'}, children=[
                            #     html.Label('Rate Intervention (bopd):', style={'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'}),
                            #     dcc.Input(
                            #         id='oil-rate-intervention', 
                            #         type='number', 
                            #         value=0, 
                            #         step=50, 
                            #         style={'border': '1px solid #616161', 'borderRadius': '6px', 'width': '134px', 'height': '30px', 'color': 'black', 'overflow': 'hidden', 'display': 'flex', 'alignItems': 'center'}
                            #     )
                            # ]),
                            html.Div(style={'fontWeight': '400', 'fontSize': '16px', 'color': '#616161'}, children=[
                                html.Label('Rate Limit Value (bopd):', style={'fontWeight': '400', 'fontSize': '16px', 'color': '#616161'}),
                                dcc.Input(
                                    id='limit-value', 
                                    type='number', 
                                    value=0.0, 
                                    step=0.1, 
                                    style={'border': '1px solid #616161', 'borderRadius': '6px', 'width': '150px', 'height': '30px', 'color': 'black', 'overflow': 'hidden', 'display': 'flex', 'alignItems': 'center'}
                                )
                            ]),
                        ])
                    ]), 
                ]),
                html.Div(children=[
                    dcc.Tabs(
                        id='tab-container',
                        value='B-L-18',
                        children=[],
                        content_style={'textAlign': 'center'}
                    ),
                    html.Div(
                        style={
                            'border': '1px solid grey', 
                            'padding': '21px', 
                            'borderBottomLeftRadius': '30px', 
                            'borderBottomRightRadius': '30px', 
                            'borderTopRightRadius': '30px'
                        },
                        children=[
                            dbc.Row([
                                dbc.Col(dcc.Loading(
                                    id="loading-oil-plot",
                                    type="dot",
                                    children=[dcc.Graph(id='oil-plot')],
                                    style={'position': 'relative'}, overlay_style={"visibility":"visible", "opacity": .5, "backgroundColor": "white"} 
                                ),),
                            ]),
                            dbc.Row([
                                dbc.Col(html.Div(id='reserves-output'), width=12),
                            ], style={'marginBottom': '10px'}),
                            dbc.Row([
                                dbc.Col([
                                    html.Label('Select Date Range:'),
                                    dcc.RangeSlider(
                                        id='date-slider',
                                        min=0,
                                        max=15000,
                                        step=1,
                                        value=[0, 15000],
                                        marks={},
                                        tooltip={"placement": "bottom", "always_visible": True}
                                    )
                                ], width=12, style={'marginBottom': '30px'}), 
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Label('Adjust b Value:'),
                                    dcc.Slider(
                                        id='b-value-slider',
                                        min=0.0,
                                        max=1.0,
                                        step=0.001,
                                        value=0.5,
                                        marks={0: '0.000', 0.5: '0.500', 1: '1.000'},
                                        tooltip={"placement": "bottom", "always_visible": True}
                                    )
                                ], width=6, style={'paddingRight': '15px'}),
                                dbc.Col([
                                    html.Label('Adjust Rate Intervention (bopd):'),
                                    dcc.Slider(
                                        id='oil-rate-intervention',
                                        min=0,
                                        max=1000,
                                        step=1,
                                        value=0,
                                        marks={0: '0', 250: '250', 500: '500', 750: '750', 1000: '1000'},
                                        tooltip={"placement": "bottom", "always_visible": True}
                                    )
                                ], width=6, style={'paddingRight': '15px'}),
                            ], style={'marginBottom': '30px'}),
                            dbc.Row([
                                dbc.Col([
                                    html.Label('Adjust Qi Value Changes:'),
                                    dcc.Slider(
                                        id='qi-value-slider',
                                        min=-500,
                                        max=500,
                                        step=1,
                                        value=0,
                                        marks={-500: '-500', 0: '0', 500: '500'},
                                        tooltip={"placement": "bottom", "always_visible": True}
                                    )
                                ], width=6, style={'paddingRight': '15px'}),
                                dbc.Col([
                                    html.Label('Adjust Di Value Changes:'),
                                    dcc.Slider(
                                        id='di-value-slider',
                                        min=100,
                                        max=10000,
                                        step=1,
                                        value=100,
                                        marks={100: '100', 10000: '10000'},
                                        tooltip={"placement": "bottom", "always_visible": True}
                                    )
                                ], width=6, style={'marginTop': '15px'}), 
                            ], ),
                            dbc.Row([
                                dbc.Col([
                                    html.Div(id='alert', children=[])
                                ], width=12),
                            ]),
                            dash_table.DataTable(
                                id="data-table",
                                columns=[{"name": col, "id": col} for col in [
                                    "Well Name", "Start Date", "End Date", "Start Forecast Date", "Cum Date", 
                                    "Cum Prod", "Reserves (bbl)", "b", "Di", "qi", "ti", "te", 
                                    "Final Rate", "EUR", "Rate Intervention", "Cut Off Date"
                                ]],
                                data=table_data.to_dict("records"),
                                editable=False,
                                row_deletable=True,
                                page_size=10,
                                style_table={'marginTop': '30px', 'overflowX': 'auto', 'maxHeight': '500px'},
                                style_header={'backgroundColor': '#3f849b', 'color': 'white', 'fontWeight': 'bold', 'textAlign': 'center'},
                                style_data={'border': '1px solid #ddd', 'textAlign': 'center'},
                                style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#f2f2f2'}],
                            ), 
                            html.Div([
                                html.Button("Download data table", id="download-button", n_clicks=0)
                            ], style={"display": "flex", "justifyContent": "center", "marginTop": "10px"}),
                            dcc.Download(id="download-csv")
                        ]
                    ),
                ]),
                html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '10px'}, children=[
                    html.Div(className='feature-container', style={'border': '1px solid #3F849B', 'padding': '0', 'borderRadius': '16px', 'width': '200px', 'minHeight': '40px'}, children=[
                        html.H1('Objects', className='Feature-title', style={'color': 'white', 'fontWeight': '700', 'fontSize': '18px', 'padding': '8px 17px', 'backgroundColor': '#3F849B', 'borderRadius': '10px'}),
                        html.Div(style={'padding': '10px', 'display': 'flex', 'flexDirection': 'column', 'gap': '10px'}, children=[
                            html.Div(style={'fontWeight': '400', 'fontSize': '18px', 'color': '#616161', 'display': 'none'}, children=[
                                html.Label('Select Well:', style={'fontWeight': '400', 'fontSize': '16px', 'color': '#616161'}),
                                dcc.Dropdown(
                                    id='well-name', 
                                    options=[{'label': name, 'value': name} for name in sheet_names], 
                                    value='B-L-18',
                                    clearable=False,
                                )
                            ]),
                            html.Div(children=create_nested_checkboxes(Objects))
                        ])
                    ]), 
                ]),
                dcc.Location(id="page-reloader", refresh=True)
            ])
        ])
    ]),
])

def save_file(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    file_path = os.path.join(excel_file)
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
    defaultStyle = {'display': 'flex', 'marginBottom': '19px', 'gap': '15px', 'align-items': 'center', 'fontWeight': '400', 'fontSize': '16px', 'color': '#616161'}
    if main_checked[0] != [] :
        return [defaultStyle for _ in sub_label_style], value
    else:
        return [{'display': 'none'} for _ in sub_label_style], [[] for _ in value]

@app.callback(
    Output({'type': 'detail-checkbox', 'name': ALL}, 'labelStyle'),
    Input({'type': 'sub-checkbox', 'name': ALL}, 'value')
)
def update_detail_checkboxes(sub_checked):
    default_style = {'display': 'flex', 'marginBottom': '19px', 'gap': '15px', 'align-items': 'center', 'fontWeight': '400', 'fontSize': '16px', 'color': '#616161'}
    style = []
    for items in sub_checked:
        if items != []:
            style.append(default_style)
        else: 
            style.append({'display': 'none'})
    return style

@app.callback(
    Output('well-name', 'value'),
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
    Output('date-slider', 'min'),
    Output('date-slider', 'max'),
    Output('date-slider', 'marks'),
    Output('date-slider', 'value'),
    Input('well-name', 'value')
)
def update_slider(well_name):
    df = pd.read_excel(excel_file, sheet_name=well_name)
    df['DATE_STAMP'] = pd.to_datetime(df['DATE_STAMP'], format='%d/%m/%Y', dayfirst=True)
    
    slider_min = 0
    slider_max = len(df) - 1
    slider_value = [slider_min, slider_max]
    marks = {i: {'label': '', 'style': {'display': 'none'}} for i, date in enumerate(df['DATE_STAMP'])}

    return slider_min, slider_max, marks, slider_value

@app.callback(
    Output('oil-plot', 'figure'),
    Output('alert', 'children'),
    Output('reserves-output', 'children'),
    Output('data-table', 'data'),
    Output('selected-b-options', 'value'),
    Output('b-value-slider', 'value'),
    Output('qi-value-slider', 'value'),
    Output('di-value-slider', 'value'),
    Input('well-name', 'value'),
    Input('foil-date-picker', 'date'),
    Input('months-end-date', 'value'),
    Input('date-slider', 'value'),
    Input('oil-rate-intervention', 'value'),
    Input('b-value-slider', 'value'),
    Input('qi-value-slider', 'value'),
    Input('di-value-slider', 'value'),
    Input('limit-value', 'value'),
    Input('data-table', 'data'),
    Input('legend-status', 'value'),
    Input('plot-type', 'value'),
    Input('selected-b-options', 'value'),
    State('b-value-slider', 'value'),
    State('selected-b-options', 'value'),
    
)
def update_plots(well_name, foil_date, months_end_date, slider_value, rate_intervention, b_value, qi_change, di_change, limit_value, rows, legend_status, plot_type, selected_b_options, prev_b_value, prev_selected_b_options):
    if rows is None:
        rows = [] 

    show_legend = 'on' in legend_status
    scatter = 'scatter' in plot_type
    line = 'line' in plot_type;

    foil_date = pd.to_datetime(foil_date)
    
    df = pd.read_excel(excel_file, sheet_name=well_name)
    df['DATE_STAMP'] = pd.to_datetime(df['DATE_STAMP'], format='%d/%m/%Y', dayfirst=True)
    
    start_date = df['DATE_STAMP'].iloc[slider_value[0]]
    end_date = df['DATE_STAMP'].iloc[slider_value[1]]
    end_dates = df['DATE_STAMP'].iloc[slider_value[1]]

    mask = (df['DATE_STAMP'] >= start_date) & (df['DATE_STAMP'] <= end_date)
    dfx = df.loc[mask].copy()

    dfx['OIL_CUMULATIVE_PRODUCTION'] = 0.0
    # Calculate cumulative production on a monthly basis into daily basis
    # for i in range(1, len(dfx)):
    #     days_diff = (dfx.loc[dfx.index[i], 'DATE_STAMP'] - dfx.loc[dfx.index[i - 1], 'DATE_STAMP']).days
    #     oil_rate = dfx.loc[dfx.index[i - 1], 'CORR_OIL_RATE_STBD']
    #     dfx.loc[dfx.index[i], 'OIL_CUMULATIVE_PRODUCTION'] = (
    #         dfx.loc[dfx.index[i - 1], 'OIL_CUMULATIVE_PRODUCTION'] + days_diff * oil_rate
    #     )

    # Calculate cumulative production on a daily basis
    for i in range(1, len(dfx)):
        oil_rate = dfx.loc[dfx.index[i - 1], 'CORR_OIL_RATE_STBD']
        dfx.loc[dfx.index[i], 'OIL_CUMULATIVE_PRODUCTION'] = (
            dfx.loc[dfx.index[i - 1], 'OIL_CUMULATIVE_PRODUCTION'] + oil_rate
        )
    
    best_b_oil, oil_exp_di, oil_har_di, oil_hyper_di, oil_exp_model, oil_har_model, oil_hyper_model, df_oil = ccf.process_data(excel_file, well_name, start_date, end_date, qi_change, di_change, 'CORR_OIL_RATE_STBD', 'oil')
    
    last_rate = dfx[dfx['CORR_OIL_RATE_STBD'] != 0]['CORR_OIL_RATE_STBD'].iloc[-1]
    current_rate = last_rate + rate_intervention
    qi = last_rate

    # foil_date = foil_date.replace(day=1) # Enable this if the data is monthly
    end_date = foil_date + pd.DateOffset(months=months_end_date)
    date_range = pd.date_range(start=foil_date, end=end_date, freq='MS')
    marker_y = dfx[dfx['DATE_STAMP'] == start_date]['CORR_OIL_RATE_STBD'].values[0]

    forecast_df = pd.DataFrame({'DATE': date_range, 'TIME': range(len(date_range))})
    forecast_df['Forecast_Oil_Exponential'] = ccf.exponential_rate(current_rate, oil_exp_di, forecast_df['TIME'])
    
    # Model category based on b value
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    if triggered_id == 'selected-b-options':
        selectedData = selected_b_options
        b_value = selected_b_options
    elif triggered_id == 'b-value-slider':
        if b_value == 0 or b_value == 1: selectedData = b_value
        else: selectedData = 0.5
    else:
        selectedData = selected_b_options
    
    forecast_df['Forecast_Oil_Hyperbolic'] = ccf.hyperbolic_rate(current_rate, oil_hyper_di, b_value, forecast_df['TIME'])
    forecast_df['Oil_Cumulative_Hyper'] = ccf.cum_hyperbolic(forecast_df['Forecast_Oil_Hyperbolic'].iloc[0], oil_hyper_di, forecast_df['Forecast_Oil_Hyperbolic'], b_value)
    forecast_df['Oil_Cumulative_Hyper'] += dfx['OIL_CUMULATIVE_PRODUCTION'].iloc[-1]
    forecast_df['Oil_Cumulative_HyperTotal'] = forecast_df['Oil_Cumulative_Hyper']

    time_EUR_hyper = forecast_df[forecast_df['Forecast_Oil_Hyperbolic'] >= limit_value].iloc[-1]
    EUR_hyper = time_EUR_hyper['Oil_Cumulative_HyperTotal']
    reserves_hyper = EUR_hyper - dfx['OIL_CUMULATIVE_PRODUCTION'].iloc[-1]
    forecast_df['Forecast_Oil_Harmonic'] = ccf.harmonic_rate(current_rate, oil_har_di, forecast_df['TIME'])

    forecast_df['Oil_Cumulative_Exp'] = ccf.cum_exponential(forecast_df['Forecast_Oil_Exponential'].iloc[0], oil_exp_di, forecast_df['Forecast_Oil_Exponential'])
    forecast_df['Oil_Cumulative_Exp'] += dfx['OIL_CUMULATIVE_PRODUCTION'].iloc[-1]
    forecast_df['Oil_Cumulative_Har'] = ccf.cum_harmonic(forecast_df['Forecast_Oil_Harmonic'].iloc[0], oil_har_di, forecast_df['Forecast_Oil_Harmonic'])
    forecast_df['Oil_Cumulative_Har'] += dfx['OIL_CUMULATIVE_PRODUCTION'].iloc[-1]

    forecast_df['Oil_Cumulative_ExpTotal'] = forecast_df['Oil_Cumulative_Exp']
    forecast_df['Oil_Cumulative_EarTotal'] = forecast_df['Oil_Cumulative_Har']

    time_EUR_exp = forecast_df[forecast_df['Forecast_Oil_Exponential'] >= limit_value].iloc[-1]
    time_EUR_har = forecast_df[forecast_df['Forecast_Oil_Harmonic'] >= limit_value].iloc[-1]
    EUR_exp = time_EUR_exp['Oil_Cumulative_ExpTotal']
    EUR_har = time_EUR_har['Oil_Cumulative_EarTotal']
    reserves_exp = EUR_exp - dfx['OIL_CUMULATIVE_PRODUCTION'].iloc[-1]
    reserves_har = EUR_har - dfx['OIL_CUMULATIVE_PRODUCTION'].iloc[-1]

    df_monthly = df[df['DATE_STAMP'].dt.is_month_start].copy()
    
    df_monthly['INDEX'] = range(0, len(df_monthly))
    last_index = df_monthly['INDEX'].iloc[-1]
    
# Plot with the filtered data

    if scatter:
        oil_fig = px.scatter(
            df_monthly,
            x='DATE_STAMP',
            y='CORR_OIL_RATE_STBD',
            title=f'Oil Rate Comparison of Decline Models Well {well_name}',
            labels={'DATE_STAMP': 'Date', 'CORR_OIL_RATE_STBD': 'Oil Rate (bopd)'},
            color_discrete_sequence=['brown'],
            size_max=5,
            hover_data={'DATE_STAMP': True, 'CORR_OIL_RATE_STBD': True, 'INDEX': True}
        )
    else:
        oil_fig = px.line(title=f'Oil Rate Comparison of Decline Models Well {well_name}')

    oil_fig.update_layout(
        height=600,
        title={
            "text": f"<b>Oil Rate Comparison of Decline Models Well {well_name}</b>",
            "x": 0.5, "xanchor": "center"},
        showlegend=show_legend)
    
    if line:
        oil_fig.add_scatter(x=df_oil['DATE_STAMP'], y=np.array(oil_exp_model), mode='lines', name='Exponential Model', line=dict(color='blue'))
        oil_fig.add_scatter(x=df_oil['DATE_STAMP'], y=np.array(oil_hyper_model), mode='lines', name=f'Hyperbolic Model (best b = {best_b_oil})', line=dict(color='green'))
        oil_fig.add_scatter(x=df_oil['DATE_STAMP'], y=np.array(oil_har_model), mode='lines', name='Harmonic Model', line=dict(color='orange'))

    if b_value == 0.000:
        if line:
            oil_fig.add_scatter(x=forecast_df['DATE'], y=forecast_df['Forecast_Oil_Exponential'].values, mode='lines', name=f'Forecast Line (di={oil_exp_di:.2f}, qi={qi:.2f})', line=dict(color='LightBlue'))
        crossed = forecast_df[forecast_df['Forecast_Oil_Exponential'] <= limit_value]
        reserves_output = "Forecasted Reserves: ", html.Span(f"{reserves_exp:,.2f} bbl", style={'fontWeight': 'bold'})
        val_reserves = reserves_exp
        val_di = oil_exp_di
        val_final_rate = forecast_df['Forecast_Oil_Exponential'].iloc[-1]
        val_eur = EUR_exp
        val_cum_prod = EUR_exp - reserves_exp
    elif b_value == 1.000:
        if line:
            oil_fig.add_scatter(x=forecast_df['DATE'], y=forecast_df['Forecast_Oil_Harmonic'].values, mode='lines', name=f'Forecast Line (di={oil_har_di:.2f}, qi={qi:.2f})', line=dict(color='LightSalmon'))
        crossed = forecast_df[forecast_df['Forecast_Oil_Harmonic'] <= limit_value]
        reserves_output = "Forecasted Reserves: ", html.Span(f"{reserves_har:,.2f} bbl", style={'fontWeight': 'bold'})
        val_reserves = reserves_har
        val_di = oil_har_di
        val_final_rate = forecast_df['Forecast_Oil_Harmonic'].iloc[-1]
        val_eur = EUR_har
        val_cum_prod = EUR_har - reserves_har
    else:
        if line:
            oil_fig.add_scatter(x=forecast_df['DATE'], y=forecast_df['Forecast_Oil_Hyperbolic'].values, mode='lines', name=f'Forecast Line (di={oil_hyper_di:.2f}, qi={qi:.2f})', line=dict(color='LightGreen'))
        crossed = forecast_df[forecast_df['Forecast_Oil_Hyperbolic'] <= limit_value]
        reserves_output = "Forecasted Reserves: ", html.Span(f"{reserves_hyper:,.2f} bbl", style={'fontWeight': 'bold'})
        val_reserves = reserves_hyper
        val_di = oil_hyper_di
        val_final_rate = forecast_df['Forecast_Oil_Hyperbolic'].iloc[-1]
        val_eur = EUR_hyper
        val_cum_prod = EUR_hyper - reserves_hyper

    if line:
        oil_fig.add_scatter(x=[foil_date, end_date], y=[limit_value, limit_value], mode='lines', name=f'Rate Limit ({limit_value} bopd)', line=dict(color='red', dash='dash'))

    forecast_df = forecast_df.copy()
    forecast_df['INDEX'] = '-'
    df_combined = pd.concat([df_monthly, forecast_df], ignore_index=True)

    alert_message = []
    if not crossed.empty:
        crossing_date = crossed['DATE'].iloc[0]
        alert_message.append(
            dbc.Alert(
                [
                    "Alert: Forecast crosses limit on ",
                    html.Span(crossing_date.strftime("%d-%m-%Y"), style={'fontWeight': 'bold'}),
                ],
                color='danger', dismissable=True, duration=7000,
            )
        )
    
    if scatter:
        oil_fig.add_scatter(x=[start_date], y=[marker_y], mode='markers', name='Initial Date', marker=dict(color='black', size=6))
        oil_fig.add_vline(x=start_date, line=dict(color='black', dash='dash', width=2), name='Initial Date')

    oil_fig.update_layout(
        xaxis=dict(title='Date', tickformat='%d-%m-%Y'),
        yaxis=dict(title='Oil Rate (bopd)'),
        legend_title="Legend",
        height=700
    )

    # Hover Values
    oil_fig.update_traces(
        customdata=df_combined[['INDEX']].values,
        hovertemplate=(
            "Date: %{x}<br>" +
            "Oil Rate: %{y:,.2f} bopd<br>" +
            "Index: %{customdata[0]}<br>" +
            "<extra></extra>"
        )
    )

    new_row = {
        "Well Name": well_name,
        "Start Date": start_date.strftime('%d-%m-%Y'),
        "End Date": end_dates.strftime('%d-%m-%Y'),
        "Start Forecast Date": foil_date.strftime('%d-%m-%Y'),
        "Cum Date": end_dates.strftime('%d-%m-%Y'),
        "Cum Prod": f"{val_cum_prod:,.3f} bbl",
        "Reserves (bbl)": f"{val_reserves:,.5f}",
        "b": f"{b_value:.3f}",
        "Di": f"{val_di:.7f} M.n.",
        "qi": f"{qi:.3f} bopd",
        "ti": foil_date.strftime('%d-%m-%Y'),
        "te": end_date.strftime('%d-%m-%Y'),
        "Final Rate": f"{val_final_rate:,.4f} bopd",
        "EUR": f"{val_eur:,.2f}",
        "Rate Intervention": rate_intervention,
        "Cut Off Date": crossing_date.strftime('%d-%m-%Y') if not crossed.empty else "N/A"
    }


    existing_row = next((row for row in rows if row['Well Name'] == new_row['Well Name']), None)
    if existing_row:
        rows[rows.index(existing_row)] = new_row
    else:
        rows.append(new_row)
    rows = sorted(rows, key=lambda x: float(x['Reserves (bbl)'].replace(',', '')), reverse=True)

    return oil_fig, alert_message, reserves_output, rows, selectedData, b_value, qi_change, di_change

@app.callback(
    Output("download-csv", "data"),
    Input("download-button", "n_clicks"),
    State("data-table", "data"),
    prevent_initial_call=True
)
def download_table(n_clicks, rows):
    if rows:
        df = pd.DataFrame(rows)
        csv_string = df.to_csv(index=False, encoding="utf-8")
        return dict(content=csv_string, filename="data_table.csv")

if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        webbrowser.open_new("http://127.0.0.1:8050/")
    app.run_server(debug=True, dev_tools_ui=True)
