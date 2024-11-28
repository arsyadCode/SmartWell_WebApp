import dash, os, webbrowser
from dash import dcc, html, Output, Input, State
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import ALL

# Initialize Dash app
app = dash.Dash(__name__, title="Smart Well Monitoring", suppress_callback_exceptions=True)
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
    html.Div(
        [
            dcc.Dropdown(
                id="well-dropdown",
                options=[{'label': well, 'value': well} for well in dropdown_options],
                value=dropdown_options[0],
                placeholder="Select a Well",
                style={'width': '40%'}
            ),
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
                inline=True
            )
        ],
        style={'display': 'flex', 'gap': '20px', 'margin': '20px'}
    ),
    html.Div(id="graphs-container", style={'margin': '20px'}),
])

# Function to create individual figures
def create_figure(x, y, x2, y2, ylabel, color):
    fig = go.Figure()

    # Add main data line
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode='lines',
        line=dict(color=color, width=1.5),
        name="Monthly production data"
    ))

    # Add test and sensor data
    fig.add_trace(go.Scatter(
        x=x2, y=y2,
        mode='markers',
        marker=dict(color='red', size=8),
        name="Test and sensor data"
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
     Input("figures-checklist", "value")]
)
def update_graphs(selected_well, selected_figures):
    selected_data = df[df['Universal'] == selected_well]
    selected_data2 = df2[df2['Universal'] == selected_well]
    plot_data = dfPlot[dfPlot['Universal'] == selected_well]

    figures = []

    if "Oil Rate" in selected_figures:
        fig = create_figure(
            selected_data['MDATE'], selected_data['OIL_per_day'],
            plot_data['DATE_STAMP'], plot_data['CORR_OIL_RATE_STBD'],
            "Oil Rate (bbl/d)", "darkgoldenrod"
        )
        figures.append(dcc.Graph(figure=fig))

    if "Water Rate" in selected_figures:
        fig = create_figure(
            selected_data['MDATE'], selected_data['WATER_per_day'],
            plot_data['DATE_STAMP'], plot_data['CORR_WTR_RATE_STBD'],
            "Water Rate (bbl/d)", "dodgerblue"
        )
        figures.append(dcc.Graph(figure=fig))

    if "Gas Rate" in selected_figures:
        fig = create_figure(
            selected_data['MDATE'], selected_data['GAS_per_day'],
            plot_data['DATE_STAMP'], plot_data['CORR_GAS_RES_RATE_MMSCFD'],
            "Gas Rate (mmscfd)", "darkturquoise"
        )
        figures.append(dcc.Graph(figure=fig))

    if "WHP Rate" in selected_figures:
        fig = create_figure(
            selected_data2['START_TIME'], selected_data2['WHP'],
            plot_data['DATE_STAMP'], plot_data['WHP_BARG'],
            "WHP Rate (barg)", "darkslateblue"
        )
        figures.append(dcc.Graph(figure=fig))

    if "WHT Rate" in selected_figures:
        fig = create_figure(
            selected_data2['START_TIME'], selected_data2['WHT'],
            plot_data['DATE_STAMP'], plot_data['WHT_DEG_C'],
            "WHT Rate (°C)", "darkslateblue"
        )
        figures.append(dcc.Graph(figure=fig))

    return figures

# Run Dash app
if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        webbrowser.open_new("http://127.0.0.1:8050/")
    app.run_server(debug=True, dev_tools_ui=False)