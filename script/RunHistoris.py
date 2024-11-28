import pandas as pd
import os, webbrowser
from dash import dcc, html, Input, Output, callback, Dash
import plotly.graph_objects as go

df = pd.read_csv("Data/monthly_rate_per_day_combined_with_pi.csv")
df['MDATE'] = pd.to_datetime(df['MDATE'], format='%m/%d/%Y')

app = Dash(__name__)
app.title = "Smart Well Monitoring - Universitas Pertamina"

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
    html.Div(
        [
            dcc.Dropdown(
                id='dropdown-well',
                options=[{'label': value, 'value': value} for value in sorted(df['Universal'].unique())],
                value=sorted(df['Universal'].unique())[0],
                placeholder="Select Well",
                clearable=True,
                style={"width": "50%"}
            ),
            dcc.Dropdown(
                id='dropdown-scale',
                options=[{'label': 'Linear', 'value': 'linear'}, {'label': 'Log', 'value': 'log'}],
                value='linear',
                placeholder="Select Y-Axis Scale",
                clearable=True,
                style={"width": "50%"}
            ),
        ],
        style={"display": "flex", "gap": "20px", "padding": "20px"}
    ),
    dcc.Graph(id='combined-graph', config={"displayModeBar": False}),
])

@app.callback(
    Output('combined-graph', 'figure'),
    [Input('dropdown-well', 'value'),
     Input('dropdown-scale', 'value')]
)
def update_graph(selected_well, y_axis_type):
    filtered_df = df[df['Universal'] == selected_well]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=filtered_df['MDATE'],
        y=filtered_df['OIL_per_day'],
        mode='lines',
        name='Oil Rate (stbd)(bbl/d)',
        line=dict(color='green', width=1.5),
        hovertemplate='Oil Rate: %{y:.2f} bbl/d<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=filtered_df['MDATE'],
        y=filtered_df['WATER_per_day'],
        mode='lines',
        name='Water Rate (stbd)(bbl/d)',
        line=dict(color='blue', width=1.5),
        hovertemplate='Water Rate: %{y:.2f} bbl/d<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=filtered_df['MDATE'],
        y=filtered_df['GAS_per_day'],
        mode='lines',
        name='Gas Rate (mmscfd)(cf/d)',
        line=dict(color='red', width=1.5),
        yaxis='y2',
        hovertemplate='Gas Rate: %{y:.2f} mmscfd<extra></extra>'
    ))

    fig.update_layout(
        xaxis=dict(title='Year'),
        yaxis=dict(title=y_axis_type + ' rate', type=y_axis_type),
        yaxis2=dict(title=y_axis_type + ' rate', overlaying='y', side='right', type=y_axis_type),
        legend=dict(orientation='h', x=0.5, xanchor='center', y=1.1),
        hovermode='x unified',
        template='simple_white',
        margin=dict(l=40, r=40, t=50, b=50),
    )

    return fig

if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        webbrowser.open_new("http://127.0.0.1:8050/")
    app.run_server(debug=True, dev_tools_ui=False)