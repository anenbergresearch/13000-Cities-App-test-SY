from dash import html
import dash_bootstrap_components as dbc

MILKEN_LOGO = "assets/milken_institute.png"
HAQAST_LOGO = "assets/HAQAST.png"
REACH_LOGO = "assets/REACH.jpg"

# Create logo row
logos = dbc.Row([
    dbc.Col(html.Img(src=MILKEN_LOGO, height="50px")),
    dbc.Col(html.Img(src=HAQAST_LOGO, height="50px")),
    dbc.Col(html.Img(src=REACH_LOGO, height="50px")),
], className="ms-auto flex-nowrap mt-3 mt-md-0", align="center")

def Navbar():
    navbar = dbc.Navbar(
        [
            dbc.Container(
                [
                    # App title as a static text element
                    html.Span(
                        "Urban Air Quality Explorer", 
                        style={
                            'color': 'white', 
                            'fontSize': '1.25rem', 
                            'fontWeight': 'bold',
                            'marginRight': '20px',
                            'fontFamily': 'Helvetica, Arial, sans-serif'
                        }
                    ),
                    
                    # Navbar toggle for responsive design
                    dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                    
                    # Navigation items and logos on the right
                    dbc.Collapse(
                        dbc.Nav(
                            [
                                dbc.NavItem(dbc.NavLink("Home", href="/", style={'fontSize': '0.95rem'})),
                                dbc.NavItem(dbc.NavLink("Networks", href="/networks", style={'fontSize': '0.95rem'})),
                                dbc.NavItem(dbc.NavLink("Countries", href="/countries", style={'fontSize': '0.95rem'})),
                                dbc.NavItem(dbc.NavLink("States", href="/states", style={'fontSize': '0.95rem'})),
                                # Logos from the new code
                                dbc.NavItem(logos)
                            ],
                            className="ms-auto",  # Align to the right
                            navbar=True
                        ),
                        id="navbar-collapse",
                        navbar=True,
                    )
                ],
                fluid=True
            )
        ],
        color="rgba(3, 60, 90,0.9)",
        dark=True,
        sticky="top",
        expand="lg"  # Allow responsive collapse
    )
    return navbar