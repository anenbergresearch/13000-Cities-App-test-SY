

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, callback, dcc, html
import dash_bootstrap_components as dbc 
from dash.dependencies import Input, Output, State
import dash
from components import buttons, const, data_prep

dash.register_page(__name__)

countries = ['United States', 'China', 'India']
feature_id = {'China': 'properties.NAME_1', 'India': 'properties.st_nm'}

# Import dictionary with geojson of states
states_df = data_prep.STATES_DF

# Import dictionary with state applied dataframes
df = data_prep.DF

# Import dictionary with mean region values of pollutants
mean_df = data_prep.MEAN_DF

# Import dataframe with stats for each state
stats = data_prep.STATS
c_gjson = data_prep.GJSON

# Added version store for tracking active version
version_store = dcc.Store(id='state-version-store', data='1')

# Add support for version 2 data
stats_v2 = data_prep.STATS_V2 if hasattr(data_prep, 'STATS_V2') else stats
df_v2 = data_prep.DF_V2 if hasattr(data_prep, 'DF_V2') else df
mean_df_v2 = data_prep.MEAN_DF_V2 if hasattr(data_prep, 'MEAN_DF_V2') else mean_df

# Set up UI components with unique IDs for states page
metrics = buttons.health_metrics('state')

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
                id="state-version-1-button",
                className="version-button active-version",
                n_clicks=0
            ),
            # Tooltip for Version 1
            dbc.Tooltip(
                "Version 1 displays estimates from several previous studies for each pollutant, using data available as of 2022 (see more details in [About])",
                target="state-version-1-button",
                placement="bottom",
                trigger="hover"
            )
        ], style={'display': 'inline-block'}),
        
        html.Div([
            html.Button(
                "Version 2",
                id="state-version-2-button",
                className="version-button",
                n_clicks=0
            ),
            # Tooltip for Version 2
            dbc.Tooltip(
                "Version 2 displays updated estimates for each pollutant from Kim et al. (2025) (see more details in [About])",
                target="state-version-2-button",
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
            id="crossfilter-yaxis-columnstate",
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

# X-axis scale selector
lin_log = buttons.lin_log('state')

# Region selector
region_selector = html.Div([
    html.H6("Country", style={
        'margin-bottom': '5px',
        'font-weight': 'bold',
        'color': '#000000',
        'font-size': '18px',
        'font-family': 'helvetica'
    }),
    dcc.Dropdown(
        id='region-selection',
        options=[{'label': country, 'value': country} for country in countries],
        value='United States',
        style={
            'color': '#123C69', 
            'font-size': '14px'
        },
        clearable=False
    )
], className="control-group")

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
        id='state-year-dropdown',
        options=[{'label': str(year), 'value': year} for year in sorted(df['United States']['Year'].unique())],
        value=df['United States']['Year'].max(),
        style={'color': '#123C69', 'font-size': '14px'},
        clearable=False
    )
], className="control-group")

# State dropdown
state_dropdown = html.Div([
    html.H6("State/province", style={
        'margin-bottom': '5px',
        'font-weight': 'bold',
        'color': '#000000',
        'font-size': '18px',
        'font-family': 'helvetica'
    }),
    dcc.Dropdown(
        id='state-s',
        options=sorted(states_df['United States']['State'].unique()),
        value='CA',
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
        id='city-sel',
        options=sorted(df['United States']["CityID"].unique()),
        value='Honolulu (1)',
        style={'color': '#123C69', 'font-size': '14px'}
    )
], className="control-group")

# Define graphs
main_graph = dcc.Graph(
    id='shaded-states',
    hoverData={'points': [{'customdata': 'CA'}]},
    style={"height": "650px", 
           "border": "none",
            "boxShadow": "none",
            "outline": "none",
            "backgroundColor": "transparent"}
)












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
                    children='Sub-national Level Summary', 
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
                    children='Exploring urban pollutions averaged at the state- or province-level in the United States, China, and India', 
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

# Left column controls
left_controls = html.Div([
    # First row: Version, Pollutant, Metrics
    dbc.Row([
        dbc.Col(version_selector, lg=4, md=4, sm=12, style={"paddingRight": "2px", "paddingLeft": "2px"}),
        dbc.Col(pollutant_selector, lg=4, md=4, sm=12, style={"paddingRight": "2px", "paddingLeft": "2px"}),
        dbc.Col(metrics, lg=4, md=4, sm=12, style={"paddingRight": "2px", "paddingLeft": "2px"}),
    ], className="mb-3", style={"marginLeft": "0", "marginRight": "0", "display": "flex", "flexWrap": "wrap"}),
    
    # Second row: Region, Year
    dbc.Row([
        dbc.Col(region_selector, lg=4, md=4, sm=12, style={"paddingRight": "2px", "paddingLeft": "2px"}),
        dbc.Col(state_dropdown, lg=4, md=4, sm=12,style={"paddingRight": "2px", "paddingLeft": "2px"}),
        dbc.Col(year_selector, lg=4, md=4, sm=12, style={"paddingRight": "2px", "paddingLeft": "2px"}),
    ], className="mb-3", style={"marginLeft": "0", "marginRight": "0", "display": "flex", "flexWrap": "wrap"}),
])

# Left column main content
left_main_content = html.Div([
    dbc.Row([
        dbc.Col(main_graph, width=12, className="dash-graph")
    ], style={"marginLeft": "0", "marginRight": "0"}),
    html.Div(style={"height": "20px"}),
    dbc.Row([
        dbc.Col(width=9),   
    ], className="g-0")
])

# Complete left column
left_column = dbc.Col([
    html.H4("State/province Pollution Map", className="mb-3 mt-1 text-center",
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

graph_stack = dbc.Stack([
    dcc.Graph(
        id='states-scatter',
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
        id='State-trends-graph',
        style={"height": "400px", "maxHeight": "350px", "overflow": "hidden",
               "border": "none",
            "boxShadow": "none",
            "outline": "none",
            "backgroundColor": "transparent"}
    )
], gap=2)  # Add gap between graphs

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
    html.H4("Summary for selected state/province & city", className="mb-3 mt-1 text-center", 
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
    # Add version store to layout
    version_store,
    # Title section
    title_section,
    # Two-column section with all controls and graphs
    two_column_section
], fluid=True)










# Helper function to get version-specific data
def get_version_data(version, region):
    """Get the appropriate data based on version selection"""
    if version == '1':
        return df[region], stats[region], mean_df[region]
    else:  # version == '2'
        # Handle cases where V2 data might not exist or have different structure
        df_v = df_v2.get(region, df[region]) if hasattr(data_prep, 'DF_V2') else df[region]
        stats_v = stats_v2.get(region, stats[region]) if hasattr(data_prep, 'STATS_V2') else stats[region]
        mean_v = mean_df_v2.get(region, mean_df[region]) if hasattr(data_prep, 'MEAN_DF_V2') else mean_df[region]
        return df_v, stats_v, mean_v


# Update state dropdown based on selected region and version
@callback(
    Output("state-s", "options"),
    Output("state-s", 'value', allow_duplicate=True),
    [Input("region-selection", "value"),
     Input("state-version-store", "data")],
    prevent_initial_call=True
)
def chained_callback_state(country, version):
    # Get appropriate dataset based on version
    df_data, _, _ = get_version_data(version, country)
    
    return sorted(df_data['State'].dropna().unique()), sorted(df_data['State'].unique())[0]

# Update city dropdown based on selected state and version
@callback(
    Output("city-sel", "options"),
    Output("city-sel", 'value', allow_duplicate=True),
    [Input("region-selection", "value"),
     Input("state-s", "value"),
     Input("state-version-store", "data")],
    prevent_initial_call=True
)
def chained_callback_city(country, state, version):
    # Get appropriate dataset based on version
    df_data, _, _ = get_version_data(version, country)
    
    l = df_data[df_data['State'] == state]
    return sorted(l['CityID'].unique()), sorted(l['CityID'].unique())[0]

# Version button toggling (based on countries.py)
@callback(
    [Output("state-version-1-button", "className"),
     Output("state-version-2-button", "className"),
     Output("state-version-store", "data")],
    [Input("state-version-1-button", "n_clicks"),
     Input("state-version-2-button", "n_clicks")],
    [State("state-version-store", "data")]
)
def update_version_selection(v1_clicks, v2_clicks, current_version):
    ctx = dash.callback_context
    if not ctx.triggered:
        return "version-button active-version", "version-button", "1"
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == "state-version-1-button":
        return "version-button active-version", "version-button", "1"
    else:
        return "version-button", "version-button active-version", "2"

# Update year dropdown options based on region and version
@callback(
    Output("state-year-dropdown", "options"),
    Output("state-year-dropdown", "value"),
    [Input("region-selection", "value"),
     Input("state-version-store", "data")],
    prevent_initial_call=True
)
def update_year_dropdown(country, version):
    # Get appropriate dataset based on version
    df_data, _, _ = get_version_data(version, country)
    
    years = sorted(df_data['Year'].unique())
    return [{'label': str(year), 'value': year} for year in years], max(years)

# Reset health metrics when version changes
@callback(
    Output('health-metricsstate', 'value'),
    Input('state-version-store', 'data'),
    prevent_initial_call=True
)
def reset_health_metrics_on_version_change(version):
    if version == '2':
        return 'Concentration'
    return dash.no_update

# Deactivates PAF, Cases, and Rates when CO2 is selected in either version
@callback(
    [Output('health-metricsstate','options'),
     Output('crossfilter-yaxis-columnstate','options')],
    [Input('crossfilter-yaxis-columnstate', 'value'),
    Input('health-metricsstate', 'value'),
    Input('state-version-store', 'data')],  # Updated ID
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





##Function to create main map of shaded states and update based on selections
@callback(
    Output('shaded-states', 'figure'),
    [Input('region-selection', 'value'),
     Input('crossfilter-yaxis-columnstate', 'value'),
     Input('state-year-dropdown', 'value'),
     Input('state-s', 'value'),
     Input('health-metricsstate', 'value'),
     Input('state-version-store', 'data')]
)
def update_map(region, pollutant, year_value, state, metric, version):
    # Force 'Concentration' metric for Version 2 (as it doesn't have health metrics)
    if version == '2' and metric != 'Concentration':
        metric = 'Concentration'
    
    # Get plot column based on version
    plot_column = data_prep.get_column_name(version, metric, pollutant)
    
    # Get data for selected year
    df_data, stats_data, _ = get_version_data(version, region)
    m = stats_data['mean'].query('Year == @year_value').copy()
    st = m.query('State == @state')
    
    unit_s = pollutant
    
    # Set appropriate units and formatting based on version
    if version == '1':
        # Version 1 formatting
        if 'CO2' in plot_column:
            if 'w_' in plot_column:  # We're not using this anymore but kept for compatibility
                maxx = 50e6
            else:
                maxx = 7e6
            m['text'] = '<b>' + m['State'] + '</b><br>' + const.UNITS[metric][unit_s] + ': ' + \
                        round((m[plot_column].astype(float) / 1000000), 3).astype(str) + 'M'
        else:
            m['text'] = '<b>' + m['State'] + '</b><br>' + const.UNITS[metric][unit_s] + ': ' + \
                        m[plot_column].round(2).astype(str)
            if plot_column == 'Cases_NO2':
                maxx = 1980
            elif plot_column == 'Cases_PM':
                maxx = 250
            elif plot_column == 'Cases_O3':
                maxx = 110
            else:
                maxx = m[plot_column].max()
    else:
        # Version 2 formatting (similar to countries.py)
        units_label = const.UNITS_V2['Concentration'][unit_s] if hasattr(const, 'UNITS_V2') else const.UNITS['Concentration'][unit_s]
        
        if 'CO2' in plot_column:
            m['text'] = '<b>' + m['State'] + '</b><br>' + units_label + ': ' + \
                        m[plot_column].round(2).astype(str)
            maxx = np.percentile(m[plot_column].dropna(), 90)  # 90th percentile
        else:
            m['text'] = '<b>' + m['State'] + '</b><br>' + units_label + ': ' + \
                        m[plot_column].round(2).astype(str)
            maxx = m[plot_column].max()
    
    # Create choropleth map
    if region == 'United States':  #No outside geojson for USA so plot with plotly's internal USA-states locations
        fig = go.Figure(data=go.Choropleth(
            locations=m['State'], locationmode='USA-states', customdata=m['State'],
            z=m[plot_column], hovertext=m['text'], hoverinfo='text',
            colorscale=const.CS[metric], zmin=0, zmax=maxx, 
        ))
        fig.add_traces(data=go.Choropleth(
            locations=st['State'], locationmode='USA-states',
            z=st[plot_column], hoverinfo='skip',
            colorscale=const.CS[metric],
            marker=dict(line_width=3), zmin=0, zmax=maxx, 
        ))
        fig.update_geos(scope='usa')
        
    else:  ##Use the uploaded geojson files for China and India states
        fig = go.Figure(data=go.Choropleth(
            locations=m["State"], geojson=c_gjson[region], z=m[plot_column],
            hovertext=m['text'], featureidkey=feature_id[region], hoverinfo='text',
            colorscale=const.CS[metric], zmin=0, zmax=maxx
        ))
        fig.add_traces(data=go.Choropleth(
            locations=st['State'], geojson=c_gjson[region], featureidkey=feature_id[region],
            z=st[plot_column], hoverinfo='skip',
            colorscale=const.CS[metric], zmin=0, zmax=maxx,
            marker=dict(line_width=3)
        ))
        fig.update_geos(fitbounds='locations', visible=False)
    
    fig.update_layout(
        legend_title_text='',
        margin={'l': 10, 'b': 10, 't': 10, 'r': 0},
        hovermode='closest',
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
            bgcolor='#f5f5f5',  
        ),
    )
    fig.update_traces(customdata=m['State'])
    fig.update_yaxes(title=plot_column)
    
    return fig










@callback(
    Output('states-scatter', 'figure'),
    [Input('region-selection', 'value'),
     Input('shaded-states', 'hoverData'),
     Input('crossfilter-yaxis-columnstate', 'value'),
     Input('crossfilter-xaxis-typestate', 'value'),
     Input('state-year-dropdown', 'value'),
     Input('state-s', 'value'),
     Input('city-sel', 'value'),
     Input('health-metricsstate', 'value'),
     Input('state-version-store', 'data')]
)
def update_scatter_plot(region, hoverData, pollutant, xaxis_type, year_value, stateS, cityS, metric, version):
    # Force 'Concentration' metric for Version 2 (as it doesn't have health metrics)
    if version == '2' and metric != 'Concentration':
        metric = 'Concentration'
    
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    state_name = hoverData['points'][0]['customdata'] if input_id == 'shaded-states' else stateS
    
    # Get appropriate dataset based on version
    df_data, _, _ = get_version_data(version, region)
    
    dff = df_data[df_data['State'] == state_name]
    dff = dff.query('Year == @year_value')
    city_df = dff.query('CityID == @cityS')
    
    # Get column to plot
    unit_s = pollutant
    plot_column = data_prep.get_column_name(version, metric, pollutant)
    
    # Get appropriate units based on version
    if version == '1':
        units_label = const.UNITS[metric][unit_s]
    else:  # version == '2'
        units_label = const.UNITS_V2['Concentration'][unit_s] if hasattr(const, 'UNITS_V2') else const.UNITS['Concentration'][unit_s]
    
    title = '<b>{}</b>'.format(state_name)

    
    # Create scatter plot for all cities in the state grouped by C40 status
    plot = []
    
    # Process all cities regardless of C40 status
    for i in const.COUNTRY_SCATTER:
        # Filter cities for this C40 category
        _c = dff.query('C40 == @i')
        
        if not _c.empty:
            # Create different hover templates based on version and metric
            if version == '1' and unit_s != 'CO2' and metric != 'Concentration':
                # For Version 1 with health metrics, include PAF and Cases
                customdata = np.stack((_c['CityID'], _c[unit_s], 
                                     _c.get(f'PAF_{unit_s}', np.zeros(len(_c))), 
                                     _c.get(f'Cases_{unit_s}', np.zeros(len(_c)))), axis=-1)
                
                hover_template = ("<b>%{customdata[0]}</b><br>" + 
                                'Population: %{x} <br>' + 
                                f"{const.UNITS['Concentration'][unit_s]}: " + '%{customdata[1]} <br>' + 
                                f"{const.UNITS['PAF'][unit_s]}: " + '%{customdata[2]} <br>' + 
                                f"{const.UNITS['Cases'][unit_s]}: " + '%{customdata[3]}')
            else:
                # For Version 2 or Concentration metric, simpler hover data
                customdata = np.stack((_c['CityID'], _c[plot_column]), axis=-1)
                hover_template = ("<b>%{customdata[0]}</b><br>" + 
                                'Population: %{x} <br>' + 
                                f"{units_label}: " + '%{customdata[1]} <br>')
            
            # Add scatter trace for this group
            plot.append(go.Scatter(
                name=const.COUNTRY_SCATTER[i]['name'],
                x=_c['Population'],
                y=_c[plot_column],
                mode='markers',
                customdata=customdata,
                hovertemplate=hover_template,
                marker={
                    'color': const.COUNTRY_SCATTER[i]['color'],
                    'symbol': const.COUNTRY_SCATTER[i]['symbol'],
                    'size': 8,
                    'line': dict(width=1, color=const.COUNTRY_SCATTER[i]['color'])
                }
            ))
    
    # Create figure with the scatter plots
    fig = go.Figure(data=plot)
    
    # Add highlighted point for selected city
    if not city_df.empty:
        fig.add_trace(
            go.Scattergl(
                mode='markers',
                x=city_df['Population'],
                y=city_df[plot_column],
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

    # Set axis properties
    if xaxis_type == 'Log':
        x_range = [0, 8] 
    else:
        x_range = [0, 50_000_000]
            
    fig.update_xaxes(
        title='Population', 
        type='linear' if xaxis_type == 'Linear' else 'log',
        range=x_range if xaxis_type == 'Log' else None
    )
    fig.update_yaxes(title=metric if metric != 'Concentration' else units_label)
    
    # Add title annotation
    fig.add_annotation(
        x=0, y=0.9,
        xanchor='left', yanchor='bottom',
        xref='paper', yref='paper',
        showarrow=False, align='left',
        bgcolor='rgba(255, 255, 255, 0.5)',
        text=title,
        font=dict(size=12)
    )
    
    # Update layout
    fig.update_layout(
        height=325,
        margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
        hovermode='closest',
        legend_title_text='',
        legend=dict(x=1, y=0),
        paper_bgcolor=const.DISP['background'],
        plot_bgcolor=const.DISP['background'],
        font=dict(
            size=const.FONTSIZE,
            family=const.FONTFAMILY
        )
    )
    
    return fig








def create_time_series(region, city, means, title, cityname, axiscol_name, metric, version):
    """Create time series plot showing state and country data"""
    # Setup
    dec = 0 if axiscol_name == 'CO2' else 2
    
    # Get column name and units based on version
    if version == '1':
        plot_column = axiscol_name if metric == 'Concentration' else f"{metric}_{axiscol_name}"
        units_label = const.UNITS[metric][axiscol_name]
    else:
        plot_column = data_prep.V2_COLUMN_MAPPING.get(axiscol_name, axiscol_name + '_V2')
        units_label = const.UNITS_V2['Concentration'][axiscol_name] if hasattr(const, 'UNITS_V2') else const.UNITS['Concentration'][axiscol_name]
    
    # Create figure with all traces
    fig = go.Figure([
        # State maximum
        go.Scatter(x=means.Year, y=means.Maximum.round(decimals=dec), name='State maximum', 
                 marker={'color': 'lightgray'}, line={'color': 'lightgray'}, showlegend=True),
        
        # State mean
        go.Scatter(x=means.Year, y=means[plot_column].round(decimals=dec), name='State mean',
                 marker={'color': '#4CB391'}, line={'color': '#4CB391'}, showlegend=True),
        
        # State minimum
        go.Scatter(x=means.Year, y=means.Minimum.round(decimals=dec), name='State minimum',
                 marker={'color': 'lightgray'}, line={'color': 'lightgray'}, showlegend=True),
        
        # Selected city
        go.Scatter(x=means.Year, y=city.round(decimals=dec), name='Selected city',
                 marker={'color': '#CC5500'}, line={'color': '#CC5500'}, showlegend=True)
    ])
    
    # Add country mean if available
    _, _, mean_data = get_version_data(version, region)
    if plot_column in mean_data.columns:
        fig.add_trace(go.Scatter(
            x=mean_data.Year, y=mean_data[plot_column].round(decimals=dec), name='Country mean',
            marker={'color': 'black'}, line={'color': 'black', 'dash': 'dot'}, showlegend=True
        ))

    # Set common trace and layout properties
    fig.update_traces(mode='lines+markers', hovertemplate='%{y:,}')
    
    fig.update_layout(
        hovermode="x unified",
        paper_bgcolor=const.DISP['background'],
        plot_bgcolor=const.DISP['background'],
        legend=dict(y=1, x=1),
        height=325,
        margin={'l': 20, 'b': 30, 'r': 10, 't': 10},
        font=dict(size=const.FONTSIZE, family=const.FONTFAMILY),
        yaxis_title=units_label
    )
    
    return fig

@callback(
    Output('State-trends-graph', 'figure'),
    [Input('region-selection', 'value'),
     Input('states-scatter', 'hoverData'),
     Input('crossfilter-yaxis-columnstate', 'value'),
     Input('city-sel', 'value'),
     Input("state-s", "value"),
     Input('health-metricsstate', 'value'),
     Input('state-version-store', 'data')]
)
def update_timeseries(region, cityName, pollutant, cityS, stateS, metric, version):
    # Force 'Concentration' metric for Version 2
    if version == '2' and metric != 'Concentration':
        metric = 'Concentration'
    
    # Get city selection from hover data if available
    ctx = dash.callback_context
    city_sel = cityS
    if ctx.triggered[0]["prop_id"].split(".")[0] == 'states-scatter':
        if cityName and 'points' in cityName and 'customdata' in cityName['points'][0]:
            city_sel = cityName['points'][0]['customdata'][0]
    
    try:
        # Get data based on version
        df_data, stats_data, _ = get_version_data(version, region)
        
        # Get column name based on version and metric
        plot_column = data_prep.get_column_name(version, metric, pollutant)
        
        # Get state data
        state_data = stats_data['mean'][stats_data['mean']['State'] == stateS]
        if state_data.empty or plot_column not in state_data.columns:
            raise ValueError(f"No data for {stateS} or column {plot_column}")
        
        _df = state_data[['Year', plot_column]].copy()
        _df['Minimum'] = stats_data['min'][stats_data['min']['State'] == stateS][plot_column]
        _df['Maximum'] = stats_data['max'][stats_data['max']['State'] == stateS][plot_column]
        
        # Get city data
        city = pd.Series()
        city_rows = df_data[df_data.CityID == city_sel]
        if not city_rows.empty and plot_column in city_rows.columns:
            city = city_rows[plot_column]
        
        # Create the time series
        return create_time_series(region, city, _df, stateS, city_sel, pollutant, metric, version)
            
    except Exception as e:
        # Return empty figure with error message
        fig = go.Figure()
        units_label = const.UNITS[metric][pollutant] if version == '1' else const.UNITS_V2['Concentration'][pollutant]
        
        fig.update_layout(
            height=325,
            paper_bgcolor=const.DISP['background'],
            plot_bgcolor=const.DISP['background'],
            margin={'l': 20, 'b': 30, 'r': 10, 't': 10},
            font=dict(size=const.FONTSIZE, family=const.FONTFAMILY),
            xaxis_title="Year",
            yaxis_title=units_label
        )
        
        fig.add_annotation(
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            xref='paper', yref='paper', showarrow=False,
            text=f"No data available for {stateS}",
            font=dict(size=14, color='gray')
        )
        
        return fig
##Sync the states selected by hover with the dropdown menu
@callback(
    Output("state-s", "value"),
    Input("state-s", "value"),
    Input('shaded-states', 'hoverData'),
)
def sync_input(state_sel, hoverData):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    value = hoverData['points'][0]['customdata'] if input_id == 'shaded-states' else state_sel
    return value

# Force updates when version changes
@callback(
    [Output('shaded-states', 'figure', allow_duplicate=True),
     Output('states-scatter', 'figure', allow_duplicate=True), 
     Output('State-trends-graph', 'figure', allow_duplicate=True)],
    [Input('state-version-store', 'data')],
    [State('region-selection', 'value'),
     State('crossfilter-yaxis-columnstate', 'value'),
     State('state-year-dropdown', 'value'),
     State('state-s', 'value'),
     State('health-metricsstate', 'value'),
     State('states-scatter', 'hoverData'),
     State('shaded-states', 'hoverData'),
     State('city-sel', 'value'),
     State('crossfilter-xaxis-typestate', 'value')],
    prevent_initial_call=True
)
def refresh_on_version_change(version, region, pollutant, year_value, state, metric, 
                             scatter_hover, map_hover, city_sel, xaxis_type):
    # Force update all figures when version changes
    # This will trigger the individual callbacks for each figure
    
    # Main map
    fig1 = update_map(region, pollutant, year_value, state, metric, version)
    
    # Scatter plot
    fig2 = update_scatter_plot(region, map_hover, pollutant, xaxis_type, 
                              year_value, state, city_sel, metric, version)
    
    # Trends graph
    fig3 = update_timeseries(region, scatter_hover, pollutant, city_sel, state, metric, version)

                              
    return fig1, fig2, fig3

##Sync the cities selected by hover with the dropdown menu
@callback(
    Output("city-sel", "value"),
    Input("city-sel", "value"),
    Input("states-scatter", "hoverData")
)
def sync_city_input(city_sel, hoverData):
    ctx = dash.callback_context

    if not ctx.triggered:
        # Nothing has triggered the callback yet
        return city_sel

    input_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if input_id == 'states-scatter' and hoverData:
        # Get city from hoverData if hover triggered the callback
        return hoverData['points'][0]['customdata'][0]
    
    # Default: return whatever is selected in dropdown
    return city_sel