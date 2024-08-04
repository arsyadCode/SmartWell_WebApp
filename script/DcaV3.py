import dash
import os, webbrowser
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import curve_cum_function as ccf
from dash import dcc, html
from dash.dependencies import Input, Output
from datetime import datetime

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'DCA'

excel_file = './Data/data_resampling.xlsx'
xls = pd.ExcelFile(excel_file)
sheet_names = xls.sheet_names

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Label('Select Well:'),
            dcc.Dropdown(id='well-name', options=[{'label': name, 'value': name} for name in sheet_names], value=sheet_names[0])
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
            dcc.Input(id='oil-rate-intervention', type='number', value=0, step=100)
        ], width=2),
        dbc.Col([
            html.Label('Forecast Months:'),
            dcc.Input(id='months-end-date', type='number', value=120, min=1)
        ], width=2),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='oil-plot'), width=12),
    ]),
    dbc.Row([
        dbc.Col([
            html.Label('Select Initial Date:'),
            dcc.Slider(
                id='date-slider', 
                min=0, 
                step=1, 
                value=0, 
                marks={}, 
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], width=12),
    ])
])

@app.callback(
    Output('date-slider', 'max'),
    Output('date-slider', 'marks'),
    Input('well-name', 'value')
)
def update_slider(well_name):
    df = pd.read_excel(excel_file, sheet_name=well_name)
    df['DATE_STAMP'] = pd.to_datetime(df['DATE_STAMP'], format='%d/%m/%Y', dayfirst=True)
    max_date = df['DATE_STAMP'].max()
    df_filtered = df[df['DATE_STAMP'] <= max_date]
    marks = {i: {'label': '', 'style': {'display': 'none'}} for i, date in enumerate(df_filtered['DATE_STAMP'])}
    return len(df_filtered) - 1, marks

@app.callback(
    Output('oil-plot', 'figure'),
    Input('well-name', 'value'), 
    Input('foil-date-picker', 'date'),
    Input('months-end-date', 'value'),
    Input('date-slider', 'value'),
    Input('oil-rate-intervention', 'value')
)
def update_plots(well_name, foil_date, months_end_date, slider_value, rate_intervention):
    foil_date = pd.to_datetime(foil_date)
    
    df = pd.read_excel(excel_file, sheet_name=well_name)
    df['DATE_STAMP'] = pd.to_datetime(df['DATE_STAMP'], format='%d/%m/%Y', dayfirst=True)
    
    start_date = df['DATE_STAMP'].iloc[slider_value]
    end_date = df['DATE_STAMP'].max()
    
    df_filtered = df[(df['DATE_STAMP'] >= start_date) & (df['DATE_STAMP'] <= end_date)]
    
    best_b_oil, oil_exp_di, oil_har_di, oil_hyper_di, oil_exp_model, oil_har_model, oil_hyper_model, df_oil = ccf.process_data(excel_file, well_name, start_date, end_date, 'CORR_OIL_RATE_STBD', 'oil')
    
    last_rate = df[df['CORR_OIL_RATE_STBD'] != 0]['CORR_OIL_RATE_STBD'].iloc[-1] + rate_intervention # Need to be validation

    foil_date = foil_date.replace(day=1)
    end_date = foil_date + pd.DateOffset(months=months_end_date)
    date_range = pd.date_range(start=foil_date, end=end_date, freq='MS')
    marker_y = df[df['DATE_STAMP'] == start_date]['CORR_OIL_RATE_STBD'].values[0]

    forecast_df = pd.DataFrame({'DATE': date_range, 'TIME': range(len(date_range))})
    forecast_df['Forecast_Oil_Exponential'] = ccf.exponential_rate(last_rate, oil_exp_di, forecast_df['TIME'])
    forecast_df['Forecast_Oil_Hyperbolic'] = ccf.hyperbolic_rate(last_rate, oil_hyper_di, best_b_oil, forecast_df['TIME'])
    forecast_df['Forecast_Oil_Harmonic'] = ccf.harmonic_rate(last_rate, oil_har_di, forecast_df['TIME'])

    oil_fig = go.Figure()
    oil_fig.add_trace(go.Scatter(x=df['DATE_STAMP'], y=df['CORR_OIL_RATE_STBD'], mode='markers', name='Data', marker=dict(color='red')))
    oil_fig.add_trace(go.Scatter(x=df_oil['DATE_STAMP'], y=oil_exp_model, mode='lines', name='Exponential Model', line=dict(color='blue')))
    oil_fig.add_trace(go.Scatter(x=df_oil['DATE_STAMP'], y=oil_hyper_model, mode='lines', name=f'Hyperbolic Model b = {best_b_oil}', line=dict(color='green')))
    oil_fig.add_trace(go.Scatter(x=df_oil['DATE_STAMP'], y=oil_har_model, mode='lines', name='Harmonic Model', line=dict(color='orange')))
    oil_fig.add_trace(go.Scatter(x=forecast_df['DATE'], y=forecast_df['Forecast_Oil_Exponential'], mode='lines', name='Exponential Forecast', line=dict(color='LightBlue')))
    oil_fig.add_trace(go.Scatter(x=forecast_df['DATE'], y=forecast_df['Forecast_Oil_Hyperbolic'], mode='lines', name='Hyperbolic Forecast', line=dict(color='LightGreen')))
    oil_fig.add_trace(go.Scatter(x=forecast_df['DATE'], y=forecast_df['Forecast_Oil_Harmonic'], mode='lines', name='Harmonic Forecast', line=dict(color='LightSalmon')))
    oil_fig.add_trace(go.Scatter(x=[start_date], y=[marker_y], mode='markers', name='Selected Date', marker=dict(color='black', size=8)))
    oil_fig.update_layout(title=f'Oil Rate Comparison of Decline Models Well {well_name}', xaxis_title='Date', yaxis_title='Oil Rate (bopd)', xaxis=dict(tickformat='%Y-%m-%d'))

    return oil_fig


if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        webbrowser.open_new("http://127.0.0.1:8050/")
    app.run_server(debug=True)
