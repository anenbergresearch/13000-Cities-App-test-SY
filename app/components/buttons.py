# Import necessary libraries
import dash_bootstrap_components as dbc
from dash import dcc,html

def sliders(df):
    layout = html.Div([
        dcc.Slider(
            id='crossfilter-year--slider',
            min=df['Year'].min(),
            max=df['Year'].max(),
            value=df['Year'].max(),
            marks={str(year): {'label': str(year)} for year in df['Year'].unique()},
            step=None,
            included=False,
            dots=False,
            tooltip={"placement": "bottom", "always_visible": False}
        )
    ], style={
        "padding": "0 15px",
        "marginTop": "15px",
        "marginBottom": "20px"
    })
    return layout

def lin_log(name):
    return html.Div([
        # Use a row to place title and buttons side by side
        dbc.Row([
            # Column for the title (left side)
            dbc.Col(
                html.Span("X-axis scale:", style={
                    'color': '#000000',
                    'font-size': '16px',
                    'font-family': 'helvetica',
                    'padding-right': '5px',
                    'display': 'flex',
                    'align-items': 'center',
                    'height': '100%',
                    'white-space': 'nowrap',
                    'font-weight': 'bold',
                }),
                width="auto",  # Auto width based on content
                style={'padding-right': '5px', 'display': 'flex', 'align-items': 'center'}
            ),
            
            # Column for the buttons (right side)
            dbc.Col(
                dbc.RadioItems(
                    id='crossfilter-xaxis-type'+name,
                    className="btn-group pollutant-radio-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-secondary pollutant-button rounded",
                    labelCheckedClassName="btn btn-outline-secondary pollutant-button selected-button rounded",
                    options=[
                        {'label': 'Linear', 'value': 'Linear'},
                        {'label': 'Log', 'value': 'Log'}
                    ],
                    value='Log',
                    labelStyle={'display': 'inline-block', 'margin': '0', 'padding': '0'}
                ),
                style={'padding-left': '0px'}
            )
        ], className="g-0 align-items-center")  # g-0 removes gutters, align-items-center vertically centers
    ], className="control-group", style={'padding': '0px'})


def health_metrics(name):
    tt = dbc.Tooltip(
        "Population Attributable Fraction (PAF) is the proportion of cases for an outcome that can be attributed to the pollutant among the entire population",
        target='PAF',
        trigger="hover",
    )
    td = dbc.Tooltip(
        "Annual cases for an outcome attributable to the pollutant",
        target='Cases',
        trigger="hover",
    )
    ts = dbc.Tooltip(
        "Annual cases for an outcome attributable to the pollutant per 100K people",
        target='Rates',
        trigger="hover",
    )
    
    metrics= html.Div([
        html.H6("Metric", style={
            'margin-bottom': '5px', 
            'font-weight': 'bold',
            'color': '#000000',
            'font-size': '18px',
            'font-family': 'helvetica'
        }),
        dbc.RadioItems(
            id='health-metrics'+name,
            className="btn-group",
            inputClassName="btn-check",
            labelClassName="btn btn-outline-secondary",
            labelCheckedClassName="selected-button",
            options=[{'label': i, 'value': i, 'label_id': i} for i in ['Concentration', 'PAF', 'Cases', 'Rates']],
            value='Concentration',
            labelStyle={'display': 'inline-block'}
        ),
        tt, td, ts
    ], className="control-group")
    return metrics

def details_tip(tar):
    tt= dbc.Tooltip(
                "Click Open Details for more information on the compenents of the webpage.",
                target=tar,
                #is_open =True,
                trigger ='hover focus legacy'
            )
    return tt

def members():
    C40 = html.Div([
        html.H6("City Type", style={
            'margin-bottom': '5px',
            'font-weight': 'bold',
            'color': '#000000',
            'font-size': '18px',
            'font-family': 'helvetica'
        }),
        # Wrapping div to help with spacing issues
        html.Div([
            dbc.RadioItems(
                id='c40-toggle',
                className="btn-group pollutant-radio-group",
                inputClassName="btn-check",
                labelClassName="btn btn-outline-secondary pollutant-button",
                labelCheckedClassName="btn btn-outline-secondary pollutant-button selected-button",
                options=[{'label': i, 'value': i} for i in ['Members', 'All Cities']],
                value='Members',
                labelStyle={'display': 'inline-block', 'margin': '0', 'padding': '0'}
            )
        ], style={'fontSize': '0', 'display': 'flex', 'whiteSpace': 'nowrap'})
    ], className="control-group")
    return C40

def instruct(ids):
    inst = html.Div([html.Div(dbc.Button(children="Open Details", id=ids, n_clicks=0,
                   color='primary'), className = 'd-grid mx-auto'),
                    dbc.Tooltip(
                        children ="Click Open Details for more information on the compenents of the webpage.",
                        id = ids+'tt',
                        target=ids,
                        is_open =True,
                        trigger ='hover focus legacy'
                    )]
                   )
    return inst

def pol_buttons(ident, selected_value='PM'):
    props = dict(
        id="crossfilter-yaxis-column" + ident,
        className="btn-group",
        inputClassName="btn-check",
        labelClassName="btn pollutant-button",
        labelCheckedClassName="btn pollutant-button selected-button",
        options=[
            {"label": u'PM\u2082\u2085', "value": 'PM'},
            {"label": u'NO\u2082', "value": 'NO2'},
            {"label": u'O\u2083', "value": 'O3'},
            {"label": u'CO\u2082', "value": 'CO2'},
        ],
        labelStyle={'display': 'inline-block'}
    )

    if selected_value is not None:
        props["value"] = selected_value

    return dbc.RadioItems(**props)


def pop_weighted(ident):
    wgt = dbc.RadioItems(
                    id='crossfilter-data-type'+ident,
                    className="btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-secondary",
                    labelCheckedClassName="secondary",
                    options=[{'label': i, 'value': i} for i in ['Unweighted','Population Weighted']],
                    value='Unweighted',
                    labelStyle={'display': 'inline-block'}
                )
    return wgt



def metric_options(is_co2_selected):
    """
    Generate the available metric options based on whether CO2 is selected
    
    Args:
        is_co2_selected (bool): Whether CO2 is selected as the pollutant
        
    Returns:
        list: List of metric options
    """
    if is_co2_selected:
        # CO2 only supports Concentration metric
        return[{"label": 'Concentration', "value": 'Concentration'},
                    {"label": 'PAF', "value": 'PAF','disabled':is_co2_selected},
                    {"label": 'Cases', "value": 'Cases','disabled':is_co2_selected},
                    {"label": 'Rates', "value": 'Rates', 'disabled':is_co2_selected}]   
    else:
        # All metrics available for other pollutants
        return [
            {'label': 'Concentration', 'value': 'Concentration'},
            {'label': 'PAF', 'value': 'PAF'},
            {'label': 'Cases', 'value': 'Cases'},
            {'label': 'Rates', 'value': 'Rates'}
        ]
        

# Function to generate pollutant options based on metric selection
def pol_options(disable_co2):
    """
    Generate the available pollutant options based on selected metric
    
    Args:
        disable_co2 (bool): Whether to disable CO2 option
        
    Returns:
        list: List of pollutant options
    """
    if disable_co2:
        # Don't include CO2 for health metrics
        return [
            {'label': 'PM₂₅', 'value': 'PM'},
            {'label': 'NO₂', 'value': 'NO2'},
            {'label': 'O₃', 'value': 'O3'},
            {'label': 'CO₂', 'value': 'CO2', 'disabled':disable_co2}
        ]
    else:
        # Include all pollutants
        return [
            {'label': 'PM₂₅', 'value': 'PM'},
            {'label': 'NO₂', 'value': 'NO2'},
            {'label': 'O₃', 'value': 'O3'},
            {'label': 'CO₂', 'value': 'CO2'}
        ]

# Fixed implementation for buttons.py - removing the disabled property
def percent_change_metric():
    """
    Creates a metric selector for the Percent Change tab using the same format
    as the version selector buttons.
    
    Returns:
        html.Div: Button component with a tooltip
    """
    # Create the metric selector component with identical format to version_selector
    metric_selector = html.Div([
        html.H6("Metric", style={
            'margin-bottom': '5px',
            'font-weight': 'bold',
            'color': '#000000',
            'font-size': '18px',
            'font-family': 'helvetica'
        }),
        html.Div([
            html.Div([
                html.Button(
                    "Percent Change in Concentration (2010-2011 vs. 2018-2019)",
                    id="percent-change-button",
                    className="version-button active-version",
                    n_clicks=0
                ),
                # Tooltip for Percent Change
                dbc.Tooltip(
                    "Percent changes in concentrations of each pollutant from the 2010-2011 2-year average to the 2018-2019 average. 2-year averages were used to reduce the influence of outliers from any single year.",
                    target="percent-change-button",
                    placement="bottom",
                    trigger="hover"
                )
            ], style={'display': 'inline-block'})
        ], className="version-button-group")
    ], className="control-group")
    
    return metric_selector

def membership():
    """
    Creates a membership dropdown selector for the app with a transparent background.
    
    Returns:
        html.Div: Membership dropdown component
    """
    membership_drop = html.Div([
        html.H6("Membership", style={
            'margin-bottom': '5px',
            'font-weight': 'bold',
            'color': '#000000',
            'font-size': '18px',
            'font-family': 'helvetica'
        }),
        dcc.Dropdown(
            id='membsDrop',
            options=[
                'All Cities',
                'All Memberships',
                'C40',
                'Global Covenant of Mayors',
                'Breathe Life 2030',
                'Climate Mayors (US ONLY)',
                'Carbon Neutral Cities Alliance ',
                'Resilient Cities Network',
                'Number of Memberships'
            ],
            value='All Cities',
            clearable=False,
            style={
                'width': '100%', 
                'color': '#123C69', 
                'font-size': '12px',
                'background-color': 'transparent'
            }
        )
    ], className='year-dropdown', style={'background-color': 'transparent'})
    
    return membership_drop

def year_dropdown(df):
    """
    Creates a year dropdown selector with a transparent background.
    
    Args:
        df (pandas.DataFrame): Dataframe containing Year column
        
    Returns:
        html.Div: Year dropdown component
    """
    available_years = sorted(df['Year'].unique())
    latest_year = max(available_years)
    
    year_drop = html.Div([
        html.H6("Year", style={
            'margin-bottom': '5px',
            'font-weight': 'bold',
            'color': '#000000',
            'font-size': '18px',
            'font-family': 'helvetica'
        }),
        dcc.Dropdown(
            id='crossfilter-year--slider',  # Keep the same ID for compatibility
            options=[{'label': str(year), 'value': year} for year in available_years],
            value=latest_year,
            clearable=False,
            style={
                'width': '100%', 
                'color': '#123C69', 
                'font-size': '12px',
                'background-color': 'transparent'
            }
        )
    ], className='year-dropdown', style={'background-color': 'transparent'})
    
    return year_drop

