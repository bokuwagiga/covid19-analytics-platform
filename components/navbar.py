# components/navbar.py
import os

import dash_bootstrap_components as dbc
from dotenv import load_dotenv

load_dotenv('config/.env')
COVID_MORTALITY_COMPARISON = os.getenv('COVID_MORTALITY_COMPARISON')

def get_navbar():
    return dbc.Navbar(
        dbc.Container(
            [
                dbc.NavbarBrand("COVID-19 Dashboard", href="/", className="text-white fw-bold"),
                dbc.Nav(
                    [
                        dbc.NavLink("Home", href="/", className="text-white me-3"),
                        dbc.NavLink("COVID Dashboard", href=f"/{COVID_MORTALITY_COMPARISON}", className="text-white me-3"),
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
