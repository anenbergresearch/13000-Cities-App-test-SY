import dash
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, dcc, html, callback, dash_table, State
import dash_bootstrap_components as dbc
from components import buttons, const, data_prep
import copy

# ---------------------------------------------------
# INITIALIZE RESOURCES AND DATA
# ---------------------------------------------------
dash.register_page(__name__, path='/')

# Load data
cb = pd.read_csv('https://raw.githubusercontent.com/anenbergresearch/app-files/main/Codebook.csv')
df = data_prep.DFILT
pc_df = data_prep.DF_CHANGE

# Define limits and mappings
conc = {'CO2': 15e6, 'NO2': 20, 'O3': 75, 'PM': 100}
conc_v2 = {'CO2': 10, 'NO2': 20, 'O3': 75, 'PM': 100} #for version 2 
paf = {'CO2': 'null', 'NO2': 25, 'O3': 20, 'PM': 40}
cases = {'CO2': 'null', 'NO2': 1000, 'O3': 100, 'PM': 1000}
rates = {'CO2': 'null', 'NO2': 100, 'O3': 40, 'PM': 110}
m_limits = {'Concentration': conc, 'PAF': paf, 'Cases': cases, 'Rates': rates}
m_limits_v2 = {'Concentration': conc_v2, 'PAF': paf, 'Cases': cases, 'Rates': rates} #for version 2

# Version 2 column mapping
V2_COLUMN_MAPPING = {
    'PM': 'Pw_PM_V2',
    'NO2': 'Pw_NO2_V2',
    'O3': 'Pw_O3_V2',
    'CO2': 'CO2_V2'
}
V1_COLUMN_MAPPING = {
    'PM': 'Pw_PM',
    'NO2': 'Pw_NO2',
    'O3': 'Pw_O3',
    'CO2': 'CO2'
}

# ---------------------------------------------------
# UI COMPONENTS BY TAB ORDER 
# ---------------------------------------------------

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
                    children='Urban Air Quality Explorer', 
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
                    children='Exploring pollution levels in 13,189 urban areas worldwide', 
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


# 1. MAP TAB COMPONENTS
# Version tracking - Used to store active version
version_store = dcc.Store(id='version-store', data='1')

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
                id="version-1-button",
                className="version-button active-version",
                n_clicks=0
            ),
            # Tooltip for Version 1
            dbc.Tooltip(
                "Version 1 displays estimates from several previous studies for each pollutant, using data available as of 2022 (see more details in [About])",
                target="version-1-button",
                placement="bottom",
                trigger="hover"
            )
        ], style={'display': 'inline-block'}),
        
        html.Div([
            html.Button(
                "Version 2",
                id="version-2-button",
                className="version-button",
                n_clicks=0
            ),
            # Tooltip for Version 2
            dbc.Tooltip(
                "Version 2 displays updated estimates for each pollutant from Kim et al. (2025) (see more details in [About])",
                target="version-2-button",
                placement="bottom",
                trigger="hover"
            )
        ], style={'display': 'inline-block'})
    ], className="version-button-group")
], className="control-group")

# Pollutant selector component
# Updated Pollutant selector component with better HTML structure
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
            id="pollutant-selector",
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

# Health metrics selector
metrics = buttons.health_metrics('home')

# Map graphs
graph = dcc.Graph(
    id='welcome-map',
    style={
        "height": "650px",  # Fixed height
        "width": "100%",    # Full width of container
        "maxHeight": "650px",  # Prevent excessive growth
        "minHeight": "550px",  # Prevent shrinking too much
        "border": "none",
        "boxShadow": "none",
        "outline": "none",
        "backgroundColor": "transparent"
    },
    config={
        'responsive': True,  # Make the graph responsive
        'displayModeBar': True,  # Show Plotly control buttons
        'displaylogo': False,  # Remove Plotly logo
        'modeBarPosition': 'left top',  # Move mode bar to top left
        'scrollZoom': False,  # Disable scroll zooming on the map
        'modeBarButtonsToAdd': ['pan2d', 'zoom2d', 'zoomIn2d', 'zoomOut2d', 'resetScale2d'],  # Specific buttons you want
        'modeBarButtonsToRemove': ['select2d', 'lasso2d']  # Optionally remove some default buttons
    }
)
slider = buttons.sliders(df)

# 2. PERCENT CHANGE TAB COMPONENTS
pc_graph = dcc.Graph(
    id='percent-change',
    style={
        "height": "650px",  # Fixed height
        "width": "100%",    # Full width of container
        "maxHeight": "650px",  # Prevent excessive growth
        "minHeight": "550px",  # Prevent shrinking too much
        "border": "none",
        "boxShadow": "none",
        "outline": "none",
        "backgroundColor": "transparent"
    },
    config={
        'responsive': True,  # Make the graph responsive
        'displayModeBar': True,  # Show Plotly control buttons
        'displaylogo': False,  # Remove Plotly logo
        'modeBarPosition': 'left top',  # Move mode bar to top left
        'scrollZoom': False,  # Disable scroll zooming on the map
        'modeBarButtonsToAdd': ['pan2d', 'zoom2d', 'zoomIn2d', 'zoomOut2d', 'resetScale2d'],  # Specific buttons you want
        'modeBarButtonsToRemove': ['select2d', 'lasso2d']  # Optionally remove some default buttons
    }
)

# 3. CODEBOOK TAB COMPONENTS
table = html.Div(
    [
        html.H4("Data Codebook", style={'fontFamily': 'Helvetica Neue, Helvetica, Arial, sans-serif'}),
        html.P("(* Use the button below to download the full dataset.)", 
               style={'fontSize': '0.8em', 'fontFamily': '"Helvetica Neue", Helvetica, Arial, sans-serif'}
        ),
        dash_table.DataTable(
            id="table",
            columns=[{"name": i, "id": i} for i in cb.columns],
            data=cb.to_dict("records"),
            style_cell=dict(textAlign="left"),
        ),
    ]
)

download = html.Div(
    [
        dbc.Button("Download Full CSV",
                   href='https://raw.githubusercontent.com/anenbergresearch/app-files/main/unified_data_SYK_Apr2025.csv',
                   download='unified_data.csv',
                   id='download_full',
                   external_link=True,
                   color='secondary'
                   ),
    ],
    className="d-grid gap-2"
)

tt = dbc.Tooltip(
    "Download the full, unfiltered dataset here. Both version 1 and 2 estimates are included. Download data filtered by country, city and/or year in [Data Download]. See more information in [About].",
    target='download_full',
    trigger='hover',
    placement='top',
    style={'color': 'lightgray'}
)

# 4. DATA DOWNLOAD TAB COMPONENTS
country_dropdown = dbc.Col(
    [
        html.Label("Country:", style={
            'fontWeight': 'bold',
            'color': 'black',
            'fontFamily': 'Helvetica, Arial, sans-serif',
            'marginBottom': '5px', 'fontSize': '15px'
        }),
        dcc.Dropdown(
            id='CountrySe',
            options=sorted(df["Country"].unique()),
            value='United States',
            clearable=False,
            style={'color': '#123C69'}
        )
    ],
    width=3  # Equal width (4 columns of width 3 = 12 total)
)

city_dropdown = dbc.Col(
    [
        html.Label("City:", style={
            'fontWeight': 'bold',
            'color': 'black',
            'fontFamily': 'Helvetica, Arial, sans-serif',
            'marginBottom': '5px', 'fontSize': '15px'
        }),
        dcc.Dropdown(
            id='CitySe',
            options=sorted(df["CityCountry"].unique()),
            value='Washington D.C., United States (860)',
            clearable=False,
            style={'color': '#123C69'}
        )
    ],
    width=3  # Equal width
)

year_options = [{'label': str(year), 'value': year} for year in range(2000, 2021)]

year_from_dropdown = dbc.Col(
    [
        html.Label("From:", style={
            'fontWeight': 'bold',
            'color': 'black',
            'fontFamily': 'Helvetica, Arial, sans-serif',
            'marginBottom': '5px', 'fontSize': '15px'
        }),
        dcc.Dropdown(
            id='year-from-dropdown',
            options=year_options,
            value=2000,
            clearable=False,
            style={'color': '#123C69'}
        )
    ],
    width=3
)

year_to_dropdown = dbc.Col(
    [
        html.Label("To:", style={
            'fontWeight': 'bold',
            'color': 'black',
            'fontFamily': 'Helvetica, Arial, sans-serif',
            'marginBottom': '5px', 'fontSize': '15px'
        }),
        dcc.Dropdown(
            id='year-to-dropdown',
            # We'll set options dynamically based on the year-from selection
            # So we leave options empty or with all years initially
            options=year_options,  
            value=2020,
            clearable=False,
            style={'color': '#123C69'}
        )
    ],
    width=3
)

dtable = dash_table.DataTable(
    id="filtered-data-table",
    columns=[{"name": i, "id": i} for i in df.columns],
    sort_action="native",
    page_size=10,
    style_table={"overflowX": "auto"},
    css=[ # Use !important to override default styles
        {
            'selector': 'td.dash-cell',
            'rule': 'font-size: 17px !important; padding: 1px !important;'
        },
        {
            'selector': 'th.dash-header',
            'rule': 'font-size: 17px !important; padding: 1px !important; '
        },
        {
            'selector': '.dash-spreadsheet',
            'rule': 'font-family: Helvetica, Arial, sans-serif !important;'
        },
        {
            'selector': '.dash-cell-value',
            'rule': 'font-size: 17px !important;'
        }
    ]
)

download_button = dbc.Button("Download Filtered CSV", id="download-button", color='secondary')
download_component = dcc.Download(id="download-filtered-data")

# 6. ABOUT TAB COMPONENTS
about_acc = html.Div(
    dbc.Accordion(
        [
            dbc.AccordionItem(
                [
                    dcc.Markdown(dangerously_allow_html=True, children='''
                    Version 1
                    - Version 1 PM<sub>2.5</sub> urban concentrations and disease burdens are from [Southerland et al. (2022)](https://www.thelancet.com/journals/lanplh/article/PIIS2542-5196(21)00350-8/fulltext). PM<sub>2.5</sub> concentrations are not from the GBD 2019, but are from a higher spatial resolution dataset (1km x 1km) developed by [Hammer et al. (2020)](https://pubs.acs.org/doi/full/10.1021/acs.est.0c01764). The dataset integrates information from satellite-retrieved aerosol optical depth, chemical transport modeling, and ground monitor data. Briefly, multiple AOD retrievals from three satellite instruments (the Moderate Resolution Imaging Spectroradiometer (MODIS), SeaWiFs, and the Multiangle Imaging Spectroradiometer (MISR)) were combined and related to near-surface PM<sub>2.5</sub> concentrations using the GEOS-Chem chemical transport model. Ground-based observations of PM<sub>2.5</sub> were then incorporated using a geographically weighted regression. PM<sub>2.5</sub> concentrations and disease burdens are year-specific.
                    - Version 1 NO<sub>2</sub> urban concentrations and disease burdens are from [Anenberg et al. (2022)](https://www.thelancet.com/journals/lanplh/article/PIIS2542-5196(21)00255-2/fulltext). NO<sub>2</sub> concentrations (1km x 1km) are those used by the GBD 2020, as NO<sub>2</sub> is a new pollutant included in the GBD after GBD 2019. The dataset was originally developed by [Anenberg et al. (2022)](https://www.thelancet.com/journals/lanplh/article/PIIS2542-5196(21)00255-2/fulltext) and combines surface NO<sub>2</sub> concentrations for 2010-2012 from a land use regression model with Ozone Monitoring Instrument (OMI) satellite NO<sub>2</sub> columns to scale to different years. NO<sub>2</sub> concentrations and disease burdens are year-specific and were interpolated for the years between 2000 and 2005 and between 2005 and 2010.
                    - Version 1 O<sub>3</sub> urban concentrations and disease burdens are from [Malashock et al. (2022a)](https://iopscience.iop.org/article/10.1088/1748-9326/ac66f3) and [Malashock et al. (2022b)](https://doi.org/10.1016/S2542-5196(22)00260-1). Estimates of ozone seasonal daily maximum 8-hour mixing ratio (OSDMA8) concentrations are from the GBD 2019 (0.1 x 0.1 degree), originally developed by [DeLang et al. (2021)](https://pubs.acs.org/doi/abs/10.1021/acs.est.0c07742). OSDMA8 is calculated as the annual maximum of the six-month running mean of the monthly average daily maximum 8 hour mixing ratio, including through March of the following year to contain the Southern Hemisphere summer. [DeLang et al. (2021)](https://pubs.acs.org/doi/abs/10.1021/acs.est.0c07742) combined ozone ground measurement data with chemical transport model estimates. Output was subsequently downscaled to create fine (0.1 degree) resolution estimates of global surface ozone concentrations from 1990-2017. For the GBD 2019 study, the Institute for Health Metrics and Evaluation (IHME) extrapolated the available estimates for 1990–2017 to 2019 using log-linear trends based on 2008−2017 estimates. We re-gridded ozone data to 1 km (0.0083 degree) resolution to match the spatial resolution of the population estimates. Ozone concentrations and disease burdens are year-specific.
                    - Version 1 CO<sub>2</sub> urban emissions are from Emission Database for Global Atmospheric Research ([EDGAR](https://edgar.jrc.ec.europa.eu/report_2022)). The fossil fuel CO<sub>2</sub> emissions are isolated by adding the annual long cycle CO<sub>2</sub> emissions from [EDGAR v7.0](https://edgar.jrc.ec.europa.eu/dataset_ghg70) for the following sectors: *Power Industry;  Energy for Buildings; Combustion for Manufacturing Industry; Road Transportation; Aviation (landing & take off, climbing & descending, and cruise); Shipping and Railways; Pipelines; and Off-Road Transport.*
                    - Urban built-up area is from the [GHS-SMOD](https://ghsl.jrc.ec.europa.eu/ghs_smod2019.php) dataset. Urban boundaries don't follow administrative boundaries and include surrounding built-up areas. [Apte et al. (2021)](https://chemrxiv.org/engage/chemrxiv/article-details/60c75932702a9baa0818ce61) show that the urban boundary definition doesn't influence concentration estimates much.
                    - Population is from the [Worldpop](https://www.worldpop.org/) dataset at ~1km resolution. There's quite a bit of difference between globally gridded population datasets, and it's not clear which is the "best" source. A good resource to see how different population datasets compare in different areas of the world is https://sedac.ciesin.columbia.edu/mapping/popgrid/.
                    
                    Version 2
                    - Version 2 PM<sub>2.5</sub> urban concentrations are from [Kim et al. (2025)](https://www.nature.com/articles/s43247-025-02270-9). PM<sub>2.5</sub> concentrations are from [van Donkelaar et al. (2021)](https://pubs.acs.org/doi/10.1021/acs.est.1c05309), which estimates annual average concentrations at 0.01° (~ 1 km) resolution, combining satellite remote sensing of aerosol optical depth, a chemical transport model, and ground-based measurements.
                    - Version 2 NO<sub>2</sub> urban concentrations are from [Kim et al. (2025)](https://www.nature.com/articles/s43247-025-02270-9). NO<sub>2</sub> concentrations are from [Larkin et al. (2023)](https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2023.1125979/full). This dataset provides annual average concentrations at 50 m resolution using a land-use regression model that ingests remotely-sensed measurements from the Ozone Monitoring Instrument (OMI) with other land use variables, trained against ground-based measurements worldwide.
                    - Version 2 O<sub>3</sub> urban concentrations are from [Kim et al. (2025)](https://www.nature.com/articles/s43247-025-02270-9). O<sub>3</sub> concentrations are from the [GBD 2019 study](https://ghdx.healthdata.org/record/global-burden-disease-study-2019-gbd-2019-air-pollution-exposure-estimates-1990-2019), which is extrapolated from a dataset of [DeLang et al. (2021)](https://pubmed.ncbi.nlm.nih.gov/33682412/). This dataset estimated the annual maximum of the six-month running mean of the monthly average daily maximum 8h mixing ratio (ozone season daily maximum 8h mixing ratios, OSDMA8) at 0.1° (~ 10 km) resolution combining ground-based O3 observations from the Tropospheric Ozone Assessment Report (TOAR) and the Chinese National Environmental Monitoring Center (CNEMC) Network, and outputs from multiple global atmospheric models.
                    - Version 2 CO<sub>2</sub> urban emissions are from [Kim et al. (2025)](https://www.nature.com/articles/s43247-025-02270-9). CO<sub>2</sub> emissons are from annual sector-specific emission datasets of the [EDGAR v8.0](https://edgar.jrc.ec.europa.eu/report_2023), which has 0.1° (~ 10 km) resolution with global coverage.
                    - [Kim et al. (2025)](https://www.nature.com/articles/s43247-025-02270-9) used the same urban boundary and popoulation datasets as those used in version 1 studies.
                    '''
                    ),
                ],
                title="More Information",
            ),
            dbc.AccordionItem(
                [
                    dcc.Markdown('''
                    This project was led by Susan Anenberg from the Milken Institute School of Public Health at George Washington University, with support from NASA, the Health Effects Institute, and the Wellcome Trust. The website was originally developed by Sara Runkel and has since been redesigned and is currently maintained by Soo-Yeon Kim. Additional contributors include Veronica Southerland, Danny Malashock, Arash Mohegh, Josh Apte, Jacob Becker, Michael Brauer, Katrin Burkart, Kai-Lan Chang, Owen Cooper, Marissa DeLang, Dan Goldberg, Melanie Hammer, Daven Henze, Perry Hystad, Gaige Kerr, Pat Kinney, Andy Larkin, Randall Martin, Omar Nawaz, Marc Serre, Aaron Van Donkelaar, Jason West and Sarah Wozniak. We also gratefully acknowledge the developers of the input datasets, including satellite observations, pollution concentration, GHS-SMOD urban area, Worldpop population, and GBD disease rates and concentration-response functions. The contents of this website do not necessarily reflect the views of NASA, the Health Effects Institute, or the Wellcome Trust.
                    '''
                    ),
                ],
                title="Acknowledgements",
            ),
            dbc.AccordionItem(
                [
                    dcc.Markdown(dangerously_allow_html=True, children='''
                    - If you have any questions, feedback, or encounter technical issues with the dataset or webpage, feel free to reach out.
                    - Email: Soo-Yeon Kim ([sooyeonkim@gwu.edu]), Susan C. Anenberg ([sanenberg@email.gwu.edu])
                    - We appreciate your feedback!
                     '''
                    ),
                ],
                title="Contact",
            )
        ],
        flush=True),
    style={'maxHeight': '600px', 'overflowY': 'auto'}
    )


# ---------------------------------------------------
# LAYOUT
# ---------------------------------------------------

# Main layout with all tabs
layout = dbc.Container([
    version_store,  # Add store for version tracking
    title_section,
    html.Hr(),
    dbc.Tabs([
        dbc.Tab(label='Map', tab_id='welcome_map',style={'font-color':'blue'}),
        dbc.Tab(label='Percent Change', tab_id='percent_change'),
        dbc.Tab(label='Data Codebook', tab_id='codebook'),
        dbc.Tab(label='Data Download', tab_id='download'),
        dbc.Tab(label='About', tab_id='about'),
    ],
    id='tabs',
    active_tab='welcome_map'
    ),
    html.Div(id="tab-content", className="p-4"),
    html.Hr(),

], fluid=True)

# ---------------------------------------------------
# CALLBACKS BY TAB ORDER
# ---------------------------------------------------

# 1. MAP TAB CALLBACKS

# Callback to update version button styles and store version value
@callback(
    [Output("version-1-button", "className"),
     Output("version-2-button", "className"),
     Output("version-store", "data")],
    [Input("version-1-button", "n_clicks"),
     Input("version-2-button", "n_clicks")],
    [State("version-store", "data")]
)
def update_version_selection(v1_clicks, v2_clicks, current_version):
    ctx = dash.callback_context
    if not ctx.triggered:
        # Default to Version 1 on initial load
        return "version-button active-version", "version-button", "1"
    
    # Get which button was clicked
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == "version-1-button":
        return "version-button active-version", "version-button", "1"
    else:
        return "version-button", "version-button active-version", "2"


# Deactivates PAF, Cases, and Rates when CO2 is selected in either version
@callback(
    [Output('health-metricshome', 'options', allow_duplicate=True),
     Output('pollutant-selector', 'options', allow_duplicate=True)],
    [Input('pollutant-selector', 'value'),
     Input('health-metricshome', 'value'),
     Input('version-store', 'data')],
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
    Output('health-metricshome', 'value'),
    Input('version-store', 'data'),
    prevent_initial_call=True
)
def reset_health_metrics_on_version_change(version):
    # When switching to Version 2, force Concentration
    if version == '2':
        return 'Concentration'
    # For Version 1, allow any selection (don't update)
    return dash.no_update


# Generate map based on selected version and options
@callback(
    Output('welcome-map', 'figure'),
    [Input('version-store', 'data'),
     Input('pollutant-selector', 'value'),
     Input('crossfilter-year--slider', 'value'),
     Input('health-metricshome', 'value')]
)
def generate_combined_graph(version, pollutant, year_value, metric):
    if not pollutant or not metric or not year_value:
        return go.Figure()  # Return empty figure if anything missing

    plot = df.query('Year == @year_value').copy()

    if version == '1':
        # Use standard metric logic
        if metric != 'Concentration':
            axis_plot = f"{metric}_{pollutant}"
        else:
            axis_plot = V1_COLUMN_MAPPING[pollutant]
        limits = m_limits
        unit_label = const.UNITS[metric][pollutant]
    else:
        # Version 2 always uses Concentration and column mapping
        axis_plot = V2_COLUMN_MAPPING[pollutant]
        metric = 'Concentration'
        limits = m_limits_v2
        unit_label = const.UNITS_V2[metric][pollutant] 

    # Prepare hover text
    plot['Text'] = '<b>' + plot['CityCountry'] + '</b><br>' + unit_label + ': ' + plot[axis_plot].round(2).astype(str)

    # Separate C40 and non-C40
    p1 = plot[plot['C40'] == False].copy().dropna(subset=[axis_plot])
    p2 = plot[plot['C40'] == True].copy().dropna(subset=[axis_plot])

    # Create base map
    fig = go.Figure(data=go.Scattergeo(
        lon=p1['Longitude'],
        lat=p1['Latitude'],
        text=p1['Text'],
        hoverinfo='text',
        name='Non-C40 Cities',
        marker=dict(
            colorscale=const.CS[metric],
            cmin=0,
            color=p1[axis_plot],
            symbol='circle',
            line_width=0,
            cmax=limits[metric][pollutant],
            colorbar_title=dict(text=unit_label, side='right'),
            size=3
        )
    ))

    fig.add_trace(go.Scattergeo(
        lon=p2['Longitude'],
        lat=p2['Latitude'],
        text=p2['Text'],
        hoverinfo='text',
        name='C40 Cities',
        marker=dict(
            colorscale=const.CS[metric],
            cmin=0,
            color=p2[axis_plot],
            symbol='diamond',
            size=5,
            line_width=1,
            line_color='#525151',
            cmax=limits[metric][pollutant],
            colorbar_title=dict(text=unit_label, side='right')
        )
    ))

    fig.update_layout(
        legend=dict(
            bgcolor=const.DISP['fades'],
            borderwidth=2, bordercolor=const.DISP['fades'],
            font=dict(size=15, color='white', family='Helvetica, sans-serif')
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
        plot_bgcolor='white',
        paper_bgcolor='white',
        template='simple_white',
        legend_x=0,
        legend_y=0.5,
        legend_title_text=' * Click to isolate cities  ',
        margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
        hovermode='closest',
        font=dict(size=const.FONTSIZE, family=const.FONTFAMILY)
    )

    fig.update_geos(showframe=False)
    return fig


# 2. PERCENT CHANGE TAB CALLBACK
@callback(
    Output('percent-change', 'figure'),
    [Input('pollutant-selector', 'value'),
     Input('version-store', 'data')]
)
def generate_pcgraph(pollutant, version):
    """
    Generate the percent change map based on selected pollutant and version
    
    Args:
        pollutant (str): Selected pollutant (PM, NO2, O3, CO2)
        version (str): Data version ('1' or '2')
        
    Returns:
        go.Figure: Plotly figure object with the percent change map
    """
    # Get the appropriate column based on version and pollutant
    if version == '1':
        # Use standard column for Version 1
        yaxis_column_name = V1_COLUMN_MAPPING[pollutant]
        plot = data_prep.DF_CHANGE
        unit_label = const.UNITS_PC[pollutant]

    else:
        # Use V2 column for Version 2
        yaxis_column_name = V2_COLUMN_MAPPING[pollutant]
        plot = data_prep.DF_CHANGE_V2
        unit_label = const.UNITS_PC_V2[pollutant]  
              
    plot['Text'] = '<b>' + plot['CityCountry'] + '</b><br>' + unit_label + ': ' + plot[
        yaxis_column_name].round(2).astype(str)
    
    # Separate C40 and non-C40 cities
    p1 = plot[plot['C40'] == False].copy().dropna(subset=[yaxis_column_name])
    p2 = plot[plot['C40'] == True].copy().dropna(subset=[yaxis_column_name])
    
    # Create the figure
    fig = go.Figure(data=go.Scattergeo(
        lon=p1['Longitude'],
        lat=p1['Latitude'],
        text=p1['Text'],
        hoverinfo='text',
        name='Non-C40 Cities',
        marker=dict(
            colorscale=[[0, '#072aed'], [0.5, 'white'],
                       [1, '#c70f02']],  # 'RdBu_r',
            cmin=-50,
            line_width=0,
            color=p1[yaxis_column_name],
            symbol='circle',
            cmax=50,
            colorbar_title=dict(text=unit_label, side='right'),
            size=3
        )))
    
    fig.add_trace(go.Scattergeo(
        lon=p2['Longitude'],
        lat=p2['Latitude'],
        text=p2['Text'],
        hoverinfo='text',
        name='C40 Cities',
        marker=dict(
            colorscale=[[0, 'blue'], [0.5, 'white'],
                       [1, 'red']],  # 'RdBu_r',
            cmin=-50,
            color=p2[yaxis_column_name],
            symbol='diamond',
            size=5,
            line_width=1,
            line_color='#525151',
            cmax=50,
            colorbar_title=dict(text=unit_label, side='right'),
        )))
    
    # Update layout
    fig.update_layout(
        legend=dict(bgcolor=const.DISP['fades'],
                    bordercolor=const.DISP['fades'],
                    borderwidth=2,
                    font=dict(size=15, color='white', family='Helvetica, sans-serif')),
        geo=dict(
            showland=True,
            landcolor=const.MAP_COLORS['lake'],
            coastlinewidth=0,
            oceancolor=const.MAP_COLORS['ocean'],
            subunitcolor=const.MAP_COLORS['land'],
            countrycolor=const.MAP_COLORS['land'],
            countrywidth=0.5,
            showlakes=True,
            lakecolor=const.MAP_COLORS['ocean'],
            showocean=True,
            showcountries=True,
            resolution=50,
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        template='simple_white',
        legend_x=0,
        legend_y=0.5,
        legend_title_text=' * Click to isolate cities  ',
        margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
        hovermode='closest',
        font=dict(size=const.FONTSIZE, family=const.FONTFAMILY))

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    return fig

# 4. DATA DOWNLOAD TAB CALLBACKS
# Creates dropdown list based on selected country
@callback(
    [Output("CitySe", "options"),
     Output("CitySe", "value")],
    Input("CountrySe", "value")
)
def chained_callback_city(country):
    dff = copy.deepcopy(df)
    if country is not None:
        dff = dff.query("Country == @country")
    return sorted(dff["CityCountry"].unique()), None

# Filter data table
@callback(
    Output("download-filtered-data", "data"),
    Input("download-button", "n_clicks"),
    State("filtered-data-table", "derived_virtual_data"),
    prevent_initial_call=True,
)
def download_data(n_clicks, data):
    if not data:
        return None
    dff = pd.DataFrame(data)
    return dcc.send_data_frame(dff.to_csv, "filtered_csv.csv")

@callback(
    Output("filtered-data-table", "data"),
    [Input('year-from-dropdown', "value"),
     Input('year-to-dropdown', "value"),
     Input('CountrySe', "value"),
     Input('CitySe', "value")],
)
def update_table(year_from, year_to, country, city):
    # Ensure year_from is not greater than year_to
    if year_from > year_to:
        year_from, year_to = year_to, year_from
        
    if city is None and country is not None:
        dff = df.query('Country==@country')
    elif city is not None:
        dff = df.query('CityCountry==@city')
    else:
        dff = df.copy()
    
    dff = dff[dff.Year.between(year_from, year_to)]
    return dff.to_dict("records")

@callback(
    [Output('year-to-dropdown', 'options'),
     Output('year-to-dropdown', 'value')],
    [Input('year-from-dropdown', 'value')],
    [State('year-to-dropdown', 'value')]
)
def update_year_to_options(selected_from_year, current_to_value):
    """
    Updates the available options in the "To" year dropdown based on
    the selected "From" year to prevent invalid date ranges.
    
    Args:
        selected_from_year: The year selected in the "From" dropdown
        current_to_value: The current value of the "To" dropdown
        
    Returns:
        tuple: (new options list, new dropdown value)
    """
    # Create options for years from the selected "From" year to 2020
    filtered_options = [
        {'label': str(year), 'value': year} 
        for year in range(selected_from_year, 2021)
    ]
    
    # If current "To" value is less than selected "From" year,
    # update it to the selected "From" year
    if current_to_value < selected_from_year:
        return filtered_options, selected_from_year
    
    # Otherwise keep the current "To" value
    return filtered_options, current_to_value


# TAB CONTENT CALLBACK
@callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab")]
)
def render_tab_content(active_tab):
    """
    This callback takes the 'active_tab' property as input and renders 
    the appropriate content for the selected tab.
    """
    if active_tab is not None:
        # 1. MAP TAB
        if active_tab == "welcome_map":
            return [
                html.Div([
                    version_selector,
                    pollutant_selector,
                    metrics
                ], className="control-panel"),
                
                # Map and slider remain the same
                dbc.Row(graph),
                dbc.Row(dbc.Col(slider))
            ]
        
        # 2. PERCENT CHANGE TAB    
        elif active_tab == "percent_change":
            return [
                html.Div([
                    version_selector,
                    pollutant_selector,
                    buttons.percent_change_metric()
                ], className="control-panel"),
        dbc.Row(pc_graph)
    ]
        
        # 3. DATA CODEBOOK TAB
        elif active_tab == 'codebook':
            return [dbc.Row(
                dbc.Stack([
                    dbc.Row(tt), 
                    dbc.Row(html.Hr()), 
                    dbc.Row(dbc.Col(table)),
                    dbc.Row(download), 
                ], gap=2)
            )]
        
        # 4. DATA DOWNLOAD TAB
        elif active_tab == 'download':
            return dbc.Stack([
                dbc.Row(
                    dbc.Col(
                        html.Div([
                            html.H5([
                                "Select country, city and/or year range to see the filtered dataset, and click the button below to download it.",
                                html.Br(),
                                html.Span("(* The full/unfiltered dataset can be downloaded in [Data Codebook].)", 
                                        style={'fontSize': '0.8em', 'fontFamily': 'Helvetica, Arial, sans-serif', 'fontWeight': 'normal'}),
                            ], style={
                                'color': const.DISP['text'],
                                'fontFamily': 'Helvetica, Arial, sans-serif',
                                'fontSize': '21px',
                                'textAlign': 'left',
                                'fontWeight': 'bold'
                            })
                        ],
                        style={
                            'backgroundColor': '#f0f4f8',
                            'padding': '15px',
                            'borderRadius': '6px',
                            'marginBottom': '5px'
                        })
                    )
                ),
                dbc.Row([
                    country_dropdown,
                    city_dropdown,
                    year_from_dropdown,
                    year_to_dropdown
                ], className="mb-4"),  
                dbc.Row(dtable),
                dbc.Row(download_button),
                dbc.Row(download_component)
            ], gap=2)

        # 6. ABOUT TAB
        elif active_tab == "about":
            return [dbc.Row(dbc.Col(about_acc))]

    return "Content coming soon."
