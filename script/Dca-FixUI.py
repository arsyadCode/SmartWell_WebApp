import dash
import os, webbrowser
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import curve_cum_function as ccf
from dash import dcc, html, dash_table, callback_context
from dash.dependencies import Input, Output, State, ALL
from datetime import datetime

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'DCA'

excel_file = './Data/data_resampling_cumProd.xlsx'
xls = pd.ExcelFile(excel_file)
sheet_names = xls.sheet_names

Objects = {}
for name in sheet_names:
    parents = name.split("-")
    main, sub, detail = parents[0], parents[1], parents[2]

    if main not in Objects:
        Objects[main] = {}
    if "Platform "+sub not in Objects[main]:
        Objects[main]["Platform "+sub] = []
    Objects[main]["Platform "+sub].append(name)

def create_nested_checkboxes(structure):
    elements = []
    
    for main, subs in structure.items():
        main_checkbox = html.Div([
            dcc.Checklist(
                options=[{'label': main, 'value': main}],
                id={'type': 'main-checkbox', 'name': f'checkbox-{main}'},
                inline=True,
                labelStyle={'display': 'flex', 'marginBottom': '19px', 'gap': '15px', 'align-items': 'center', 'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'},
                inputStyle={'transform': 'scale(1.5)', 'borderRadius': '6px'}
            )
        ], style={'marginLeft': '8px'})
        
        sub_elements = []
        for sub, details in subs.items():
            sub_checkbox = dcc.Checklist(
                options=[{'label': sub, 'value': sub}],
                id={'type': 'sub-checkbox', 'name': f'checkbox-{main}-{sub}'},
                inline=True,
                labelStyle={'display': 'flex', 'marginBottom': '19px', 'gap': '15px', 'alignItems': 'center', 'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'},
                inputStyle={'transform': 'scale(1.5)', 'border-radius': '6px'}
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

table_data = pd.DataFrame(columns=["Well Name", "Start Date", "End Date", "Reserves", "Cut Off Date"])
selected_b_value = 0.5

app.layout = dbc.Container([
    html.Div(style={'display': 'flex', 'gap': 28, 'padding': '50px'}, children=[
        html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '10px'}, children=[
            html.Div(className='feature-container', style={'border': '1px solid #3F849B', 'padding': '0', 'borderRadius': '16px', 'width': '174px', 'height': '123px'}, children=[
                html.H1('Plot Type', className='Feature-title', style={'color': 'white', 'fontWeight': '700', 'fontSize': '16px', 'padding': '8px 17px', 'backgroundColor': '#3F849B', 'borderRadius': '10px'}),
                html.Div(style={'padding': '10px 25px'}, children=[
                    dcc.Checklist(
                        id='plot-type',
                        options=[
                            {'label': 'Scatter', 'value': 'scatter'},
                            {'label': 'Line', 'value': 'line'},
                        ],
                        value=['scatter', 'line'], 
                        labelStyle={'display': 'flex', 'margin-bottom': '9.5px', 'gap': '15px', 'align-items': 'center', 'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'},
                        inputStyle={'transform': 'scale(1.5)', 'border-radius': '6px'}
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
                        labelStyle={'display': 'flex', 'margin-bottom': '9.5px', 'gap': '15px', 'align-items': 'center', 'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'},
                        inputStyle={'transform': 'scale(1.5)', 'border-radius': '6px'}
                    ),
                ])
            ]),
            html.Div(className='feature-container', style={'border': '1px solid #3F849B', 'padding': '0', 'borderRadius': '16px', 'width': '174px', 'height': '153px'}, children=[
                html.H1('Models', className='Feature-title', style={'color': 'white', 'fontWeight': '700', 'fontSize': '16px', 'padding': '8px 17px', 'backgroundColor': '#3F849B', 'borderRadius': '10px'}),
                html.Div(style={'padding': '10px 25px'}, children=[
                    dcc.RadioItems(
                        id="selected-b-options",
                        options=[
                            {'label': 'Exponential', 'value': 0},
                            {'label': 'Hyperbolic', 'value': 0.5},
                            {'label': 'Harmonic', 'value': 1},
                        ],
                        value=selected_b_value, 
                        labelStyle={'display': 'flex', 'margin-bottom': '9.5px', 'gap': '15px', 'align-items': 'center', 'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'},
                        inputStyle={'transform': 'scale(1.5)', 'border-radius': '6px'}
                    ),
                ])
            ]),
            html.Div(className='feature-container', style={'border': '1px solid #3F849B', 'padding': '0', 'borderRadius': '16px', 'width': '174px', 'minHeight': '123px'}, children=[
                html.H1('Settings', className='Feature-title', style={'color': 'white', 'fontWeight': '700', 'fontSize': '16px', 'padding': '8px 17px', 'backgroundColor': '#3F849B', 'borderRadius': '10px'}),
                html.Div(style={'padding': '10px', 'display': 'flex', 'flexDirection': 'column', 'gap': '10px'}, children=[
                    html.Div(style={'width': '100%'}, children=[
                        html.Label('Start Forecast Date:', style={'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'}),
                        dcc.DatePickerSingle(
                            id='foil-date-picker',
                            date=datetime(2024, 4, 1),
                            display_format='DD/MM/YYYY', 
                            style={ 'border': '1px solid #616161', 'borderRadius': '6px', 'width': '134px', 'height': '30px', 'color': 'black', 'overflow': 'hidden', 'display': 'flex', 'alignItems': 'center' },
                        )
                    ]),
                    html.Div(style={'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'}, children=[
                        html.Label('Forecast Months:', style={'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'}),
                        dcc.Input(
                            id='months-end-date', 
                            type='number', 
                            value=120, 
                            min=1, 
                            style={'border': '1px solid #616161', 'borderRadius': '6px', 'width': '134px', 'height': '30px', 'color': 'black', 'overflow': 'hidden', 'display': 'flex', 'alignItems': 'center'}
                        )
                    ]),
                    html.Div(style={'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'}, children=[
                        html.Label('Rate Intervention (bopd):', style={'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'}),
                        dcc.Input(
                            id='oil-rate-intervention', 
                            type='number', 
                            value=0, 
                            step=50, 
                            style={'border': '1px solid #616161', 'borderRadius': '6px', 'width': '134px', 'height': '30px', 'color': 'black', 'overflow': 'hidden', 'display': 'flex', 'alignItems': 'center'}
                        )
                    ]),
                    html.Div(style={'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'}, children=[
                        html.Label('Rate Limit Value (bopd):', style={'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'}),
                        dcc.Input(
                            id='limit-value', 
                            type='number', 
                            value=0.0, 
                            step=0.1, 
                            style={'border': '1px solid #616161', 'borderRadius': '6px', 'width': '134px', 'height': '30px', 'color': 'black', 'overflow': 'hidden', 'display': 'flex', 'alignItems': 'center'}
                        )
                    ]),
                ])
            ]), 
        ]),
        html.Div(children=[
            dcc.Tabs(id='tab-container',
                value='B-L-18',
                children=[],
                content_style={'textAlign':'center'}
            ),
            html.Div(style={'border': '1px solid grey', 'padding': '21px', 'borderBottomLeftRadius': '30px', 'borderBottomRightRadius': '30px', 'borderTopRightRadius': '30px'}, children=[
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
                    ], width=4),
                ]),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='oil-plot'), width=12),
                ]),
                dbc.Row([
                dbc.Col(html.Div(id='reserves-output'), width=12),
                ], style={'margin-bottom': '10px'}),
                dbc.Row([
                    dbc.Col([
                        html.Label('Select Date Range:'),
                        dcc.RangeSlider(
                            id='date-slider',
                            min=0,
                            max=1000,
                            step=1,
                            value=[0, 1000],
                            marks={},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], width=12),
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Div(id='alert', children=[])
                    ], width=12),
                ]),
                dash_table.DataTable(
                    id="data-table",
                    columns=[
                        {"name": "Well Name", "id": "Well Name"},
                        {"name": "Start Date", "id": "Start Date"},
                        {"name": "End Date", "id": "End Date"},
                        {"name": "Start Forecast Date", "id": "Start Forecast Date"},
                        {"name": "Reserves (stb)", "id": "Reserves (stb)"},
                        {"name": "Rate Intervention (bopd)", "id": "Rate Intervention (bopd)"},
                        {"name": "Cut Off Date", "id": "Cut Off Date"}
                    ],
                    data=table_data.to_dict("records"),
                    editable=True,
                    row_deletable=True,
                    style_table={'margin-top': '20px'}
                ),
                
                html.Div([
                    html.Button("Update data", id="update-button", n_clicks=0),
                    html.Button("Download data table", id="download-button", n_clicks=0)
                ], style={"display": "flex", "gap": "10px", "margin-top": "10px"}),

                dcc.Download(id="download-csv")
            ]),
        ]),
        html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '10px'}, children=[
            html.Div(className='feature-container', style={'border': '1px solid #3F849B', 'padding': '0', 'borderRadius': '16px', 'width': '229px', 'minHeight': '40px'}, children=[
                html.H1('Objects', className='Feature-title', style={'color': 'white', 'fontWeight': '700', 'fontSize': '16px', 'padding': '8px 17px', 'backgroundColor': '#3F849B', 'borderRadius': '10px'}),
                html.Div(style={'padding': '10px', 'display': 'flex', 'flexDirection': 'column', 'gap': '10px'}, children=[
                    html.Div(style={'fontWeight': '400', 'fontSize': '14px', 'color': '#616161', 'display': 'none'}, children=[
                        html.Label('Select Well:', style={'fontWeight': '400', 'fontSize': '14px', 'color': '#616161'}),
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
    ])
])

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
    Input('update-button', 'n_clicks'),
    Input('well-name', 'value'),
    Input('foil-date-picker', 'date'),
    Input('months-end-date', 'value'),
    Input('date-slider', 'value'),
    Input('oil-rate-intervention', 'value'),
    Input('b-value-slider', 'value'),
    Input('limit-value', 'value'),
    Input('data-table', 'data'),
    Input('legend-status', 'value'),
    Input('plot-type', 'value'),
    Input('selected-b-options', 'value'),
    State('b-value-slider', 'value'),
    State('selected-b-options', 'value'),
)
def update_plots(n_clicks, well_name, foil_date, months_end_date, slider_value, rate_intervention, b_value, limit_value, rows, legend_status, plot_type, selected_b_options, prev_b_value, prev_selected_b_options):
    if rows is None:
        rows = [] 

    show_legend = 'on' in legend_status;
    scatter = 'scatter' in plot_type;
    line = 'line' in plot_type;


    foil_date = pd.to_datetime(foil_date)
    
    df = pd.read_excel(excel_file, sheet_name=well_name)
    df['DATE_STAMP'] = pd.to_datetime(df['DATE_STAMP'], format='%d/%m/%Y', dayfirst=True)
    
    start_date = df['DATE_STAMP'].iloc[slider_value[0]]
    end_date = df['DATE_STAMP'].iloc[slider_value[1]]
    end_dates = df['DATE_STAMP'].iloc[slider_value[1]]
    
    best_b_oil, oil_exp_di, oil_har_di, oil_hyper_di, oil_exp_model, oil_har_model, oil_hyper_model, df_oil = ccf.process_data(excel_file, well_name, start_date, end_date, 'CORR_OIL_RATE_STBD', 'oil')
    
    last_rate = df[df['CORR_OIL_RATE_STBD'] != 0]['CORR_OIL_RATE_STBD'].iloc[-1] + rate_intervention
    qi = last_rate

    foil_date = foil_date.replace(day=1)
    end_date = foil_date + pd.DateOffset(months=months_end_date)
    date_range = pd.date_range(start=foil_date, end=end_date, freq='MS')
    marker_y = df[df['DATE_STAMP'] == start_date]['CORR_OIL_RATE_STBD'].values[0]

    forecast_df = pd.DataFrame({'DATE': date_range, 'TIME': range(len(date_range))})
    forecast_df['Forecast_Oil_Exponential'] = ccf.exponential_rate(last_rate, oil_exp_di, forecast_df['TIME'])
    
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    if triggered_id == 'selected-b-options':
        selectedData = selected_b_options
        b_value = selected_b_options
    elif triggered_id == 'b-value-slider':
        if b_value == 0 or b_value == 1: selectedData = b_value
        else: selectedData = 0.5
    else:
        selectedData = selected_b_options
    
    if(b_value != 0):
        forecast_df['Forecast_Oil_Hyperbolic'] = ccf.hyperbolic_rate(last_rate, oil_hyper_di, b_value, forecast_df['TIME'])
        forecast_df['Oil_Cumulative_Hyper'] = ccf.cum_hyperbolic(forecast_df['Forecast_Oil_Hyperbolic'].iloc[0], oil_hyper_di, forecast_df['Forecast_Oil_Hyperbolic'], b_value)
        forecast_df['Oil_Cumulative_Hyper'] += df['OIL_CUMULATIVE_PRODUCTION'].iloc[-1]
        forecast_df['Oil_Cumulative_HyperTotal'] = forecast_df['Oil_Cumulative_Hyper']

        time_EUR_hyper = forecast_df[forecast_df['Forecast_Oil_Hyperbolic'] >= limit_value].iloc[-1]
        EUR_hyper = time_EUR_hyper['Oil_Cumulative_HyperTotal']
        reserves_hyper = EUR_hyper - df['OIL_CUMULATIVE_PRODUCTION'].iloc[-1]
    forecast_df['Forecast_Oil_Harmonic'] = ccf.harmonic_rate(last_rate, oil_har_di, forecast_df['TIME'])

    forecast_df['Oil_Cumulative_Exp'] = ccf.cum_exponential(forecast_df['Forecast_Oil_Exponential'].iloc[0], oil_exp_di, forecast_df['Forecast_Oil_Exponential'])
    forecast_df['Oil_Cumulative_Exp'] += df['OIL_CUMULATIVE_PRODUCTION'].iloc[-1]
    forecast_df['Oil_Cumulative_Har'] = ccf.cum_harmonic(forecast_df['Forecast_Oil_Harmonic'].iloc[0], oil_har_di, forecast_df['Forecast_Oil_Harmonic'])
    forecast_df['Oil_Cumulative_Har'] += df['OIL_CUMULATIVE_PRODUCTION'].iloc[-1]

    forecast_df['Oil_Cumulative_ExpTotal'] = forecast_df['Oil_Cumulative_Exp']
    forecast_df['Oil_Cumulative_EarTotal'] = forecast_df['Oil_Cumulative_Har']

    time_EUR_exp = forecast_df[forecast_df['Forecast_Oil_Exponential'] >= limit_value].iloc[-1]
    time_EUR_har = forecast_df[forecast_df['Forecast_Oil_Harmonic'] >= limit_value].iloc[-1]
    EUR_exp = time_EUR_exp['Oil_Cumulative_ExpTotal']
    EUR_har = time_EUR_har['Oil_Cumulative_EarTotal']
    reserves_exp = EUR_exp - df['OIL_CUMULATIVE_PRODUCTION'].iloc[-1]
    reserves_har = EUR_har - df['OIL_CUMULATIVE_PRODUCTION'].iloc[-1]

    oil_fig = go.Figure()
    if scatter: 
        oil_fig.add_trace(go.Scatter(x=df['DATE_STAMP'], y=df['CORR_OIL_RATE_STBD'], mode='markers', name='Data', marker=dict(color='brown', size=5), showlegend=show_legend and scatter))
    if line: 
        oil_fig.add_trace(go.Scatter(x=df_oil['DATE_STAMP'], y=oil_exp_model, mode='lines', name='Exponential Model', line=dict(color='blue'), showlegend=show_legend and line))
        oil_fig.add_trace(go.Scatter(x=df_oil['DATE_STAMP'], y=oil_hyper_model, mode='lines', name=f'Hyperbolic Model (best b = {best_b_oil})', line=dict(color='green'), showlegend=show_legend and line))
        oil_fig.add_trace(go.Scatter(x=df_oil['DATE_STAMP'], y=oil_har_model, mode='lines', name='Harmonic Model', line=dict(color='orange'), showlegend=show_legend and line))
    
    val_reserves = 0
    if b_value == 0.000:
        if line:
            oil_fig.add_trace(go.Scatter(x=forecast_df['DATE'], y=forecast_df['Forecast_Oil_Exponential'], mode='lines', name=f'Exponential Forecast (b={b_value:.3f}, di={oil_exp_di:.2f}, qi={qi:.2f})', line=dict(color='LightBlue'), showlegend=show_legend and line))
        crossed = forecast_df[forecast_df['Forecast_Oil_Exponential'] <= limit_value]
        reserves_output = "Reserves (Exponential): ", html.Span(f"{reserves_exp:.2f} stb", style={'fontWeight': 'bold'})
        val_reserves = reserves_exp
    elif b_value == 1.000:
        if line:
            oil_fig.add_trace(go.Scatter(x=forecast_df['DATE'], y=forecast_df['Forecast_Oil_Harmonic'], mode='lines', name=f'Harmonic Forecast (b={b_value:.3f}, di={oil_har_di:.2f}, qi={qi:.2f})', line=dict(color='LightSalmon'), showlegend=show_legend and line))
        crossed = forecast_df[forecast_df['Forecast_Oil_Harmonic'] <= limit_value]
        reserves_output = "Reserves (Harmonic): ", html.Span(f"{reserves_har:.2f} stb", style={'fontWeight': 'bold'})
        val_reserves = reserves_har
    else:
        if line :
            oil_fig.add_trace(go.Scatter(x=forecast_df['DATE'], y=forecast_df['Forecast_Oil_Hyperbolic'], mode='lines', name=f'Hyperbolic Forecast (b={b_value:.3f}, di={oil_hyper_di:.2f}, qi={qi:.2f})', line=dict(color='LightGreen'), showlegend=show_legend and line))
        crossed = forecast_df[forecast_df['Forecast_Oil_Hyperbolic'] <= limit_value]
        reserves_output = "Reserves (Hyperbolic): ", html.Span(f"{reserves_hyper:.2f} stb", style={'fontWeight': 'bold'})
        val_reserves = reserves_hyper

    if line : 
        oil_fig.add_trace(go.Scatter(x=[foil_date, end_date], y=[limit_value, limit_value], mode='lines', name=f'Rate Limit ({limit_value} bopd)', line=dict(color='red', dash='dash'), showlegend=show_legend and line))

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
        oil_fig.add_trace(go.Scatter(x=[start_date], y=[marker_y], mode='markers', name='Initial Date', marker=dict(color='black', size=7), showlegend=show_legend and scatter))

    oil_fig.update_layout(
        title=f'Oil Rate Comparison of Decline Models Well {well_name}',
        xaxis_title='Date',
        yaxis_title='Oil Rate (bopd)',
        xaxis=dict(tickformat='%d-%m-%Y'),
        legend_title="Legend"
    )

    new_row = {
        "Well Name": well_name,
        "Start Date": start_date.strftime('%d-%m-%Y'),
        "End Date": end_dates.strftime('%d-%m-%Y'),
        "Start Forecast Date": foil_date.strftime('%d-%m-%Y'),
        "Reserves (stb)": f"{val_reserves:.5f}",
        "Rate Intervention (bopd)": rate_intervention,
        "Cut Off Date": crossing_date.strftime('%d-%m-%Y') if not crossed.empty else "N/A"
    }
    
    if n_clicks:
        existing_row = next((row for row in rows if row['Well Name'] == new_row['Well Name']), None)
        if existing_row:
            rows[rows.index(existing_row)] = new_row
        else:
            rows.append(new_row)
        rows = sorted(rows, key=lambda x: float(x['Reserves (stb)']), reverse=True)

    return oil_fig, alert_message, reserves_output, rows, selectedData, b_value

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
