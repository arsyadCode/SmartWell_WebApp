import pandas as pd
import panel as pn
from bokeh.plotting import figure
from bokeh.models import Select, CheckboxGroup
from bokeh.layouts import column, row
from bokeh.models.formatters import DatetimeTickFormatter

# Initialize Panel extension
pn.extension()

# Load data from CSV files
df = pd.read_csv("Data/monthly_rate_per_day_combined_with_pi.csv")
df2 = pd.read_csv("Data/pi_sensor_per_month.csv")
dfPlot = pd.read_csv("Data/combined_view.csv")

# Convert date columns to datetime format
df['MDATE'] = pd.to_datetime(df['MDATE'], format='%m/%d/%Y')
df2['START_TIME'] = pd.to_datetime(df2['START_TIME'], format='%Y-%m-%d')
dfPlot['DATE_STAMP'] = pd.to_datetime(dfPlot['DATE_STAMP'], format='%d/%m/%Y %H:%M')

# Paths to images
favicon = "img/SmartWell1co.ico"
phm_logo = "img/PHM.png"
logo = "img/SmartWell2-2.png"

# Create dropdown menu with unique 'Universal' column values
dropdown_options = sorted(df['Universal'].unique())
dropdown = Select(title="Well:", value=dropdown_options[0], options=dropdown_options)

# Create checkbox group for selecting figures
figures_checkbox = CheckboxGroup(labels=["All", "Oil Rate", "Water Rate", "Gas Rate", "WHP Rate", "WHT Rate"], active=[0])

# Define the header with logos and title
title = "Smart Well Monitoring - Universitas Pertamina"
header = pn.Row(
    pn.pane.PNG(logo, height=80, sizing_mode='stretch_width'),
    pn.layout.Spacer(),
    pn.pane.Str(f'<b style="color:#000000; font-family: Roboto">{title}</b>', styles={'font-size': '18pt', 'margin': 'auto', 'text-align': 'center'}, sizing_mode='stretch_width'),
    pn.layout.Spacer(),
    pn.pane.PNG(phm_logo, height=115, sizing_mode='stretch_width', link_url='https://phi.pertamina.com/'),
    styles=dict(background="#ffffff"),
    align="center",
    sizing_mode="stretch_width",
)

# Function to create a Bokeh figure
def create_figure(width, height, x, y, x2, y2, ylabel, color):
    fig = figure(width=width, height=height, background_fill_color="#fafafa")
    fig.line(x, y, line_width=1.5, color=color, alpha=1, legend_label="monthly production data")
    fig.scatter(x2, y2, marker='dot', size=15, color='red', alpha=1, legend_label="test and sensor data")
    fig.grid.grid_line_color = None
    fig.legend.click_policy = "hide"
    fig.xaxis.axis_label = 'Year'
    fig.yaxis.axis_label = ylabel
    fig.xaxis.formatter = DatetimeTickFormatter(years="%Y")
    return fig

# Callback function to update figures based on dropdown selection and checkbox status
def update_figures(attr, old, new):
    selected_data = df.loc[df['Universal'] == dropdown.value]
    selected_data2 = df2.loc[df2['Universal'] == dropdown.value]
    plot = dfPlot.loc[dfPlot['Universal'] == dropdown.value]

    # Ensure "All" checkbox behavior
    if 0 in figures_checkbox.active:
        if len(figures_checkbox.active) <= len(figures_checkbox.labels):
            figures_checkbox.active = list(range(len(figures_checkbox.labels)))
        else:
            figures_checkbox.active = [i for i in figures_checkbox.active if i != 0]
    else:
        figures_checkbox.active = [i for i in figures_checkbox.active if i != 0]

    # Initialize list to store selected figures
    selected_figures = []

    # Generate figures based on checkbox selection
    for i in figures_checkbox.active:
        if figures_checkbox.labels[i] == 'Oil Rate':
            figOil = create_figure(950, 225, selected_data['MDATE'], selected_data['OIL_per_day'],
                                   plot['DATE_STAMP'], plot['CORR_OIL_RATE_STBD'], 'Oil Rate', "darkgoldenrod")
            selected_figures.append(figOil)
        elif figures_checkbox.labels[i] == 'Water Rate':
            figWater = create_figure(950, 225, selected_data['MDATE'], selected_data['WATER_per_day'],
                                     plot['DATE_STAMP'], plot['CORR_WTR_RATE_STBD'], 'Water Rate', "dodgerblue")
            selected_figures.append(figWater)
        elif figures_checkbox.labels[i] == 'Gas Rate':
            figGas = create_figure(950, 225, selected_data['MDATE'], selected_data['GAS_per_day'],
                                   plot['DATE_STAMP'], plot['CORR_GAS_RES_RATE_MMSCFD'], 'Gas Rate', "darkturquoise")
            selected_figures.append(figGas)
        elif figures_checkbox.labels[i] == 'WHP Rate':
            figWHP = create_figure(950, 225, selected_data2['START_TIME'], selected_data2['WHP'],
                                   plot['DATE_STAMP'], plot['WHP_BARG'], 'WHP Rate', "darkslateblue")
            selected_figures.append(figWHP)
        elif figures_checkbox.labels[i] == 'WHT Rate':
            figWHT = create_figure(950, 225, selected_data2['START_TIME'], selected_data2['WHT'],
                                   plot['DATE_STAMP'], plot['WHT_DEG_C'], 'WHT Rate', "darkslateblue")
            selected_figures.append(figWHT)

    # Determine layout of figures
    num_selected_figures = len(selected_figures)
    num_cols = 2
    num_rows = (num_selected_figures + num_cols - 1) // num_cols

    # Create layout components
    layout_components = [row(dropdown, figures_checkbox)]
    start_idx = 0
    for row_idx in range(num_rows):
        row_figures = selected_figures[start_idx:start_idx+num_cols]
        layout_components.append(row(*row_figures, sizing_mode='stretch_width'))
        start_idx += num_cols

    # Update the Panel dashboard layout
    dashboard[:] = [header, column(*layout_components)]

# Initial layout
layout = row(dropdown, figures_checkbox)

# Create the Panel dashboard
dashboard = pn.Column(header, layout, sizing_mode="stretch_width")

# Register callback functions
dropdown.on_change('value', update_figures)
figures_checkbox.on_change('active', update_figures)

# Serve the Panel dashboard on localhost
if __name__ == '__main__':
    pn.serve(dashboard.servable(), title=title, favicon=favicon)