import dash, os, webbrowser
from dash import dcc, html, Input, Output, State, ALL
import RunAll_5PlotsData, RunHistoris
import dash_bootstrap_components as dbc
import base64, os
import pandas as pd

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title="Smart Well Monitoring", suppress_callback_exceptions=True)
server = app.server

excel_file = pd.ExcelFile("./Data/show_historicalData.xlsx")
df = pd.read_excel(excel_file, sheet_name="monthly_rate_per_day_combined")
df2 = pd.read_excel(excel_file, sheet_name="pi_sensor_per_month")
dfPlot = pd.read_excel(excel_file, sheet_name="plot_data")

df['MDATE'] = pd.to_datetime(df['MDATE'], format='%m/%d/%Y')
df2['START_TIME'] = pd.to_datetime(df2['START_TIME'], format='%Y-%m-%d')
dfPlot['DATE_STAMP'] = pd.to_datetime(dfPlot['DATE_STAMP'], format='%d/%m/%Y %H:%M')

dropdown_options = sorted(df['Universal'].unique())

app.layout = html.Div(style={'padding': 0, 'margin': 0}, children=[
    html.Div(id='page-content', style={'padding': 0, 'margin': 0}, children=[
        RunHistoris.app.layout,
    ]),
])

RunHistoris.callback(app)
RunAll_5PlotsData.callbacks(app)

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
    Output('page-content', 'children'),
    Input('plot-type', 'value')
)
def change_plot_type(plot_type):
    if plot_type == 'multi':
        return RunAll_5PlotsData.app.layout
    else:
        return RunHistoris.app.layout

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

if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        webbrowser.open_new("http://127.0.0.1:8050/")
    app.run_server(debug=True, dev_tools_ui=False)
