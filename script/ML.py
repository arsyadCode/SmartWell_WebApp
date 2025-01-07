import os, webbrowser, base64, sys
import pandas as pd
import numpy as np
import ml_process as mlp
from PIL import Image

import dash
from dash import dcc, html, dash_table, callback_context
from dash.exceptions import PreventUpdate
from dash.dependencies import State, ALL, Output, Input
import dash_bootstrap_components as dbc

excel_file = './Data/data_ml.csv'
df = pd.read_csv(excel_file)
df['DATE'] = pd.to_datetime(df['DATE'])

completion_features = ['VSH', 'PHI', 'SW', 'NET_THICK', 'N_OPEN_RESERVOIR']
event_features = ['EVENT', 'LAST_EVENT', 'EVENT_PLATFORM', 'LAST_EVENT_PLATFORM', 'NORM_PROD_DAYS']
main_features = ['WHP', 'WHT']
additional_features = ['CHOKE_FLAG']
ratios = ['LIQUID', 'WATERCUT', 'GLR', 'GOR']
targets = ['OIL', 'WATER', 'GAS']
additional = ['Universal']

directory_path = 'export'

def generate_directory_structure(path):
    folder_content = []
    
    for root, dirs, files in os.walk(path):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            folder_content.append(
                html.Details([
                    html.Summary(dir_name),
                    html.Div(generate_directory_structure(dir_path))
                ])
            )

        for file_name in files:
            file_path = os.path.join(root, file_name)
            file_ext = os.path.splitext(file_name)[1].lower()
            if file_ext in ['.png', '.csv', '.xlsx']:
                folder_content.append(html.Li(
                    html.Button(
                        file_name, id={'type': 'file-btn', 'index': file_path}, n_clicks=0
                    )
                ))
        break

    return folder_content

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
                value=[sub],
                inline=True,
                labelStyle={'display': 'flex', 'marginBottom': '19px', 'gap': '15px', 'alignItems': 'center', 'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'},
                inputStyle={'transform': 'scale(1.5)', 'borderRadius': '6px'}
            )


            detail_elements = dcc.Checklist(
                options=[{'label': detail, 'value': detail} for detail in details],
                id={'type':'detail-checkbox', 'name': f'checkbox-{main}-{sub}-details'},
                value=details,
                inline=True,
                labelStyle={'display': 'flex', 'marginBottom': '19px', 'gap': '15px', 'alignItems': 'center', 'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'},
                inputStyle={'transform': 'scale(1.5)', 'borderRadius': '6px'}
            )
            
            sub_elements.append(html.Div([sub_checkbox, html.Div(detail_elements, style={'marginLeft': '32px'})]))
        
        elements.append(html.Div([main_checkbox, html.Div(sub_elements, style={'marginLeft': '32px'})]))
    return elements

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
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
                        html.P("Historical", style={"fontWeight": "400", "fontSize": '16px', "color": 'white'}),
                        html.P("DCA", style={"fontWeight": "400", 'fontSize': '16px', "color": 'white'}),
                        html.P('Forecast', style={"fontWeight": "800", "fontSize": '16px', "color": 'white'})
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
                        html.Div(className='feature-container', style={'border': '1px solid #3F849B', 'padding': '0', 'borderRadius': '16px', 'width': '240px', 'height': '220px'}, children=[
                            html.H1('Completion Features', className='Feature-title', style={'color': 'white', 'fontWeight': '700', 'fontSize': '16px', 'padding': '8px 17px', 'backgroundColor': '#3F849B', 'borderRadius': '10px'}),
                            html.Div(style={'padding': '10px 25px'}, children=[
                                dcc.Checklist(
                                    id='completion-features-dropdown',
                                    options=[{'label': feature, 'value': feature} for feature in completion_features],
                                    value=completion_features, 
                                    labelStyle={'display': 'flex', 'marginBottom': '9.5px', 'gap': '15px', 'alignItems': 'center', 'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'},
                                    inputStyle={'transform': 'scale(1.5)', 'borderRadius': '6px'}
                                ),
                            ])
                        ]),
                        html.Div(className='feature-container', style={'border': '1px solid #3F849B', 'padding': '0', 'borderRadius': '16px', 'width': '240px', 'height': '220px'}, children=[
                            html.H1('Event Features', className='Feature-title', style={'color': 'white', 'fontWeight': '700', 'fontSize': '16px', 'padding': '8px 17px', 'backgroundColor': '#3F849B', 'borderRadius': '10px'}),
                            html.Div(style={'padding': '10px 25px'}, children=[
                                dcc.Checklist(
                                    id='event-features-dropdown',
                                    options=[{'label': feature, 'value': feature} for feature in event_features],
                                    value=event_features,  
                                    labelStyle={'display': 'flex', 'marginBottom': '9.5px', 'gap': '15px', 'alignItems': 'center', 'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'},
                                    inputStyle={'transform': 'scale(1.5)', 'borderRadius': '6px'}
                                ),
                            ])
                        ]),
                        html.Div(className='feature-container', style={'border': '1px solid #3F849B', 'padding': '0', 'borderRadius': '16px', 'width': '240px', 'height': '130px'}, children=[
                            html.H1('Main Features', className='Feature-title', style={'color': 'white', 'fontWeight': '700', 'fontSize': '16px', 'padding': '8px 17px', 'backgroundColor': '#3F849B', 'borderRadius': '10px'}),
                            html.Div(style={'padding': '10px 25px'}, children=[
                                dcc.Checklist(
                                    id='main-features-dropdown',
                                    options=[{'label': feature, 'value': feature} for feature in main_features],
                                    value=main_features,  
                                    labelStyle={'display': 'flex', 'marginBottom': '9.5px', 'gap': '15px', 'alignItems': 'center', 'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'},
                                    inputStyle={'transform': 'scale(1.5)', 'borderRadius': '6px'}
                                ),
                            ])
                        ]),
                        html.Div(className='feature-container', style={'border': '1px solid #3F849B', 'padding': '0', 'borderRadius': '16px', 'width': '240px', 'minHeight': '93px'}, children=[
                            html.H1('Additional Features', className='Feature-title', style={'color': 'white', 'fontWeight': '700', 'fontSize': '16px', 'padding': '8px 17px', 'backgroundColor': '#3F849B', 'borderRadius': '10px'}),
                            html.Div(style={'padding': '10px 25px'}, children=[
                                dcc.Checklist(
                                    id='additional-features-dropdown',
                                    options=[{'label': feature, 'value': feature} for feature in additional_features],
                                    value=additional_features, 
                                    labelStyle={'display': 'flex', 'marginBottom': '9.5px', 'gap': '15px', 'alignItems': 'center', 'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'},
                                    inputStyle={'transform': 'scale(1.5)', 'borderRadius': '6px'}
                                ),
                            ])
                        ]), 
                        html.Div(className='feature-container', style={'border': '1px solid #3F849B', 'padding': '0', 'borderRadius': '16px', 'width': '240px', 'height': '193px'}, children=[
                            html.H1('Date Range', className='Feature-title', style={'color': 'white', 'fontWeight': '700', 'fontSize': '16px', 'padding': '8px 17px', 'backgroundColor': '#3F849B', 'borderRadius': '10px'}),
                            html.Div(style={'padding': '10px', 'display': 'flex', 'flexDirection': 'column', 'gap': '10px'}, children=[
                                html.Div(style={'width': '100%'}, children=[
                                    html.Label('Start Forecast Date:', style={'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'}),
                                    dcc.DatePickerSingle(
                                        id='date-picker-range-start',
                                        date=df['DATE'].min(),
                                        display_format='DD/MM/YYYY', 
                                        style={ 'border': '1px solid #616161', 'borderRadius': '6px', 'width': '134px', 'height': '30px', 'color': 'black', 'overflow': 'hidden', 'display': 'flex', 'alignItems': 'center' },
                                    )
                                ]),
                                html.Div(style={'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'}, children=[
                                    html.Label('End Forecast Date:', style={'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'}),
                                    dcc.DatePickerSingle(
                                        id='date-picker-range-end',
                                        date=df['DATE'].max(), 
                                        display_format='DD/MM/YYYY',
                                        style={'border': '1px solid #616161', 'borderRadius': '6px', 'width': '134px', 'height': '30px', 'color': 'black', 'overflow': 'hidden', 'display': 'flex', 'alignItems': 'center'}
                                    )
                                ]),
                            ])
                        ]),
                    ]),
                    html.Div(style={'width': '60vw'}, children=[
                        html.Div(style={'border': '1px solid #909090',  'backgroundColor': '#3F849B', 'width': '141px',  'height': '39px',  'borderTopLeftRadius': '10px',  'borderTopRightRadius': '10px', 'display': 'flex', 'alignItems': 'center', 'justifyItems': 'center', 'paddingLeft': '10px', 'paddingTop': '10px'},
                            children=[
                                html.H1("Preview", style={'color': 'white', 'fontSize': '14px', 'fontWeight': '700', 'textAlign': 'center'})
                            ]
                        ),
                        html.Div(style={'border': '1px solid grey', 'padding': '21px', 'borderBottomLeftRadius': '30px', 'borderBottomRightRadius': '30px', 'borderTopRightRadius': '30px'}, children=[
                            html.Div(
                                style={
                                    'border': '1px solid #ddd', 
                                    'padding': '20px', 
                                    'border-radius': '8px',
                                    'margin-bottom': '30px', 
                                    'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)'
                                },
                                children=[
                                    html.Div(
                                        style={'display': 'flex', 'justify-content': 'space-between', 'margin-bottom': '20px'},
                                        children=[
                                            html.Div(
                                                style={'width': '48%'},
                                                children=[
                                                    html.Label('Sort By Column:', style={'font-weight': 'bold'}),
                                                    dcc.Dropdown(
                                                        id='sort-column-dropdown',
                                                        options=[{'label': col, 'value': col} for col in df.columns],
                                                        value='DATE',
                                                        placeholder='Select a column to sort by...'
                                                    )
                                                ]
                                            ),
                                            html.Div(
                                                style={'width': '48%'},
                                                children=[
                                                    html.Label('Sort Order:', style={'font-weight': 'bold'}),
                                                    dcc.RadioItems(
                                                        id='sort-order-radio',
                                                        options=[
                                                            {'label': 'Ascending', 'value': 'asc'},
                                                            {'label': 'Descending', 'value': 'desc'}
                                                        ],
                                                        value='asc',
                                                        labelStyle={'display': 'inline-block', 'margin-right': '10px'}
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            ),
                            html.Div(
                                style={'margin-top': '30px', 'width': '60vw'},
                                children=[
                                    html.Div(
                                        style={'overflow': 'scroll', 'width': '57vw'},
                                        children=[
                                            dash_table.DataTable(
                                                id='table',
                                                columns=[], 
                                                data=[],
                                                page_size=10,
                                                style_table={'border': '1px solid #ddd', 'border-radius': '8px'},
                                                style_cell={'textAlign': 'left', 'padding': '10px'},
                                                style_header={'fontWeight': 'bold', 'backgroundColor': '#f9f9f9'}
                                            ),
                                        ]
                                    )
                                ]
                            ),
                            html.Div(
                                style={'margin-top': '20px', 'text-align': 'center'},
                                children=[
                                    html.Button('Download Filtered Data', id='download-button', n_clicks=0, 
                                                style={'margin-right': '15px'}),
                                    dcc.Download(id='download-csv'),
                                    html.Button('Train', id='train-button', n_clicks=0, 
                                                style={'margin-right': '15px'}),
                                    dcc.Loading(
                                        id="loading-train",
                                        type="default",
                                        children=html.Div(id="train-status", children="", style={'margin': '15px', 'padding': '20px'}),
                                    ),
                                ]
                            ),
                            html.Div(
                                style={'margin-top': '30px', 'padding': '10px', 'border': '1px solid #ddd', 'border-radius': '8px'},
                                children=[
                                    html.H3("Directory Contents", style={'text-align': 'center'}),
                                    html.P("Note: Training may take some time. Existing folders will appear below.", 
                                        style={'text-align': 'center', 'color': '#555', 'margin-bottom': '20px'}),
                                        # Directory View
                                        html.Div([
                                            html.H2("Existing Directory"),
                                            html.Ul(generate_directory_structure(directory_path))
                                        ], style={'width': '48%', 'display': 'inline-block', 'vertical-align': 'top'}),
                                        # File Preview Section
                                        html.Div([
                                            html.H2("File Preview"),
                                            html.Div(id='file-preview')
                                        ], style={'width': '48%', 'display': 'inline-block', 'vertical-align': 'top'})
                                    ]
                            )
                        ]),
                    ]),
                    html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '10px'}, children=[
                        html.Div(className='feature-container', style={'border': '1px solid #3F849B', 'padding': '0', 'borderRadius': '16px', 'width': '229px', 'minHeight': '40px'}, children=[
                            html.H1('Objects', className='Feature-title', style={'color': 'white', 'fontWeight': '700', 'fontSize': '16px', 'padding': '8px 17px', 'backgroundColor': '#3F849B', 'borderRadius': '10px'}),
                            html.Div(style={'padding': '10px', 'display': 'flex', 'flexDirection': 'column', 'gap': '10px'}, children=[
                                html.Div(style={'fontWeight': '400', 'fontSize': '14px', 'color': '#616161', 'display': 'none'}, children=[
                                    html.Label('Select Well:', style={'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'}),
                                    dcc.Dropdown(
                                        id='universal-dropdown', 
                                        options=[{'label': name, 'value': name} for name in df['Universal'].unique()], 
                                        value=df['Universal'].unique(),
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
    ]
)

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
    [Output('universal-dropdown', 'options'),
     Output('universal-dropdown', 'value'),
     Output('table', 'data'),
     Output('table', 'columns')],
    [Input({'type': 'sub-checkbox', 'name': ALL}, 'value'),
     Input({'type': 'detail-checkbox', 'name': ALL}, 'value'),
     Input('date-picker-range-start', 'date'),
     Input('date-picker-range-end', 'date'),
     Input('completion-features-dropdown', 'value'),
     Input('event-features-dropdown', 'value'),
     Input('main-features-dropdown', 'value'),
     Input('additional-features-dropdown', 'value'),
     Input('sort-column-dropdown', 'value'),
     Input('sort-order-radio', 'value'),
     Input({'type': 'detail-checkbox', 'name': ALL}, 'value')]
)
def update_filters(selected_platforms, selected_universal, start_date, end_date, 
                   selected_completion, selected_event, selected_main, 
                   selected_additional, sort_column, sort_order, detail_checkbox):
    if not selected_platforms:
        return [], None, [], []
    
    platform = []
    for item in selected_platforms:
        if len(item) > 0: platform.append(item[0].split()[-1])

    selected_platforms = platform

    universal = []
    for items in selected_universal:
        for item in items:
            universal.append(item)
    
    selected_universal = universal

    
    filtered_df = df[df['Platform'].isin(selected_platforms)]

    universal_options = [{'label': universal, 'value': universal} for universal in filtered_df['Universal'].unique()]

    if selected_universal:
        selected_universal = [univ for univ in selected_universal if univ in filtered_df['Universal'].unique()]

    if selected_universal:
        filtered_df = filtered_df[filtered_df['Universal'].isin(selected_universal)]

    filtered_df = filtered_df[(filtered_df['DATE'] >= start_date) & (filtered_df['DATE'] <= end_date)]

    columns_to_keep = ['DATE'] + additional + targets + selected_main + ['CHOKE'] + ratios + selected_completion + selected_event + selected_additional
    filtered_df = filtered_df[columns_to_keep]

    if sort_column and sort_order:
        filtered_df = filtered_df.sort_values(by=sort_column, ascending=(sort_order == 'asc'))

    filtered_df['DATE'] = filtered_df['DATE'].dt.strftime('%d-%m-%Y')
    if 'GAS' in filtered_df.columns:
        filtered_df['GAS'] = filtered_df['GAS'].round(2)
    if 'WATER' in filtered_df.columns:
        filtered_df['WATER'] = filtered_df['WATER'].astype(int)
    if 'OIL' in filtered_df.columns:
        filtered_df['OIL'] = filtered_df['OIL'].astype(int)

    table_data = filtered_df.to_dict('records')
    table_columns = [{'name': col, 'id': col} for col in filtered_df.columns]

    return universal_options, selected_universal, table_data, table_columns


@app.callback(
    Output('download-csv', 'data'),
    Input('download-button', 'n_clicks'),
    State({'type': 'sub-checkbox', 'name': ALL}, 'value'),
    State({'type': 'detail-checkbox', 'name': ALL}, 'value'),
    State('date-picker-range-start', 'date'),
    State('date-picker-range-end', 'date'),
    State('completion-features-dropdown', 'value'),
    State('event-features-dropdown', 'value'),
    State('main-features-dropdown', 'value'),
    State('additional-features-dropdown', 'value'),
    State('sort-column-dropdown', 'value'),
    State('sort-order-radio', 'value')
)
def download_filtered_data(n_clicks, selected_platforms, selected_universal, start_date, end_date, 
                           selected_completion, selected_event, selected_main, selected_additional, 
                           sort_column, sort_order):
    if n_clicks == 0:
        raise PreventUpdate
    
    platform = []
    for item in selected_platforms:
        if len(item) > 0: platform.append(item[0].split()[-1])

    selected_platforms = platform

    universal = []
    for items in selected_universal:
        for item in items:
            universal.append(item)
    
    selected_universal = universal

    filtered_df = df[df['Platform'].isin(selected_platforms)]
    if selected_universal:
        filtered_df = filtered_df[filtered_df['Universal'].isin(selected_universal)]
    filtered_df = filtered_df[(filtered_df['DATE'] >= start_date) & (filtered_df['DATE'] <= end_date)]

    columns_to_keep = ['DATE'] + additional + selected_main + ['CHOKE'] + targets + ratios + selected_completion + selected_event + selected_additional
    filtered_df = filtered_df[columns_to_keep]

    if sort_column and sort_order:
        filtered_df = filtered_df.sort_values(by=sort_column, ascending=(sort_order == 'asc'))

    filtered_df['DATE'] = filtered_df['DATE'].dt.strftime('%d-%m-%Y')
    csv_string = filtered_df.to_csv(index=False, encoding='utf-8')

    return dict(content=csv_string, filename='filtered_data.csv')

@app.callback(
    Output('train-status', 'children'),
    Input('train-button', 'n_clicks'),
    State({'type': 'sub-checkbox', 'name': ALL}, 'value'),
    State({'type': 'detail-checkbox', 'name': ALL}, 'value'),
    State('date-picker-range-start', 'date'),
    State('date-picker-range-end', 'date'),
    State('completion-features-dropdown', 'value'),
    State('event-features-dropdown', 'value'),
    State('main-features-dropdown', 'value'),
    State('additional-features-dropdown', 'value'),
    State('sort-column-dropdown', 'value'),
    State('sort-order-radio', 'value')
)
def run_ml_and_update_directory(n_clicks, selected_platforms, selected_universal, start_date, end_date, 
                                selected_completion, selected_event, selected_main, selected_additional, 
                                sort_column, sort_order):
    if n_clicks == 0:
        raise PreventUpdate
    
    platform = []
    for item in selected_platforms:
        if len(item) > 0: platform.append(item[0].split()[-1])

    selected_platforms = platform

    universal = []
    for items in selected_universal:
        for item in items:
            universal.append(item)
    
    selected_universal = universal

    filtered_df = df[df['Platform'].isin(selected_platforms)]
    
    if selected_universal:
        filtered_df = filtered_df[filtered_df['Universal'].isin(selected_universal)]

    columns_to_keep = ['DATE'] + additional + selected_main + ['CHOKE'] + targets + ratios + selected_completion + selected_event + selected_additional
    filtered_df = filtered_df[columns_to_keep]

    if sort_column and sort_order:
        filtered_df = filtered_df.sort_values(by=sort_column, ascending=(sort_order == 'asc'))
    filtered_df.drop(columns=['WHP', 'WHT'], inplace=True)
    
    folder_marker = mlp.run_ml(filtered_df, start_date, end_date)
    
    directory_content = []
    for item in os.listdir(folder_marker):
        item_path = os.path.join(folder_marker, item)
        if os.path.isdir(item_path):
            directory_content.append(html.Li(f"Folder: {item}", id={'type': 'folder', 'name': item}))
        else:
            file_type = item.split('.')[-1]
            if file_type in ['png', 'csv', 'xlsx']:
                directory_content.append(html.Li(
                    html.A(item, href="#", id={'type': 'file', 'name': item}),
                    id={'type': 'file-list', 'name': item}
                ))
    os.execv(sys.executable, ['python'] + sys.argv)
    return directory_content

def serve_image(image_path):
    with open(image_path, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('ascii')
    return f"data:image/png;base64,{encoded_image}"

@app.callback(
    Output('file-preview', 'children'),
    Input({'type': 'file-btn', 'index': ALL}, 'n_clicks'),
    State({'type': 'file-btn', 'index': ALL}, 'id')
)
def display_file_preview(n_clicks_list, file_ids):
    if not any(n_clicks_list):
        return "Select a file to preview."

    clicked_idx = n_clicks_list.index(max(n_clicks_list))
    file_path = file_ids[clicked_idx]['index']
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.png':
        return html.Img(src=serve_image(file_path), style={'width': '100%', 'height': 'auto'})
    
    elif file_ext == '.csv':
        df = pd.read_csv(file_path)
        return dash_table.DataTable(
            columns=[{'name': col, 'id': col} for col in df.columns],
            data=df.head(10).to_dict('records'),  
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'}
        )
    
    elif file_ext == '.xlsx':
        df = pd.read_excel(file_path)
        return dash_table.DataTable(
            columns=[{'name': col, 'id': col} for col in df.columns],
            data=df.head(10).to_dict('records'), 
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'}
        )
    
    return "File format not supported for preview."

if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        webbrowser.open_new("http://127.0.0.1:8050/")
    app.run_server(debug=True, dev_tools_ui=True)