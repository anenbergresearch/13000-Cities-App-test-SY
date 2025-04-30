# Import necessary libraries
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import dash
import copy
import dash_bootstrap_components as dbc
from dash import callback, dcc, html
from dash.dependencies import Input, Output, State

# Import custom components
from components import buttons, const, data_prep

# Register the page for Dash
dash.register_page(__name__)

# Set default Plotly template
pio.templates.default = "simple_white"

# Load preprocessed data
df = data_prep.DFILT
fmean, fmax, fmin = data_prep.MEAN, data_prep.MAX, data_prep.MIN
fmean_v2, fmax_v2, fmin_v2 = data_prep.MEAN_V2, data_prep.MAX_V2, data_prep.MIN_V2







# === PAGE LAYOUT COMPONENTS ===
# Main graph and interactive components
main_graph = dcc.Graph(
    id='shaded-map',
    hoverData={'points': [{'customdata': 'United States'}]},
    style={"height": "650px",
           "border": "none",
            "boxShadow": "none",
            "outline": "none",
            "backgroundColor": "transparent"}
)

# Added version store for tracking active version
version_store = dcc.Store(id='country-version-store', data='1')

# Version selector component
version_selector = html.Div([
    html.H6("Data Version", style={
        'margin-bottom': '5px',
        'font-weight': 'bold',
        'color': '#000000',
        'font-size': '18px',
        'font-family': 'helvetica'
    }),
    html.Div([
        html.Div([
            html.Button(
                "Version 1",
                id="country-version-1-button",
                className="version-button active-version",
                n_clicks=0
            ),
            # Tooltip for Version 1
            dbc.Tooltip(
                "Version 1 displays estimates from several previous studies for each pollutant, using data available as of 2022 (see more details in [About])",
                target="country-version-1-button",
                placement="bottom",
                trigger="hover"
            )
        ], style={'display': 'inline-block'}),
        
        html.Div([
            html.Button(
                "Version 2",
                id="country-version-2-button",
                className="version-button",
                n_clicks=0
            ),
            # Tooltip for Version 2
            dbc.Tooltip(
                "Version 2 displays updated estimates for each pollutant from Kim et al. (2025) (see more details in [About])",
                target="country-version-2-button",
                placement="bottom",
                trigger="hover"
            )
        ], style={'display': 'inline-block'})
    ], className="version-button-group")
], className="control-group")

# Pollutant selector
pollutant_selector = html.Div([
    html.H6("Pollutant", style={
        'margin-bottom': '5px',
        'font-weight': 'bold',
        'color': '#000000',
        'font-size': '18px',
        'font-family': 'helvetica'
    }),
    html.Div([
        dbc.RadioItems(
            id="crossfilter-yaxis-columncountry",
            className="btn-group pollutant-radio-group",
            inputClassName="btn-check",
            labelClassName="btn btn-outline-secondary pollutant-button",
            labelCheckedClassName="btn btn-outline-secondary pollutant-button selected-button",
            options=[
                {"label": u'PM\u2082\u2085', "value": 'PM'},
                {"label": u'NO\u2082', "value": 'NO2'},
                {"label": u'O\u2083', "value": 'O3'},
                {"label": u'CO\u2082', "value": 'CO2'},
            ],
            value='PM',
            labelStyle={'display': 'inline-block', 'margin': '0', 'padding': '0'}
        )
    ], style={'fontSize': '0', 'display': 'flex', 'whiteSpace': 'nowrap'})
], className="control-group")

metrics = buttons.health_metrics('country')  # Using 'country' as a unique identifier

# Year dropdown
year_selector = html.Div([
    html.H6("Year", style={
        'margin-bottom': '5px',
        'font-weight': 'bold',
        'color': '#000000',
        'font-size': '18px',
        'font-family': 'helvetica'
    }),
    dcc.Dropdown(
        id='country-year-dropdown',
        options=[{'label': str(year), 'value': year} for year in sorted(df['Year'].unique())],
        value=df['Year'].max(),
        style={'color': '#123C69', 'font-size': '14px'},
        clearable=False
    )
], className="control-group")

# X-axis scale selector
lin_log = buttons.lin_log('country')

# Country dropdown
country_dropdown = html.Div([
    html.H6("Country", style={
        'margin-bottom': '5px',
        'font-weight': 'bold',
        'color': '#000000',
        'font-size': '18px',
        'font-family': 'helvetica'
    }),
    dcc.Dropdown(
        id='country-s',
        options=sorted(df["Country"].unique()),
        value='United States',
        style={'color': '#123C69', 'font-size': '14px'},
        clearable=False
    )
], className="control-group")

# City dropdown
city_dropdown = html.Div([
    html.H6("City", style={
        'margin-bottom': '5px',
        'font-weight': 'bold',
        'color': '#000000',
        'font-size': '18px',
        'font-family': 'helvetica'
    }),
    dcc.Dropdown(
        id='city-s',
        options=sorted(df["CityCountry"].unique()),
        value='Washington D.C., United States (860)',
        style={'color': '#123C69', 'font-size': '14px'}
    )
], className="control-group")











# Title section
title_section = dbc.Row([
    dbc.Col(width=2),
    dbc.Col(
        html.Div(
            style={
                'backgroundColor': const.DISP['background'], 
                'marginTop': '2rem',
                'textAlign': 'center',
                'display': 'flex',
                'flexDirection': 'column',
                'alignItems': 'center'
            }, 
            children=[
                html.H1(
                    children='Countrywide Summary', 
                    style={
                        'textAlign': 'center',
                        'color': 'black',
                        'fontFamily': 'Helvetica, Arial, sans-serif',
                        'fontWeight': 'bold',
                        'fontSize': '2.5rem',
                        'letterSpacing': '-0.05em',
                        'padding': '0.5rem 0',
                        'borderBottom': '3px solid rgba(0,0,0,0.1)',
                        'maxWidth': '800px',
                        'width': '100%'
                    }
                ),
                html.Div(
                    children='Exploring urban pollutions averaged at the country-level', 
                    style={
                        'textAlign': 'center',
                        'color': 'black',
                        'fontFamily': 'Helvetica, Arial, sans-serif',
                        'fontSize': '1rem',
                        'marginTop': '0.2rem',
                        'marginBottom': '2.5rem',
                        'maxWidth': '800px',
                        'width': '100%'
                    }
                )
            ]
        ),
        width=12,
        className="d-flex justify-content-center"
    )
], justify="center", align="center")

# Left column controls - Modified to make buttons fill the width
left_controls = html.Div([
    dbc.Row([
        dbc.Col(version_selector, lg=4, md=4, sm=12, style={"paddingRight": "2px", "paddingLeft": "2px"}),
        dbc.Col(pollutant_selector, lg=4, md=4, sm=12, style={"paddingRight": "2px", "paddingLeft": "2px"}),
        dbc.Col(metrics, lg=4, md=4, sm=12, style={"paddingRight": "2px", "paddingLeft": "2px"})
    ], className="mb-3", style={"marginLeft": "0", "marginRight": "0", "display": "flex", "flexWrap": "wrap"}),
    
    dbc.Row([
        dbc.Col(country_dropdown, lg=6, md=6, sm=12, style={"paddingRight": "5px", "paddingLeft": "5px"}),
        dbc.Col(year_selector, lg=6, md=6, sm=12, style={"paddingRight": "2px", "paddingLeft": "2px"}),
    ], className="mb-3", style={"marginLeft": "0", "marginRight": "0", "display": "flex", "flexWrap": "wrap"})
], className="control-panel", style={"padding": "15px", "display": "block"})

# Left column main content
left_main_content = html.Div([
    dbc.Row([
        dbc.Col(main_graph, width=12, className="dash-graph")
    ], style={"marginLeft": "0", "marginRight": "0"}),
    html.Div(style={"height": "20px"}),
    dbc.Row([
        dbc.Col(width=9),   
    ], style={"marginLeft": "0", "marginRight": "0",
              "border": "none",
        "boxShadow": "none",
        "outline": "none",
        "backgroundColor": "transparent"})
])

# Complete left column
left_column = dbc.Col([
    html.H4("Country Pollution Map", className="mb-3 mt-1 text-center",
            style={"color": "#123C69", "fontFamily": "Helvetica, Arial, sans-serif",
                  "fontWeight": "bold", "borderBottom": "2px solid #123C69",
                  "paddingBottom": "10px", "fontSize": "25px"}),
    left_controls,
    left_main_content
], lg=7, md=12, sm=12, className="pe-4 two-column-divider")


# Right column controls
right_controls = dbc.Row([
    dbc.Col(city_dropdown, lg=12, md=12, sm=12, style={"paddingRight": "5px", "paddingLeft": "5px"})
], className="mb-3")

right_controls_panel = html.Div([
    right_controls
], className="control-panel", style={"padding": "15px", "display": "block"})

# Graph stack
graph_stack = dbc.Stack([
    dcc.Graph(
        id='cities-scatter',
        style={"height": "400px", "maxHeight": "350px", "overflow": "hidden",
               "border": "none",
            "boxShadow": "none",
            "outline": "none",
            "backgroundColor": "transparent"}
    ),
    dbc.Row([
        dbc.Col(width=7),  # Empty space
        dbc.Col(lin_log, width=5, style={
            "paddingBottom": "15px",
            "display": "flex",
            "justifyContent": "flex-end"})
    ], className="g-0"),  # Remove gutters with g-0 class
    dcc.Graph(
        id='country-trends-graph',
        style={"height": "400px", "maxHeight": "350px", "overflow": "hidden",
               "border": "none",
            "boxShadow": "none",
            "outline": "none",
            "backgroundColor": "transparent"}
    ),
 
], gap=2)

# Right column main content
right_main_content = dbc.Row([
    dbc.Col(
        html.Div([
            graph_stack
        ], style={
            "height": "800px",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "space-between"
        }),
        width=12, 
        className="dash-graph"
    )
])

# Complete right column
right_column = dbc.Col([
    html.H4("Summary for selected country & city", className="mb-3 mt-1 text-center", 
            style={"color": "#123C69", "fontFamily": "Helvetica, Arial, sans-serif", 
                  "fontWeight": "bold", "borderBottom": "2px solid #123C69", 
                  "paddingBottom": "10px", "fontSize": "25px"}),
    right_controls_panel,
    right_main_content
], lg=5, md=12, sm=12, className="ps-4")

# Two-column section
two_column_section = dbc.Row([
    left_column,
    right_column
], className="mt-3", style={"height": "1000px"})

# Final layout
layout = dbc.Container([
    version_store,
    title_section,
    two_column_section
], fluid=True)







# === CALLBACKS ===

# Version button toggling
@callback(
    [Output("country-version-1-button", "className"),
     Output("country-version-2-button", "className"),
     Output("country-version-store", "data")],
    [Input("country-version-1-button", "n_clicks"),
     Input("country-version-2-button", "n_clicks")],
    [State("country-version-store", "data")]
)
def update_version_selection(v1_clicks, v2_clicks, current_version):
    ctx = dash.callback_context
    if not ctx.triggered:
        return "version-button active-version", "version-button", "1"
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == "country-version-1-button":
        return "version-button active-version", "version-button", "1"
    else:
        return "version-button", "version-button active-version", "2"

# Deactivates PAF, Cases, and Rates when CO2 is selected in either version
@callback(
    [Output('health-metricscountry','options'),
     Output('crossfilter-yaxis-columncountry','options')],
    [Input('crossfilter-yaxis-columncountry', 'value'),
    Input('health-metricscountry', 'value'),
    Input('country-version-store', 'data')],  # Updated ID
    prevent_initial_call=True
)
def update_dropdown_options(selected_pollutant, selected_metric, version):
    # Disable health metrics for CO2 or when in Version 2
    if selected_pollutant == 'CO2' or version == '2':
        metric_opts = buttons.metric_options(True)  # Disable non-concentration metrics
    else:
        metric_opts = buttons.metric_options(False)

    # Disable CO2 when a non-concentration metric is selected
    if selected_metric and selected_metric != 'Concentration':
        pol_opts = buttons.pol_options(True)  # Remove CO2
    else:
        pol_opts = buttons.pol_options(False)  # All pollutants allowed

    return metric_opts, pol_opts

# Reset health metrics when version changes
@callback(
    Output('health-metricscountry', 'value'),
    Input('country-version-store', 'data'),
    prevent_initial_call=True
)
def reset_health_metrics_on_version_change(version):
    if version == '2':
        return 'Concentration'
    return dash.no_update

# City dropdown population based on selected country
@callback(
    Output("city-s", "options"),
    Output("city-s", "value"),
    [Input("country-s", "value"),
     Input("cities-scatter", "hoverData")],  # Add hover data as input
    prevent_initial_call=True
)
def chained_callback_city(country, hover_data):
    # Get the trigger context
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    dff = copy.deepcopy(df)
    if country is not None:
        dff = dff.query("Country == @country")
    
    # Get all cities for the selected country
    city_options = sorted(dff["CityCountry"].unique())
    
    # Determine which city to select
    if trigger_id == "cities-scatter" and hover_data is not None:
        # If triggered by hovering on the scatter plot
        if 'points' in hover_data and len(hover_data['points']) > 0:
            if 'customdata' in hover_data['points'][0]:
                # Extract city name from hover data
                hovered_city = hover_data['points'][0]['customdata'][0]
                # Check if the hovered city is in the options
                if hovered_city in city_options:
                    return city_options, hovered_city
    
    # Default behavior when not triggered by hover or if hovered city isn't valid
    return city_options, city_options[0] if city_options else None


def get_version_data(version):
    if version == '1':
        return data_prep.DFILT, data_prep.MEAN, data_prep.MAX, data_prep.MIN
    else:  # version == '2'
        return data_prep.DFILT_V2, data_prep.MEAN_V2, data_prep.MAX_V2, data_prep.MIN_V2



# The main updates to countries.py focus on modifying the callbacks to properly use V2 data
# 1. Modify the update_graph function to properly handle versions
@callback(
    Output('shaded-map', 'figure'),
    [Input('crossfilter-yaxis-columncountry', 'value'),
     Input('country-year-dropdown', 'value'),
     Input('country-s','value'),
     Input('health-metricscountry','value'),
     Input('country-version-store', 'data')]
)
def update_graph(pollutant, year_value, countryS, metric, version):
    # Get appropriate datasets based on version
    DFILT_V, MEAN_V, MAX_V, MIN_V = get_version_data(version)
    
    # Get the column to plot based on version and metric
    plot_column = data_prep.get_column_name(version, metric, pollutant)
    
    # Force 'Concentration' metric for Version 2 (as it doesn't have health metrics)
    if version == '2':
        metric = 'Concentration'
    
    # Query data for the selected year
    m = MEAN_V.query('Year == @year_value').copy()
    
    # Set display units based on pollutant and version
    unit_s = pollutant
    
    # Format text and set color scale limits based on pollutant, metric and version
    if version == '1':
        if 'CO2' in plot_column:
            maxx = 4e6
            m['text'] = '<b>'+m['Country'] + '</b><br>'+const.UNITS['Concentration'][unit_s]+': '+ round((m[plot_column].astype(float)/1000000),3).astype(str) + 'M'
        else:
            m['text'] = '<b>'+m['Country'] + '</b><br>'+const.UNITS[metric][unit_s]+': '+ m[plot_column].round(2).astype(str)
            if plot_column == 'Cases_NO2':
                maxx = 500
            elif plot_column == 'Cases_PM':
                maxx = 300
            else:
                maxx = m[plot_column].max()
    else:  # version == '2'
        
        # Use V2-specific units and scale
        if plot_column == 'CO2_V2':
            m['text'] = '<b>'+m['Country'] + '</b><br>'+const.UNITS_V2['Concentration'][unit_s]+': '+ m[plot_column].round(2).astype(str)
            maxx = np.percentile(m[plot_column].dropna(), 90)  #max in the CO2 per capita axis: 90% percentile
        else:
            m['text'] = '<b>'+m['Country'] + '</b><br>'+const.UNITS_V2['Concentration'][unit_s]+': '+ m[plot_column].round(2).astype(str)
            maxx = m[plot_column].max()
    
    # Create the choropleth map
    fig = go.Figure(data=go.Choropleth(
        locations = m['Country'],
        locationmode = 'country names',
        customdata=m['Country'],
        z = m[plot_column],
        hovertext=m['text'],
        hoverinfo='text',
        colorscale=const.CS[metric],
        zmin=0,
        zmax=maxx
    ))
    
    # Add highlight for selected country
    ctry = m.query('Country ==@countryS')
    fig.add_traces(data=go.Choropleth(
        locations = ctry['Country'],
        locationmode = 'country names',
        z = ctry[plot_column],
        hoverinfo='skip',
        colorscale=const.CS[metric],
        zmin=0,
        zmax=maxx,
        marker = dict(
            line=dict(           # Fix: Use "line" not "ine"
                width=2.3,       # Increased width for better visibility
                color='#3d3d3d',   # White border that will contrast with any color
        ))))
    
    
    # Update layout
    fig.update_geos(showframe=False)
    fig.update_layout(
        legend_title_text='',
        paper_bgcolor=const.DISP['background'],
        plot_bgcolor=const.DISP['background'],
        margin={'l': 10, 'b': 10, 't': 10, 'r': 0},
        hovermode='closest',
        coloraxis_colorbar_x=-0.1,
        height=600,
        font=dict(
            size=const.FONTSIZE,
            family=const.FONTFAMILY
        ),
        geo=dict(
            showland=True,
            landcolor=const.MAP_COLORS['lake'],
            coastlinewidth=0,
            oceancolor=const.MAP_COLORS['ocean'],
            subunitcolor="rgb(255, 255, 255)",
            countrycolor=const.MAP_COLORS['land'],
            countrywidth=0.5,
            showlakes=True,
            lakecolor=const.MAP_COLORS['ocean'],
            showocean=True,
            showcountries=True,
            resolution=50,
        ),
    )
    
    return fig

# Updated callback for cities scatter plot
@callback(
    Output('cities-scatter', 'figure'),
    [
        Input('shaded-map', 'hoverData'),
        Input('crossfilter-yaxis-columncountry', 'value'),
        Input('crossfilter-xaxis-typecountry', 'value'),
        Input('country-year-dropdown', 'value'),
        Input('country-s', 'value'),
        Input('city-s', 'value'),
        Input('health-metricscountry', 'value'),
        Input('country-version-store', 'data')
    ]
)
def update_scatter_plot(hoverData, pollutant, xaxis_type, year_value, countryS, cityS, metric, version):
    # Get appropriate datasets
    DFILT_V, MEAN_V, MAX_V, MIN_V = get_version_data(version)
    
    # Force 'Concentration' metric for Version 2 (as it doesn't have health metrics)
    if version == '2' and metric != 'Concentration':
        metric = 'Concentration'
    
    # Get the column to plot
    plot_column = data_prep.get_column_name(version, metric, pollutant)
    
    # Get data for the selected country
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    country_name = hoverData['points'][0]['customdata'] if input_id == 'shaded-map' else countryS
    
    # Filter data for year and city
    dff = DFILT_V[DFILT_V['Country'] == country_name]
    dff = dff.query('Year == @year_value')
    city_df = dff.query('CityCountry == @cityS')
    
    # Set title and units based on version
    unit_s = pollutant
    title = '<b>{}</b>'.format(country_name)
    
    if metric == 'Concentration':
        units_display = const.UNITS[metric][unit_s]
    else:
        units_display = metric

    # Create scatter plot
    plot = []
    
    # Plot cities by C40 membership
    for i in const.COUNTRY_SCATTER:
        _c = dff.query('C40 == @i')
        if _c.empty:
            continue
            
        # Handle different hover data for Version 1 vs Version 2
        if version == '1' and metric != 'Concentration':
            # For Version 1 with health metrics, include PAF and Cases in hover
            customdata = np.stack((_c['CityCountry'], _c[pollutant], 
                                  _c.get(f'PAF_{pollutant}', np.zeros(len(_c))), 
                                  _c.get(f'Cases_{pollutant}', np.zeros(len(_c)))), axis=-1)
            hovertemplate = ("<b>%{customdata[0]}</b><br>" + 
                            'Population: %{x} <br>' + 
                            f"{const.UNITS['Concentration'][unit_s]}: " + '%{customdata[1]} <br>' + 
                            f"{const.UNITS['PAF'][unit_s]}: " + '%{customdata[2]} <br>' + 
                            f"{const.UNITS['Cases'][unit_s]}: " + '%{customdata[3]}')
        else:
            # For Version 2 or Concentration metric, simpler hover data
            customdata = np.stack((_c['CityCountry'], _c[plot_column]), axis=-1)
            
            if version == '1':
                hovertemplate = ("<b>%{customdata[0]}</b><br>" + 
                                'Population: %{x} <br>' + 
                                f"{const.UNITS['Concentration'][unit_s]}: " + '%{customdata[1]} <br>')
            else:  # version == '2'
                hovertemplate = ("<b>%{customdata[0]}</b><br>" + 
                                'Population: %{x} <br>' + 
                                f"{const.UNITS_V2['Concentration'][unit_s]}: " + '%{customdata[1]} <br>')
        
        # Add scatter trace
        plot.append(go.Scatter(
            name=const.COUNTRY_SCATTER[i]['name'],
            x=_c['Population'],
            y=_c[plot_column],
            mode='markers',
            customdata=customdata,
            hovertemplate=hovertemplate,
            marker={
                'color': const.COUNTRY_SCATTER[i]['color'],
                'symbol': const.COUNTRY_SCATTER[i]['symbol'],
                'line': dict(width=1, color=const.COUNTRY_SCATTER[i]['color'])
            }
        ))
    
    # Create the figure
    fig = go.Figure(data=plot)
    
    # Highlight selected city
    if not city_df.empty:
        fig.add_trace(
            go.Scattergl(
                mode='markers',
                x=city_df['Population'],
                y=city_df[plot_column],
                customdata=np.stack((city_df['CityCountry'], city_df[plot_column]), axis=-1),
                opacity=1,
                marker=dict(
                    symbol='circle-open-dot',
                    color='#FAED26',
                    size=10,
                    line=dict(width=2)
                ),
                showlegend=False,
                hoverinfo='skip'
            )
        )
    
    # Update layout
    if xaxis_type == 'Log':
        x_range = [0, 8] 
    else:
        x_range = [0, 50_000_000] 
        
    fig.update_xaxes(
        title='Population',
        type='linear' if xaxis_type == 'Linear' else 'log',
        range=x_range
    )
    
    fig.update_yaxes(title=units_display)
    
    fig.update_layout(
        height=325,
        margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
        hovermode='closest',
        legend_title_text='',
        legend_x=1,
        legend_y=0,
        paper_bgcolor=const.DISP['background'],
        plot_bgcolor=const.DISP['background'],
        font=dict(
            size=const.FONTSIZE,
            family=const.FONTFAMILY
        )
    )
    
    fig.add_annotation(
        x=0,
        y=0.9,
        xanchor='left',
        yanchor='bottom',
        xref='paper',
        yref='paper',
        showarrow=False,
        align='left',
        bgcolor='rgba(255, 255, 255, 0.5)',
        text=title,
        font=dict(size=12)
    )
    
    return fig














def create_time_series(city, means, title, cityname, axiscol_name, metric, units):
    fig = go.Figure()
    fig.update_layout(
        font=dict(
            size=const.FONTSIZE,
            family=const.FONTFAMILY
        )
    )
    
    fig.add_trace(go.Scatter(
        x=means.Year,
        y=means.Maximum,
        name='Maximum',
        marker={'color':'lightgray'},
        line={'color':'lightgray'},
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=means.Year,
        y=means[axiscol_name],
        name='Mean',
        marker={'color':'#4CB391'},
        line={'color':'#4CB391'},
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=means.Year,
        y=means.Minimum,
        name='Minimum',
        marker={'color':'lightgray'},
        line={'color':'lightgray'},
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=means.Year,
        y=city.round(decimals=2),
        name='Selected city',
        marker={'color':'#CC5500'},
        line={'color':'#CC5500'},
        showlegend=True
    ))
    
    fig.update_traces(mode='lines+markers')
    fig.update_layout(
        hovermode="x unified",
        paper_bgcolor=const.DISP['background'],
        plot_bgcolor=const.DISP['background'],
        legend=dict(y=1, x=1),
        height=325,
        margin={'l': 20, 'b': 30, 'r': 10, 't': 10}
    )
    
    if metric != 'Concentration':
        fig.update_yaxes(title=metric)
    else:
        fig.update_yaxes(title=const.UNITS[metric][units])
    
    return fig

# Function to create time series for Version 2 data
def create_time_series_v2(city, means, title, cityname, axiscol_name, units):
    """Create time series for Version 2 data with appropriate units"""
    fig = go.Figure()
    fig.update_layout(
        font=dict(
            size=const.FONTSIZE,
            family=const.FONTFAMILY
        )
    )
    
    fig.add_trace(go.Scatter(
        x=means.Year,
        y=means.Maximum,
        name='Maximum',
        marker={'color':'lightgray'},
        line={'color':'lightgray'},
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=means.Year,
        y=means[axiscol_name],
        name='Mean',
        marker={'color':'#4CB391'},
        line={'color':'#4CB391'},
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=means.Year,
        y=means.Minimum,
        name='Minimum',
        marker={'color':'lightgray'},
        line={'color':'lightgray'},
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=means.Year,
        y=city.round(decimals=2),
        name=cityname,
        marker={'color':'#CC5500'},
        line={'color':'#CC5500'},
        showlegend=True
    ))
    
    fig.update_traces(mode='lines+markers')
    fig.update_layout(
        hovermode="x unified",
        paper_bgcolor=const.DISP['background'],
        plot_bgcolor=const.DISP['background'],
        legend=dict(y=1, x=1),
        height=325,
        margin={'l': 20, 'b': 30, 'r': 10, 't': 10}
    )
    
    # Use V2-specific units
    units_display = const.UNITS_V2['Concentration'][units]
    fig.update_yaxes(title=units_display)
    
    return fig


# Updated callback for country trends graph
@callback(
    Output('country-trends-graph', 'figure'),
    [
        Input('cities-scatter', 'hoverData'),
        Input('country-s', 'value'),
        Input('crossfilter-yaxis-columncountry', 'value'),
        Input('city-s', 'value'),
        Input('health-metricscountry', 'value'),
        Input('country-version-store', 'data')
    ]
)
def update_timeseries(cityName, country_name, pollutant, cityS, metric, version):
    # Get appropriate datasets
    DFILT_V, MEAN_V, MAX_V, MIN_V = get_version_data(version)
    
    # Force 'Concentration' metric for Version 2 (as it doesn't have health metrics)
    if version == '2' and metric != 'Concentration':
        metric = 'Concentration'
    
    # Handle city selection from hover data
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if input_id == 'cities-scatter' and cityName and 'points' in cityName and len(cityName['points']) > 0:
        if 'customdata' in cityName['points'][0] and len(cityName['points'][0]['customdata']) > 0:
            city_sel = cityName['points'][0]['customdata'][0]
        else:
            city_sel = cityS
    else:
        city_sel = cityS
    
    # Get column to plot
    plot_column = data_prep.get_column_name(version, metric, pollutant)
    units = pollutant
    
    # Get data for selected city
    city = DFILT_V[DFILT_V.CityCountry == city_sel][plot_column]
    
    # Get country data
    _df = MEAN_V[MEAN_V['Country'] == country_name][['Year', plot_column]]
    _df['Minimum'] = MIN_V[MIN_V['Country'] == country_name][plot_column]
    _df['Maximum'] = MAX_V[MAX_V['Country'] == country_name][plot_column]
    
    # Create time series based on version
    if version == '1':
        return create_time_series(city, _df, country_name, city_sel, plot_column, metric, units)
    else:
        # Create a modified version of create_time_series for Version 2 data
        return create_time_series_v2(city, _df, country_name, city_sel, plot_column, units)

# Modified callback for city dropdown
@callback(
    Output("city-s", "options", allow_duplicate=True),
    Output("city-s", "value", allow_duplicate=True),
    [Input("country-s", "value"),
     Input('country-version-store', 'data')],
    prevent_initial_call=True
)
def update_city_dropdown(country, version):
    # Get appropriate dataset
    DFILT_V, _, _, _ = get_version_data(version)
    
    # Filter cities for selected country
    if country is not None:
        dff = DFILT_V.query("Country == @country")
    else:
        dff = DFILT_V
        
    # Return sorted list of cities and select first one
    cities = sorted(dff["CityCountry"].unique())
    return cities, cities[0] if cities else None

@callback(
    Output('health-metricscountry', 'options', allow_duplicate=True),
    Output('health-metricscountry', 'value', allow_duplicate=True),
    Input('country-version-store', 'data'),
    prevent_initial_call=True
)
def update_metrics_for_version(version):
    if version == '2':
        # Version 2 only has concentration data
        return [{"label": "Concentration", "value": "Concentration"}], "Concentration"
    else:
        # Version 1 has all metrics
        return buttons.metric_options(False), dash.no_update
    
@callback(
    Output("country-s", "value"),
    Input("country-s", "value"),
    Input('shaded-map', 'hoverData')
)
def sync_input(city_sel, hoverData):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    value = hoverData['points'][0]['customdata'] if input_id == 'shaded-map' else city_sel
    return value
