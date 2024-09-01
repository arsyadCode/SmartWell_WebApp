import dash
import os, webbrowser
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import curve_cum_function as ccf
from dash import dcc, html
from dash.dependencies import Input, Output, State
from datetime import datetime

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'DCA'

excel_file = './Data/data_resampling_cumProd.xlsx'
xls = pd.ExcelFile(excel_file)
sheet_names = xls.sheet_names

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Label('Select Well:'),
            dcc.Dropdown(id='well-name', options=[{'label': name, 'value': name} for name in sheet_names], value='B-L-18')
        ], width=4),
        dbc.Col([
            html.Label('Start Forecast Date:'),
            dcc.DatePickerSingle(
                id='foil-date-picker',
                date=datetime(2024, 4, 1),
                display_format='DD/MM/YYYY'
            )
        ], width=2),
        dbc.Col([
            html.Label('Rate Intervention:'),
            dcc.Input(id='oil-rate-intervention', type='number', value=0, step=50)
        ], width=2),
        dbc.Col([
            html.Label('Forecast Months:'),
            dcc.Input(id='months-end-date', type='number', value=120, min=1)
        ], width=2),
        dbc.Col([
            html.Label('Rate Limit Value:'),
            dcc.Input(id='limit-value', type='number', value=0.0, step=0.1)
        ], width=2),
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
    ])
])

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
    Input('well-name', 'value'), 
    Input('foil-date-picker', 'date'),
    Input('months-end-date', 'value'),
    Input('date-slider', 'value'),
    Input('oil-rate-intervention', 'value'),
    Input('b-value-slider', 'value'),
    Input('limit-value', 'value')
)
def update_plots(well_name, foil_date, months_end_date, slider_value, rate_intervention, b_value, limit_value):
    foil_date = pd.to_datetime(foil_date)
    
    df = pd.read_excel(excel_file, sheet_name=well_name)
    df['DATE_STAMP'] = pd.to_datetime(df['DATE_STAMP'], format='%d/%m/%Y', dayfirst=True)
    
    start_date = df['DATE_STAMP'].iloc[slider_value[0]]
    end_date = df['DATE_STAMP'].iloc[slider_value[1]]
    
    best_b_oil, oil_exp_di, oil_har_di, oil_hyper_di, oil_exp_model, oil_har_model, oil_hyper_model, df_oil = ccf.process_data(excel_file, well_name, start_date, end_date, 'CORR_OIL_RATE_STBD', 'oil')
    
    last_rate = df[df['CORR_OIL_RATE_STBD'] != 0]['CORR_OIL_RATE_STBD'].iloc[-1] + rate_intervention
    qi = last_rate

    foil_date = foil_date.replace(day=1)
    end_date = foil_date + pd.DateOffset(months=months_end_date)
    date_range = pd.date_range(start=foil_date, end=end_date, freq='MS')
    marker_y = df[df['DATE_STAMP'] == start_date]['CORR_OIL_RATE_STBD'].values[0]

    forecast_df = pd.DataFrame({'DATE': date_range, 'TIME': range(len(date_range))})
    forecast_df['Forecast_Oil_Exponential'] = ccf.exponential_rate(last_rate, oil_exp_di, forecast_df['TIME'])
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
    oil_fig.add_trace(go.Scatter(x=df['DATE_STAMP'], y=df['CORR_OIL_RATE_STBD'], mode='markers', name='Data', marker=dict(color='red', size=5)))
    oil_fig.add_trace(go.Scatter(x=df_oil['DATE_STAMP'], y=oil_exp_model, mode='lines', name='Exponential Model', line=dict(color='blue')))
    oil_fig.add_trace(go.Scatter(x=df_oil['DATE_STAMP'], y=oil_hyper_model, mode='lines', name=f'Hyperbolic Model (best b = {best_b_oil})', line=dict(color='green')))
    oil_fig.add_trace(go.Scatter(x=df_oil['DATE_STAMP'], y=oil_har_model, mode='lines', name='Harmonic Model', line=dict(color='orange')))
    
    if b_value == 0.000:
        oil_fig.add_trace(go.Scatter(x=forecast_df['DATE'], y=forecast_df['Forecast_Oil_Exponential'], mode='lines', name=f'Exponential Forecast (b={b_value:.3f}, di={oil_exp_di:.2f}, qi={qi:.2f})', line=dict(color='LightBlue')))
        crossed = forecast_df[forecast_df['Forecast_Oil_Exponential'] <= limit_value]
        reserves_output = "Reserves (Exponential): ", html.Span(f"{reserves_exp:.2f} stb", style={'fontWeight': 'bold'})
    elif b_value == 1.000:
        oil_fig.add_trace(go.Scatter(x=forecast_df['DATE'], y=forecast_df['Forecast_Oil_Harmonic'], mode='lines', name=f'Harmonic Forecast (b={b_value:.3f}, di={oil_har_di:.2f}, qi={qi:.2f})', line=dict(color='LightSalmon')))
        crossed = forecast_df[forecast_df['Forecast_Oil_Harmonic'] <= limit_value]
        reserves_output = "Reserves (Harmonic): ", html.Span(f"{reserves_har:.2f} stb", style={'fontWeight': 'bold'})
    else:
        oil_fig.add_trace(go.Scatter(x=forecast_df['DATE'], y=forecast_df['Forecast_Oil_Hyperbolic'], mode='lines', name=f'Hyperbolic Forecast (b={b_value:.3f}, di={oil_hyper_di:.2f}, qi={qi:.2f})', line=dict(color='LightGreen')))
        crossed = forecast_df[forecast_df['Forecast_Oil_Hyperbolic'] <= limit_value]
        reserves_output = "Reserves (Hyperbolic): ", html.Span(f"{reserves_hyper:.2f} stb", style={'fontWeight': 'bold'})

    # Add horizontal line at limit value
    oil_fig.add_trace(go.Scatter(x=[foil_date, end_date], y=[limit_value, limit_value], mode='lines', name=f'Rate Limit ({limit_value} bopd)', line=dict(color='red', dash='dash')))

    # Check if the forecast crosses the limit value
    alert_message = []
    if not crossed.empty:
        crossing_date = crossed['DATE'].iloc[0]
        alert_message.append(
            dbc.Alert(
                [
                    "Alert: Forecast crosses limit on ",
                    html.Span(crossing_date.strftime("%Y-%m-%d"), style={'fontWeight': 'bold'}),
                ],
                color='danger', dismissable=True, duration=7000,
            )
        )
    
    oil_fig.add_trace(go.Scatter(x=[start_date], y=[marker_y], mode='markers', name='Initial Date', marker=dict(color='black', size=7)))

    oil_fig.update_layout(
        title=f'Oil Rate Comparison of Decline Models Well {well_name}',
        xaxis_title='Date',
        yaxis_title='Oil Rate (bopd)',
        xaxis=dict(tickformat='%Y-%m-%d'),
        legend_title="Legend"
    )

    return oil_fig, alert_message, reserves_output

if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        webbrowser.open_new("http://127.0.0.1:8050/")
    app.run_server(debug=True)
