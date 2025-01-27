import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import os, webbrowser
from dash.exceptions import PreventUpdate
from dash.dependencies import State

df = pd.read_csv('./Data/dataset_toFilter.csv') 
df['DATE'] = pd.to_datetime(df['DATE'])

completion_features = ['VSH', 'PHI', 'SW', 'NET_THICK', 'N_OPEN_RESERVOIR']
event_features = ['EVENT', 'LAST_EVENT', 'EVENT_PLATFORM', 'LAST_EVENT_PLATFORM', 'NORM_PROD_DAYS']
main_features = ['WHP', 'WHT', 'CHOKE']
additional_features = ['CHOKE_FLAG']
ratios = ['LIQUID', 'WATERCUT', 'GLR', 'GOR']
targets = ['OIL', 'WATER', 'GAS']
additional = ['Universal']

app = dash.Dash(__name__)
app.layout = html.Div(
    style={'padding': '20px', 'font-family': 'Arial, sans-serif'},
    children=[
        html.Div(
            children=[
                html.H1("Bekapai DataFrame Display (WIP)",
                        style={'text-align': 'center', 'margin-bottom': '30px', 'position': 'sticky', 'top': 0, 'z-index': 9999, 'background-color': '#f9f9f9', 'padding': '10px'}),
            ]
        ),

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
                            style={'width': '30%'},
                            children=[
                                html.Label('Select Platform:', style={'font-weight': 'bold'}),
                                dcc.Dropdown(
                                    id='platform-dropdown',
                                    options=[{'label': platform, 'value': platform} for platform in df['Platform'].unique()],
                                    value=df['Platform'].unique(), 
                                    multi=True,
                                    placeholder='Select one or more platforms...'
                                )
                            ]
                        ),
                        html.Div(
                            style={'width': '30%'},
                            children=[
                                html.Label('Select Well:', style={'font-weight': 'bold'}),
                                dcc.Dropdown(
                                    id='universal-dropdown',
                                    options=[{'label': universal, 'value': universal} for universal in df['Universal'].unique()],
                                    value=df['Universal'].unique(),
                                    multi=True,
                                    placeholder='Select one or more Universal values...'
                                )
                            ]
                        ),
                        html.Div(
                            style={'width': '30%'},
                            children=[
                                html.Label('Select Date Range:', style={'font-weight': 'bold'}),
                                dcc.DatePickerRange(
                                    id='date-picker-range',
                                    start_date=df['DATE'].min(),
                                    end_date=df['DATE'].max(),
                                    display_format='DD-MM-YYYY'
                                )
                            ]
                        )
                    ]
                ),

                html.Div(
                    style={'display': 'flex', 'justify-content': 'space-between', 'margin-bottom': '20px'},
                    children=[
                        html.Div(
                            style={'width': '48%'},
                            children=[
                                html.Label('Completion Features:', style={'font-weight': 'bold'}),
                                dcc.Dropdown(
                                    id='completion-features-dropdown',
                                    options=[{'label': feature, 'value': feature} for feature in completion_features],
                                    value=completion_features,
                                    multi=True,
                                    placeholder='Select completion features...'
                                )
                            ]
                        ),
                        html.Div(
                            style={'width': '48%'},
                            children=[
                                html.Label('Event Features:', style={'font-weight': 'bold'}),
                                dcc.Dropdown(
                                    id='event-features-dropdown',
                                    options=[{'label': feature, 'value': feature} for feature in event_features],
                                    value=event_features, 
                                    multi=True,
                                    placeholder='Select event features...'
                                )
                            ]
                        )
                    ]
                ),

                html.Div(
                    style={'display': 'flex', 'justify-content': 'space-between', 'margin-bottom': '20px'},
                    children=[
                        html.Div(
                            style={'width': '48%'},
                            children=[
                                html.Label('Main Features:', style={'font-weight': 'bold'}),
                                dcc.Dropdown(
                                    id='main-features-dropdown',
                                    options=[{'label': feature, 'value': feature} for feature in main_features],
                                    value=main_features,  # Select all main features by default
                                    multi=True,
                                    placeholder='Select main features...'
                                )
                            ]
                        ),
                        html.Div(
                            style={'width': '48%'},
                            children=[
                                html.Label('Additional Features:', style={'font-weight': 'bold'}),
                                dcc.Dropdown(
                                    id='additional-features-dropdown',
                                    options=[{'label': feature, 'value': feature} for feature in additional_features],
                                    value=additional_features,  # Select all additional features by default
                                    multi=True,
                                    placeholder='Select additional features...'
                                )
                            ]
                        )
                    ]
                ),

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
                                    value='DATE',  # Default to 'DATE'
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
                                    value='asc',  # Default to ascending
                                    labelStyle={'display': 'inline-block', 'margin-right': '10px'}
                                )
                            ]
                        )
                    ]
                )
            ]
        ),

        html.Div(
            style={'margin-top': '30px'},
            children=[
                dash_table.DataTable(
                    id='table',
                    columns=[], 
                    data=[],
                    page_size=10,
                    style_table={'overflowX': 'auto', 'border': '1px solid #ddd', 'border-radius': '8px'},
                    style_cell={'textAlign': 'left', 'padding': '10px'},
                    style_header={'fontWeight': 'bold', 'backgroundColor': '#f9f9f9'}
                ),
                html.Div(
                    style={'margin-top': '20px', 'text-align': 'center'},
                    children=[
                        html.Button('Download Filtered Data', id='download-button', n_clicks=0),
                        dcc.Download(id='download-csv')
                    ]
                )
            ]
        )
    ]
)

@app.callback(
    [Output('universal-dropdown', 'options'),
     Output('universal-dropdown', 'value'),
     Output('table', 'data'),
     Output('table', 'columns')],
    [Input('platform-dropdown', 'value'),
     Input('universal-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('completion-features-dropdown', 'value'),
     Input('event-features-dropdown', 'value'),
     Input('main-features-dropdown', 'value'),
     Input('additional-features-dropdown', 'value'),
     Input('sort-column-dropdown', 'value'),
     Input('sort-order-radio', 'value')]
)
def update_filters(selected_platforms, selected_universal, start_date, end_date, 
                   selected_completion, selected_event, selected_main, 
                   selected_additional, sort_column, sort_order):

    if not selected_platforms:
        return [], [], [], []

    filtered_df = df[df['Platform'].isin(selected_platforms)]
    if selected_universal:
        filtered_df = filtered_df[filtered_df['Universal'].isin(selected_universal)]
    filtered_df = filtered_df[(filtered_df['DATE'] >= start_date) & (filtered_df['DATE'] <= end_date)]

    columns_to_keep = ['DATE'] + additional + targets + ratios + selected_completion + selected_event + selected_main + selected_additional
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

    universal_options = [{'label': universal, 'value': universal} for universal in filtered_df['Universal'].unique()]
    if not set(selected_universal).issubset(set(filtered_df['Universal'].unique())):
        selected_universal = filtered_df['Universal'].unique()

    table_data = filtered_df.to_dict('records')
    table_columns = [{'name': col, 'id': col} for col in filtered_df.columns]

    return universal_options, selected_universal, table_data, table_columns

@app.callback(
    Output('download-csv', 'data'),
    Input('download-button', 'n_clicks'),
    State('platform-dropdown', 'value'),
    State('universal-dropdown', 'value'),
    State('date-picker-range', 'start_date'),
    State('date-picker-range', 'end_date'),
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

    filtered_df = df[df['Platform'].isin(selected_platforms)]
    if selected_universal:
        filtered_df = filtered_df[filtered_df['Universal'].isin(selected_universal)]
    filtered_df = filtered_df[(filtered_df['DATE'] >= start_date) & (filtered_df['DATE'] <= end_date)]

    columns_to_keep = ['DATE'] + additional + targets + ratios + selected_completion + selected_event + selected_main + selected_additional
    filtered_df = filtered_df[columns_to_keep]

    if sort_column and sort_order:
        filtered_df = filtered_df.sort_values(by=sort_column, ascending=(sort_order == 'asc'))

    # Apply formatting to downloaded file
    filtered_df['DATE'] = filtered_df['DATE'].dt.strftime('%d-%m-%Y')
    # if 'GAS' in filtered_df.columns:
    #     filtered_df['GAS'] = filtered_df['GAS'].round(2)
    # if 'WATER' in filtered_df.columns:
    #     filtered_df['WATER'] = filtered_df['WATER'].astype(int)
    # if 'OIL' in filtered_df.columns:
    #     filtered_df['OIL'] = filtered_df['OIL'].astype(int)

    csv_string = filtered_df.to_csv(index=False, encoding='utf-8')

    return dict(content=csv_string, filename='filtered_data.csv')

if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        webbrowser.open_new("http://127.0.0.1:8050/")
    app.run_server(debug=True)