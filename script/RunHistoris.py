import pandas as pd
import panel as pn
from bokeh.plotting import figure
from bokeh.models import Select, LinearAxis, Range1d, HoverTool, ColumnDataSource
from bokeh.layouts import column, row
from bokeh.models.formatters import DatetimeTickFormatter

# Load Bokeh and Panel extension
pn.extension()

# Read data
df = pd.read_csv("Data/monthly_rate_per_day_combined_with_pi.csv")
df['MDATE'] = pd.to_datetime(df['MDATE'], format='%m/%d/%Y')

# Paths to images
favicon = "img/SmartWell1co.ico"
phm_logo = "img/PHM.png"
logo = "img/SmartWell2-2.png"

# Create dropdown menu with unique 'Universal' column values
dropdown_options = sorted(df['Universal'].unique())
dropdown = Select(title="Well:", value=dropdown_options[0], options=dropdown_options)

# Create y-axis scale selection dropdown
scale_options = ['Linear', 'Log']
scale_dropdown = Select(title="Y-Axis Scale:", value=scale_options[0], options=scale_options)

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

# Create a single figure with multiple lines and secondary y-axis
def create_combined_figure(selected_data, y_axis_type):
    fig = figure(width=950, height=500, background_fill_color="#fafafa", x_axis_type='datetime', y_axis_type=y_axis_type)
    fig.xaxis.formatter = DatetimeTickFormatter(years="%Y")
    
    lines = {
        'OIL_per_day': {'color': 'green', 'legend_label': 'Oil Rate (stbd)(bbl/d)'},
        'WATER_per_day': {'color': 'blue', 'legend_label': 'Water Rate (stbd)(bbl/d)'}
    }
    
    for column, line_props in lines.items():
        source = ColumnDataSource(data={'x': selected_data['MDATE'], 'y': selected_data[column], 'name': [line_props['legend_label']] * len(selected_data)})
        fig.line('x', 'y', source=source, line_width=1.5, color=line_props['color'], alpha=1, legend_label=line_props['legend_label'])
    
    # Add secondary y-axis for Gas Rate
    fig.extra_y_ranges = {"gas_rate": Range1d(start=selected_data['GAS_per_day'].min(), end=selected_data['GAS_per_day'].max())}
    fig.add_layout(LinearAxis(y_range_name="gas_rate", axis_label="Gas Rate (mmscfd)(cf/d)"), 'right')
    source_gas = ColumnDataSource(data={'x': selected_data['MDATE'], 'y': selected_data['GAS_per_day'], 'name': ['Gas Rate (mmscfd)(cf/d)'] * len(selected_data)})
    fig.line('x', 'y', source=source_gas, line_width=1.5, color='red', alpha=1, legend_label='Gas Rate (mmscfd)(cf/d)', y_range_name="gas_rate")
    
    # Add Hover tool
    tooltips = [
        ("Date", "@x{%F}"),
        ("Value", "@y{0.000}"),
        ("Category", "@name")
    ]
    formatters = {
        '@x': 'datetime',
    }
    fig.add_tools(HoverTool(tooltips=tooltips, formatters=formatters, mode='vline'))
    
    fig.legend.click_policy = "hide"
    fig.grid.grid_line_color = None
    fig.xaxis.axis_label = 'Year'

    # Update y-axis label based on the scale
    if y_axis_type == 'linear':
        fig.yaxis.axis_label = 'Linear Scale'
    else:
        fig.yaxis.axis_label = 'Logarithmic Scale'
    
    return fig

# Callback function to update figures based on dropdown selection
def update_figures(attr, old, new):
    selected_data = df.loc[df['Universal'] == dropdown.value]
    # Convert the y-axis type to lowercase for Bokeh
    y_axis_type = scale_dropdown.value.lower()
    combined_figure = create_combined_figure(selected_data, y_axis_type)
    
    # Create layout
    layout = column(
        row(dropdown, scale_dropdown),
        combined_figure
    )
    
    # Update the panel
    dashboard[:] = [header, layout]

# Create the initial layout
initial_data = df.loc[df['Universal'] == dropdown.value]
combined_figure = create_combined_figure(initial_data, scale_dropdown.value.lower())

layout = column(
    row(dropdown, scale_dropdown),
    combined_figure
)

# Create the dashboard
dashboard = pn.Column(header, layout, sizing_mode="stretch_width")

# Register the callback function with the dropdown widgets
dropdown.on_change('value', update_figures)
scale_dropdown.on_change('value', update_figures)

# Serve the Panel dashboard on localhost
if __name__ == '__main__':
    pn.serve(dashboard.servable(), title=title, favicon=favicon)