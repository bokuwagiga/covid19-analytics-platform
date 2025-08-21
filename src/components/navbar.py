import dash_bootstrap_components as dbc


def get_navbar():
    """
    Creates the top navigation bar
    Contains links to Home, Dashboards, and About
    """
    return dbc.Navbar(
        dbc.Container(
            [
                # app title
                dbc.NavbarBrand("COVID-19 Dashboard", href="/", className="text-white fw-bold"),

                # navigation links
                dbc.Nav(
                    [
                        dbc.NavLink("Home", href="/", className="text-white me-3"),
                        dbc.NavLink("Dashboards", href="/dashboards", className="text-white me-3"),
                        dbc.NavLink("About", href="/about", className="text-white"),
                    ],
                    pills=True,
                ),
            ],
            fluid=True,
        ),
        color="dark",
        dark=True,
        className="mb-0",
        style={"padding": "1rem 2rem"},
    )
