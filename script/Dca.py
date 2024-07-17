import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import curve_cum_function as ccf

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'DCA'

# Load the Excel file and get the sheet names
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
            html.Label('Select Date Range:'),
            dcc.DatePickerRange(
                id='date-picker-range',
                display_format='DD/MM/YYYY'
            )
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
            html.Label('Forecast Months:'),
            dcc.Input(id='months-end-date', type='number', value=120, min=1)
        ], width=2),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='oil-plot'), width=12),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='gas-plot'), width=12),
    ]),
])

@app.callback(
    Output('date-picker-range', 'min_date_allowed'),
    Output('date-picker-range', 'max_date_allowed'),
    Output('date-picker-range', 'start_date'),
    Output('date-picker-range', 'end_date'),
    Input('well-name', 'value')
)
def update_date_range(well_name):
    df = pd.read_excel(excel_file, sheet_name=well_name)
    df['DATE_STAMP'] = pd.to_datetime(df['DATE_STAMP'], format='%d/%m/%Y', dayfirst=True)
    min_date = df['DATE_STAMP'].min()
    max_date = df['DATE_STAMP'].max()
    return min_date, max_date, min_date, max_date

@app.callback(
    [Output('oil-plot', 'figure'), Output('gas-plot', 'figure')],
    [Input('well-name', 'value'), 
     Input('date-picker-range', 'start_date'), 
     Input('date-picker-range', 'end_date'),
     Input('foil-date-picker', 'date'),
     Input('months-end-date', 'value')]
)
def update_plots(well_name, start_date, end_date, foil_date, months_end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    foil_date = pd.to_datetime(foil_date)

    best_b_oil, oil_exp_di, oil_har_di, oil_hyper_di, oil_exp_model, oil_har_model, oil_hyper_model, df_oil = ccf.process_data(excel_file, well_name, start_date, end_date, 'CORR_OIL_RATE_STBD', 'oil')
    best_b_gas, gas_exp_di, gas_har_di, gas_hyper_di, gas_exp_model, gas_har_model, gas_hyper_model, df_gas = ccf.process_data(excel_file, well_name, start_date, end_date, 'CORR_GAS_RES_RATE_MMSCFD', 'gas')

    df = pd.read_excel(excel_file, sheet_name=well_name)
    df['DATE_STAMP'] = pd.to_datetime(df['DATE_STAMP'], format='%d/%m/%Y', dayfirst=True)
    last_rate = df[df['CORR_OIL_RATE_STBD'] != 0]['CORR_OIL_RATE_STBD'].iloc[-1]
    last_gas_rate = df.loc[df['DATE_STAMP'] == foil_date, 'CORR_GAS_RES_RATE_MMSCFD'].iloc[0]

    foil_date = foil_date.replace(day=1)
    end_date = foil_date + pd.DateOffset(months=months_end_date)
    date_range = pd.date_range(start=foil_date, end=end_date, freq='MS')

    forecast_df = pd.DataFrame({'DATE': date_range, 'TIME': range(len(date_range))})
    forecast_df['Forecast_Oil_Exponential'] = ccf.exponential_rate(last_rate, oil_exp_di, forecast_df['TIME'])
    forecast_df['Forecast_Oil_Hyperbolic'] = ccf.hyperbolic_rate(last_rate, oil_hyper_di, best_b_oil, forecast_df['TIME'])
    forecast_df['Forecast_Oil_Harmonic'] = ccf.harmonic_rate(last_rate, oil_har_di, forecast_df['TIME'])
    forecast_df['Forecast_Gas_Exponential'] = ccf.exponential_rate(last_gas_rate, gas_exp_di, forecast_df['TIME'])
    forecast_df['Forecast_Gas_Hyperbolic'] = ccf.hyperbolic_rate(last_gas_rate, gas_hyper_di, best_b_gas, forecast_df['TIME'])
    forecast_df['Forecast_Gas_Harmonic'] = ccf.harmonic_rate(last_gas_rate, gas_har_di, forecast_df['TIME'])

    # Plotting for Oil
    oil_fig = go.Figure()
    oil_fig.add_trace(go.Scatter(x=df['DATE_STAMP'], y=df['CORR_OIL_RATE_STBD'], mode='markers', name='Data', marker=dict(color='red')))
    oil_fig.add_trace(go.Scatter(x=df_oil['DATE_STAMP'], y=oil_exp_model, mode='lines', name='Exponential Model', line=dict(color='blue')))
    oil_fig.add_trace(go.Scatter(x=df_oil['DATE_STAMP'], y=oil_hyper_model, mode='lines', name=f'Hyperbolic Model b = {best_b_oil}', line=dict(color='green')))
    oil_fig.add_trace(go.Scatter(x=df_oil['DATE_STAMP'], y=oil_har_model, mode='lines', name='Harmonic Model', line=dict(color='orange')))
    oil_fig.add_trace(go.Scatter(x=forecast_df['DATE'], y=forecast_df['Forecast_Oil_Exponential'], mode='lines', name='Exponential Forecast', line=dict(color='LightBlue')))
    oil_fig.add_trace(go.Scatter(x=forecast_df['DATE'], y=forecast_df['Forecast_Oil_Hyperbolic'], mode='lines', name='Hyperbolic Forecast', line=dict(color='LightGreen')))
    oil_fig.add_trace(go.Scatter(x=forecast_df['DATE'], y=forecast_df['Forecast_Oil_Harmonic'], mode='lines', name='Harmonic Forecast', line=dict(color='LightSalmon')))
    oil_fig.update_layout(title=f'Oil Rate Comparison of Decline Models Well {well_name}', xaxis_title='Date', yaxis_title='Oil Rate (stbd)', xaxis=dict(tickformat='%Y-%m-%d'))

    # Plotting for Gas
    gas_fig = go.Figure()
    gas_fig.add_trace(go.Scatter(x=df['DATE_STAMP'], y=df['CORR_GAS_RES_RATE_MMSCFD'], mode='markers', name='Data', marker=dict(color='red')))
    gas_fig.add_trace(go.Scatter(x=df_gas['DATE_STAMP'], y=gas_exp_model, mode='lines', name='Exponential Model', line=dict(color='blue')))
    gas_fig.add_trace(go.Scatter(x=df_gas['DATE_STAMP'], y=gas_hyper_model, mode='lines', name=f'Hyperbolic Model b = {best_b_gas}', line=dict(color='green')))
    gas_fig.add_trace(go.Scatter(x=df_gas['DATE_STAMP'], y=gas_har_model, mode='lines', name='Harmonic Model', line=dict(color='orange')))
    gas_fig.add_trace(go.Scatter(x=forecast_df['DATE'], y=forecast_df['Forecast_Gas_Exponential'], mode='lines', name='Exponential Forecast', line=dict(color='LightBlue')))
    gas_fig.add_trace(go.Scatter(x=forecast_df['DATE'], y=forecast_df['Forecast_Gas_Hyperbolic'], mode='lines', name='Hyperbolic Forecast', line=dict(color='LightGreen')))
    gas_fig.add_trace(go.Scatter(x=forecast_df['DATE'], y=forecast_df['Forecast_Gas_Harmonic'], mode='lines', name='Harmonic Forecast', line=dict(color='LightSalmon')))
    gas_fig.update_layout(title=f'Gas Rate Comparison of Decline Models Well {well_name}', xaxis_title='Date', yaxis_title='Gas Rate (MMscfd)', xaxis=dict(tickformat='%Y-%m-%d'))

    return oil_fig, gas_fig

if __name__ == '__main__':
    app.run_server(debug=True)
