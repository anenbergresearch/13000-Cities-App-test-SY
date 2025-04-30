import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, callback,dcc,html
from dash.dependencies import Input, Output,State
import dash_bootstrap_components as dbc
from components import const,data_prep,buttons

import dash

dash.register_page(__name__, path='/networks')
df = data_prep.DFILT

# Version 2 column mapping - Added for version control
V2_COLUMN_MAPPING = {
    'PM': 'Pw_PM_V2',
    'NO2': 'Pw_NO2_V2',
    'O3': 'Pw_O3_V2',
    'CO2': 'CO2_V2'
}

cont_l = df.continent.dropna().unique() #getting the list of distinct continent names
cont_dict = {}
for i in range(len(cont_l)):
    cont_dict[cont_l[i]]=const.CITY[i] #style

available_indicators = const.POLS

# Added version store for tracking active version with unique name
version_store = dcc.Store(id='cities-version-store', data='1')

# Added version selector component with unique IDs
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
                id="cities-version-1-button",
                className="version-button active-version",
                n_clicks=0
            ),
            # Tooltip for Version 1
            dbc.Tooltip(
                "Version 1 displays estimates from several previous studies for each pollutant, using data available as of 2022 (see more details in [About])",
                target="cities-version-1-button",
                placement="bottom",
                trigger="hover"
            )
        ], style={'display': 'inline-block'}),
        
        html.Div([
            html.Button(
                "Version 2",
                id="cities-version-2-button",
                className="version-button",
                n_clicks=0
            ),
            # Tooltip for Version 2
            dbc.Tooltip(
                "Version 2 displays updated estimates for each pollutant from Kim et al. (2025) (see more details in [About])",
                target="cities-version-2-button",
                placement="bottom",
                trigger="hover"
            )
        ], style={'display': 'inline-block'})
    ], className="version-button-group")
], className="control-group")


pollutant_selector = html.Div([
    html.H6("Pollutant", style={
        'margin-bottom': '5px',
        'font-weight': 'bold',
        'color': '#000000',
        'font-size': '18px',
        'font-family': 'helvetica'
    }),
    # Wrapping div to help with spacing issues
    html.Div([
        dbc.RadioItems(
            id="crossfilter-yaxis-columncities",
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

lin_log = buttons.lin_log('')
metrics = buttons.health_metrics('cities')  # Using 'cities' as a unique identifier
membership_sel = buttons.membership()

city_drop = html.Div(dcc.Dropdown(
                    id='cities-CityS',  # Unique ID
                    options=sorted(df["CityCountry"].unique()),
                    value='Washington D.C., United States (860)',
                    placeholder= 'Select city...',
                style ={'color':'#123C69', 'font-size':'12px'},
                ),className='single-dropd')

cont_drop = html.Div(dcc.Dropdown(
            id="cities-ContS",  # Unique ID
            value=list(cont_l.astype(str)),
            options=list(cont_l.astype(str)),
            multi=True, style ={'color':'#123C69'},
            placeholder= 'Select continents...'
        ),className="custom-dropdown")

year_selector = buttons.year_dropdown(df) 

main_graph = dcc.Graph(
            id='cities-crossfilter-indicator-scatter',  # Unique ID
            style={
                "border": "none",
                "boxShadow": "none",
                "outline": "none",
                "backgroundColor": "transparent"
            },
            hoverData={'points': [{'customdata': 'Washington D.C., United States (860)'}]}
        )                        

graph_stack = dbc.Stack([  
    dcc.Graph(
        id='cities-x-time-series',
        style={
            "height": "400px",  # Fixed height
            "maxHeight": "350px",
            "overflow": "hidden",
            "border": "none",
            "boxShadow": "none",
            "outline": "none",
            "backgroundColor": "transparent"
        }
    ),
    dcc.Graph(
        id='cities-y-time-series',
        style={
            "height": "400px",  # Fixed height
            "maxHeight": "350px", 
            "overflow": "hidden",
            "border": "none",
            "boxShadow": "none",
            "outline": "none",
            "backgroundColor": "transparent"
        }
    )
], gap=2)  # Add gap between graphs

# Title section
title_section = dbc.Row([
    dbc.Col(width=2),
    dbc.Col(
        html.Div(
            style={
                'backgroundColor': const.DISP['background'], 
                'marginTop': '2rem',
                'textAlign': 'center',  # Center align the entire container
                'display': 'flex',
                'flexDirection': 'column',
                'alignItems': 'center'  # Center align children horizontally
            }, 
            children=[
                html.H1(
                    children='Urban Climate Network Memberships', 
                    style={
                        'textAlign': 'center',
                        'color': 'black',
                        'fontFamily': 'Helvetica, Arial, sans-serif',
                        'fontWeight': 'bold',
                        'fontSize': '2.5rem',
                        'letterSpacing': '-0.05em',
                        'padding': '0.5rem 0',
                        'borderBottom': '3px solid rgba(0,0,0,0.1)',
                        'maxWidth': '800px',  # Optional: limit width for better readability
                        'width': '100%'
                    }
                ),
                html.Div(
                    children='A closer look at cities in different urban climate networks', 
                    style={
                        'textAlign': 'center',
                        'color': 'black',
                        'fontFamily': 'Helvetica, Arial, sans-serif',
                        'fontSize': '1rem',  # Fixed typo from '0.7 rem'
                        'marginTop': '0.2rem',
                        'marginBottom': '2.5rem',
                        'maxWidth': '800px',  # Optional: limit width for better readability
                        'width': '100%'
                    }
                )
            ]
        ),
        width=12,  # Use full width of the column
        className="d-flex justify-content-center"  # Bootstrap centering class
    )
], justify="center", align="center")

# Left column - Control Panel with three distinct rows (without lin_log)
left_controls = html.Div([
    # First row: Data version, Pollutant, Metric (removed lin_log)
    dbc.Row([
        dbc.Col(version_selector, lg=4, md=12, sm=12, style={"paddingRight": "2px", "paddingLeft": "2px"}),
        dbc.Col(pollutant_selector, lg=4, md=12, sm=12, style={"paddingRight": "2px", "paddingLeft": "2px"}),
        dbc.Col(metrics, lg=4, md=12, sm=12, style={"paddingRight": "2px", "paddingLeft": "2px"})
    ], className="mb-3", style={"marginLeft": "0", "marginRight": "0", "display": "flex", "flexWrap": "wrap"}),
    
    # Second row: Membership, Year
    dbc.Row([
        dbc.Col(membership_sel, lg=6, md=6, sm=12, style={"paddingRight": "5px", "paddingLeft": "5px"}),
        dbc.Col(year_selector, lg=6, md=6, sm=12, style={"paddingRight": "5px", "paddingLeft": "5px"})
    ], className="mb-3", style={"marginLeft": "0", "marginRight": "0", "display": "flex", "flexWrap": "wrap"}),
    
    # Third row: Country (Continent)
    dbc.Row([
        dbc.Col(cont_drop, width=12, style={"paddingRight": "5px", "paddingLeft": "5px"})
    ], className="mb-3", style={"marginLeft": "0", "marginRight": "0"})
], className="control-panel", style={"padding": "15px", "display": "block"})

# Left column scatter plot with lin_log button underneath (right-aligned)
left_main_content = html.Div([
    # Graph
    dbc.Row([
        dbc.Col(main_graph, width=12, className="dash-graph")
    ], style={"marginLeft": "0", "marginRight": "0",
              "border": "none",
        "boxShadow": "none",
        "outline": "none",
        "backgroundColor": "transparent"}),
    html.Div(style={"height": "20px"}),
    
    # Add lin_log button underneath the graph, right-aligned
    dbc.Row([
        dbc.Col(width=7),  # Empty space
        dbc.Col(lin_log, width=5, style={
            "paddingTop": "2px", 
            "display": "flex", 
            "justifyContent": "flex-end"})    
        ], className="g-0"),  # Remove gutters with g-0 class
])

# Complete left column
left_column = dbc.Col([
    html.H4("Urban Pollution vs. Population", className="mb-3 mt-1 text-center",
            style={"color": "#123C69", "fontFamily": "Helvetica, Arial, sans-serif",
                  "fontWeight": "bold", "borderBottom": "2px solid #123C69",
                  "paddingBottom": "10px", "fontSize": "25px"}),
    left_controls,
    left_main_content
], lg=7, md=12, sm=12, className="pe-4 two-column-divider")


# Right column components with fixed heights
right_controls = dbc.Row([
    dbc.Col(city_drop, width=12)
], className="mb-3")

right_controls_panel = html.Div([
    right_controls
], className="control-panel")

# Set a specific height for the graph stack
right_main_content = dbc.Row([
    dbc.Col(
        html.Div([
            graph_stack
        ], style={
            "height": "800px",  # Maintains total height
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "space-between"
        }),  # Fixed height that matches left column
        width=12, 
        className="dash-graph"
    )
])

# Complete right column
right_column = dbc.Col([
    html.H4("Time-series trends for selected city", className="mb-3 mt-1 text-center", 
            style={"color": "#123C69", "fontFamily": "Helvetica, Arial, sans-serif", 
                   "fontWeight": "bold", "borderBottom": "2px solid #123C69", 
                   "paddingBottom": "10px",  "fontSize": "25px"}),
    right_controls_panel,
    right_main_content
], width=5, className="ps-4")


# Adjust the two-column section to have a minimum height
two_column_section = dbc.Row([
    left_column,
    right_column
], className="mt-3", style={"height": "1000px"})


# Updated layout
layout = dbc.Container([
    # Adding version_store to the layout
    version_store,
    
    # Title section
    title_section,
  
    # Two-column section with all controls and graphs
    two_column_section
    
], fluid=True)

# Added callback to update version button styles and store version value
@callback(
    [Output("cities-version-1-button", "className"),  # Updated ID
     Output("cities-version-2-button", "className"),  # Updated ID
     Output("cities-version-store", "data")],  # Updated ID
    [Input("cities-version-1-button", "n_clicks"),  # Updated ID
     Input("cities-version-2-button", "n_clicks")],  # Updated ID
    [State("cities-version-store", "data")]  # Updated ID
)
def update_version_selection(v1_clicks, v2_clicks, current_version):
    ctx = dash.callback_context
    if not ctx.triggered:
        # Default to Version 1 on initial load
        return "version-button active-version", "version-button", "1"
    
    # Get which button was clicked
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == "cities-version-1-button":  # Updated ID
        return "version-button active-version", "version-button", "1"
    else:
        return "version-button", "version-button active-version", "2"


# Deactivates PAF, Cases, and Rates when CO2 is selected in either version
@callback(
    [Output('health-metricscities', 'options'),  # ID already scoped with 'cities'
     Output('crossfilter-yaxis-columncities', 'options')],  # ID already scoped with 'cities'
    [Input('crossfilter-yaxis-columncities', 'value'),  # ID already scoped with 'cities'
     Input('health-metricscities', 'value'),  # ID already scoped with 'cities'
     Input('cities-version-store', 'data')],  # Updated ID
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
    Output('health-metricscities', 'value'),  # ID already scoped with 'cities'
    Input('cities-version-store', 'data'),  # Updated ID
    prevent_initial_call=True
)
def reset_health_metrics_on_version_change(version):
    # When switching to Version 2, force Concentration
    if version == '2':
        return 'Concentration'
    # For Version 1, allow any selection (don't update)
    return dash.no_update


# Update metrics options when version changes
@callback(
    [Output('health-metricscities', 'options', allow_duplicate=True),
     Output('crossfilter-yaxis-columnscities', 'options', allow_duplicate=True)],
    [Input('state-version-store', 'data')],
    prevent_initial_call=True
)
def update_metrics_for_version(version):
    if version == '2':
        # Version 2 only has concentration data
        metric_opts = [{"label": "Concentration", "value": "Concentration"}]
        pollutant_opts = buttons.pol_options(False)  # All pollutants allowed
        return metric_opts, pollutant_opts
    else:
        # Version 1 has all metrics
        return buttons.metric_options(False), buttons.pol_options(False)

# Cleaned callback for scatter plot update - c40-toggle removed
@callback(
    Output('cities-crossfilter-indicator-scatter', 'figure'),  # Updated to use cities-specific ID
    [Input('crossfilter-yaxis-columncities', 'value'),
    Input('crossfilter-xaxis-type', 'value'),
    Input('crossfilter-year--slider', 'value'),
    Input('cities-CityS', 'value'),  # Updated to use cities-specific ID
    Input('cities-ContS', 'value'),  # Updated to use cities-specific ID
    Input('membsDrop', 'value'),
    Input('health-metricscities', 'value'),  # Updated to use cities-specific ID
    Input('cities-version-store', 'data')]  # Added version store input
)
def update_graph(yaxis_column_name,
                 xaxis_type,
                 year_value,
                 cityS,
                 contS,
                 memb,
                 metric,
                 version):  # Removed 'toggle' parameter
    
    dff = df.query('Year == @year_value').copy()
    city_df = dff.query('CityCountry == @cityS').copy()
    
    # Resolve metric column and unit based on version
    if version == '1':
        if metric != 'Concentration':
            yaxis_plot = metric + '_' + yaxis_column_name
        else:
            yaxis_plot = yaxis_column_name
        unit_title = const.UNITS[metric][yaxis_column_name]
    else:  # version == '2'
        yaxis_plot = V2_COLUMN_MAPPING[yaxis_column_name]
        unit_title = const.UNITS_V2[metric][yaxis_column_name]
    
    x_axis_label = 'Population'
    if xaxis_type == 'Log':
        x_range = [0, 8] 
    else:
        x_range = [0, 50_000_000] 
        
    plot = []
    
    # Define the mapping between dropdown options and actual column names
    membership_columns = {
        'C40': 'C40',
        'Global Covenant of Mayors': 'Global.Covenant.of.Mayors',
        'Breathe Life 2030': 'Breathe.Life.2030',
        'Climate Mayors (US ONLY)': 'Climate.Mayors..US.ONLY.',
        'Carbon Neutral Cities Alliance ': 'Carbon.Neutral.Cities.Alliance',
        'Resilient Cities Network': 'Resilient.Cities.Network'
    }
    
    # Handle 'All Cities' option first as a special case
    if memb == 'All Cities':
        # Show all cities grouped by continent
        for i in contS:
            _c = dff.query('continent == @i')
            plot.append(go.Scatter(
                name = i, 
                legendgroup = 'All Cities',
                legendgrouptitle = {'text': 'All Cities'}, 
                x = _c['Population'], 
                y = _c[yaxis_plot], 
                mode = 'markers',
                customdata = _c['CityCountry'],
                hovertemplate = "<b>%{customdata}</b><br>" + 'Population: %{x} <br>' + unit_title + ': %{y}',
                marker = {
                    'color': cont_dict[i][1],
                    'size': 7,
                    'opacity': 0.75,
                    'line': dict(width=0.2, color=const.DISP['background'])
                }
            ))
    
    # Handle 'Number of Memberships' option
    elif memb == 'Number of Memberships':
        coll = ['#f4f100', '#c9e52f', '#76c68f', '#22a7f0', '#115f9a']
        
        # Add cities with 0 memberships
        _nc = dff.query('Memberships == 0') 
        plot.append(go.Scatter(
            name = '0 Memberships', 
            legendgroup = 'Memberships', 
            legendgrouptitle = {'text': 'Number of Memberships'}, 
            x = _nc['Population'],
            y = _nc[yaxis_plot],
            mode = 'markers',
            customdata = _nc['CityCountry'],
            hovertemplate = "<b>%{customdata}</b><br>" + 'Population: %{x} <br> ' + unit_title + ': %{y}',
            marker = {'color': 'pink', 'opacity': 0.4}
        ))
        
        # Add cities with 1-4+ memberships
        for i in range(1, 5):
            _nc = dff.query('Memberships == @i')
            if i == 4:
                _nc = dff.query('Memberships >= @i')
            plot.append(go.Scatter(
                name = str(i) + ' Memberships', 
                legendgroup = 'Memberships', 
                legendgrouptitle = {'text': 'Number of Memberships'}, 
                x = _nc['Population'],
                y = _nc[yaxis_plot],
                mode = 'markers',
                customdata = _nc['CityCountry'],
                hovertemplate = "<b>%{customdata}</b><br>" + 'Population: %{x} <br> ' + unit_title + ': %{y}',
                marker = {'color': coll[i], 'opacity': 0.9}
            ))
    
    # Handle 'All Memberships' option
    elif memb == 'All Memberships':
        # Get the list of actual membership columns that exist in the dataframe
        for m_display, m_col in membership_columns.items():
            if m_col in dff.columns:
                _c = dff[dff[m_col] == True]
                
                # Generate a consistent color for this membership if not in const.MEMBERS
                color = const.MEMBERS.get(m_col, [0, '#' + ''.join([hex(hash(m_col) % 256)[2:].zfill(2) for _ in range(3)])])[1]
                symbol = const.MEMBERS.get(m_col, [0, '#000000'])[0]
                
                plot.append(go.Scatter(
                    name = m_display,  # Use the display name for legend 
                    legendgroup = memb,
                    legendgrouptitle = {'text': memb + ' Cities'}, 
                    x = _c['Population'], 
                    y = _c[yaxis_plot], 
                    mode = 'markers',
                    customdata = _c['CityCountry'],
                    hovertemplate = "<b>%{customdata}</b><br>" + 'Population: %{x} <br>' + unit_title + ': %{y}',
                    marker = {
                        'color': color,
                        'symbol': symbol,
                        'size': 10,
                        'opacity': 0.8,
                        'line': dict(width=0.5, color=const.DISP['background'])
                    }
                ))
    
    # Handle specific membership option
    else:
        # Get the actual column name for the selected membership
        if memb in membership_columns:
            column_name = membership_columns[memb]
            
            # Check if the column exists in the dataframe
            if column_name in dff.columns:
                for i in contS:
                    _c = dff.query('continent == @i')
                    _c = _c[_c[column_name] == True]
                    
                    # Generate a consistent symbol if not in const.MEMBERS
                    symbol = 0  # Default symbol
                    if column_name in const.MEMBERS:
                        symbol = const.MEMBERS[column_name][0]
                    
                    plot.append(go.Scatter(
                        name = i, 
                        legendgroup = memb,
                        legendgrouptitle = {'text': memb + ' Cities'}, 
                        x = _c['Population'], 
                        y = _c[yaxis_plot], 
                        mode = 'markers',
                        customdata = _c['CityCountry'],
                        hovertemplate = "<b>%{customdata}</b><br>" + 'Population: %{x} <br>' + unit_title + ': %{y}',
                        marker = {
                            'color': cont_dict[i][1], 
                            'symbol': symbol,
                            'size': 10,
                            'line': dict(width=0.8, color=const.DISP['background'])
                        }
                    ))
            else:
                # If column doesn't exist, just show an empty plot
                print(f"Warning: Column '{column_name}' not found in dataframe for membership '{memb}'")
        else:
            # If membership is not in our mapping (shouldn't happen), show an empty plot
            print(f"Warning: Unknown membership option '{memb}'")

    fig = go.Figure(data=plot)
    
    fig.update_layout(
        legend = dict(groupclick="toggleitem"),
        legend_title_text = '',
        paper_bgcolor = const.DISP['background'],
        plot_bgcolor = const.DISP['background']
    )
    
    fig.add_trace(
        go.Scattergl(
            mode = 'markers',
            x = city_df['Population'],
            y = city_df[yaxis_plot],
            opacity = 1,
            marker = dict(
                symbol = 'circle-dot',
                color = '#FAED26',
                size = 11,
                line = dict(
                    color = const.DISP['text'],
                    width = 2
                ),
            ),
            showlegend = False,
            hoverinfo = 'skip'
        )
    )    
    

    fig.update_xaxes(
        title=x_axis_label, 
        type='linear' if xaxis_type == 'Linear' else 'log',
        range=x_range
    )
    fig.update_yaxes(title=unit_title)
    fig.update_layout(
        margin = {'l': 40, 'b': 40, 't': 10, 'r': 0}, 
        hovermode = 'closest',
        legend = dict(
            x = 0,
            y = 1,
            bgcolor = 'rgba(255, 255, 255, 0.5)',
            borderwidth = 0, 
            font = dict(size = 18, color = const.DISP['text'])
        ),
        font = dict(
            size = const.FONTSIZE,
            family = const.FONTFAMILY
        )
    )
    
    return fig

@callback(
    Output('crossfilter-xaxis-type', 'data'),
    Input('lin-log-radio', 'value')
)
def sync_lin_log(value):
    return value

@callback(
    Output('cities-x-time-series', 'figure'),  # Updated ID
    [Input('cities-crossfilter-indicator-scatter', 'hoverData'),  # Updated ID
     Input('cities-CityS', 'value')]  # Updated ID
)
def update_pop_timeseries(hoverData, city_sel):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    city_sel = hoverData['points'][0]['customdata'] if input_id == 'cities-crossfilter-indicator-scatter' and hoverData else city_sel

    if not city_sel:
        # Return a default figure with consistent layout
        return go.Figure(layout=go.Layout(
            height=325,
            margin={'l': 20, 'b': 30, 'r': 10, 't': 10},
            paper_bgcolor=const.DISP['background'],
            plot_bgcolor=const.DISP['background'],
            font=dict(size=const.FONTSIZE, family=const.FONTFAMILY)
        ))

    dff = df[df['CityCountry'] == city_sel]
    if dff.empty:
        # Return a default figure with consistent layout
        return go.Figure(layout=go.Layout(
            height=325,
            margin={'l': 20, 'b': 30, 'r': 10, 't': 10},
            paper_bgcolor=const.DISP['background'],
            plot_bgcolor=const.DISP['background'],
            font=dict(size=const.FONTSIZE, family=const.FONTFAMILY)
        ))

    country_name = dff['CityCountry'].iloc[0]
    
    title_add = f"<b>{country_name}</b>"

    fig = go.Figure(go.Scatter(
        x=dff['Year'], 
        y=dff['Population'],
        name='Population',
        hovertemplate="<b>Year: </b>%{x}<br><b>Population: </b>%{y:,}<extra></extra>",
        mode='lines+markers'
    ))
    
    fig.update_traces(
        line=dict(color='#123C69'),  # Use a consistent color
        marker=dict(color='#123C69', size=8))
    fig.update_xaxes(
        showgrid=False, 
        title='')
    fig.update_yaxes(
        type='linear', 
        title='Population',
        tickformat=',')
    fig.update_layout(
        height=325,  # Fixed height
        margin={'l': 60, 'b': 30, 'r': 10, 't': 10},
        paper_bgcolor=const.DISP['background'],
        plot_bgcolor=const.DISP['background'],
        font=dict(
            size=const.FONTSIZE, 
            family=const.FONTFAMILY))
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
        text=title_add)
    
    return fig


@callback(
    Output('cities-y-time-series', 'figure'),  # Updated ID
    [Input('cities-crossfilter-indicator-scatter', 'hoverData'),  # Updated ID
     Input('crossfilter-yaxis-columncities', 'value'),  # ID already scoped with 'cities'
     Input('cities-CityS', 'value'),  # Updated ID
     Input('cities-version-store', 'data'),  # Updated ID
     Input('health-metricscities', 'value')]  # Added metric input
)
def update_pol_timeseries(hoverData, yaxis_column_name, city_sel, version, metric):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    city_sel = hoverData['points'][0]['customdata'] if input_id == 'cities-crossfilter-indicator-scatter' and hoverData else city_sel
    
    if not city_sel or not yaxis_column_name:
        # Return a default figure with consistent layout
        return go.Figure(layout=go.Layout(
            height=325,
            margin={'l': 20, 'b': 30, 'r': 10, 't': 10},
            paper_bgcolor=const.DISP['background'],
            plot_bgcolor=const.DISP['background'],
            font=dict(size=const.FONTSIZE, family=const.FONTFAMILY)
        ))

    dff = df[df['CityCountry'] == city_sel]
    if dff.empty:
        # Return a default figure with consistent layout
        return go.Figure(layout=go.Layout(
            height=325,
            margin={'l': 20, 'b': 30, 'r': 10, 't': 10},
            paper_bgcolor=const.DISP['background'],
            plot_bgcolor=const.DISP['background'],
            font=dict(size=const.FONTSIZE, family=const.FONTFAMILY)
        ))

    country_name = dff['CityCountry'].iloc[0]
    
    # Determine which column to plot based on metric and pollutant
    if metric == 'Concentration':
        # Version-dependent concentration mapping
        if version == '2' and yaxis_column_name in V2_COLUMN_MAPPING:
            axis_plot = V2_COLUMN_MAPPING[yaxis_column_name]
            ytitle = const.UNITS_V2['Concentration'].get(yaxis_column_name, yaxis_column_name)
        else:
            axis_plot = yaxis_column_name
            ytitle = const.UNITS['Concentration'][yaxis_column_name]
        
    else:
        # Other metrics (PAF, Rates, Cases)
        axis_plot = metric + '_' + yaxis_column_name
        ytitle = metric

    title_add = f"<b>{country_name}</b>"
    fig = go.Figure(go.Scatter(
        x=dff['Year'], 
        y=dff[axis_plot],
        name=ytitle,
        hovertemplate=f"<b>Year: </b>%{{x}}<br><b>{ytitle}: </b>%{{y:.4f}}<extra></extra>",
        mode='lines+markers'
    ))
    
    fig.update_traces(
        line=dict(color='#123C69'),  # Use a consistent color
        marker=dict(color='#123C69', size=8))
    fig.update_xaxes(
        showgrid=True, 
        title='')
    fig.update_yaxes(
        title=ytitle,
        tickformat='.4f')
    fig.update_layout(
        height=325,  # Fixed height
        margin={'l': 60, 'b': 30, 'r': 10, 't': 10},
        paper_bgcolor=const.DISP['background'],
        plot_bgcolor=const.DISP['background'],
        font=dict(
            size=const.FONTSIZE, 
            family=const.FONTFAMILY))

    return fig





@callback(
    Output("cities-CityS", "value"),  # Updated ID
    [Input("cities-CityS", "value"),  # Updated ID
     Input('cities-crossfilter-indicator-scatter', 'hoverData')]  # Updated ID
)
def sync_input(city_sel, hoverData):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id == 'cities-crossfilter-indicator-scatter' and hoverData:
        return hoverData['points'][0]['customdata']
    return city_sel