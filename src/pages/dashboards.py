from dash import html
import dash_bootstrap_components as dbc
import dash
from src.config.config import DASHBOARDS_LIST

# register this page with dash
dash.register_page(__name__, path="/dashboards", name="Dashboards")

# create links for each dashboard in the list
dashboard_links = [
    dbc.NavLink(
        dashboard.title().replace('-', ' ').replace('_', ' '),  # format title
        href=f"/dashboards/{dashboard}",  # link to dashboard page
        className="btn text-white bg-dark common-hover",
        style={"padding": "10px 15px", "margin-bottom": "5px", "border-radius": "5px"}
    )
    for dashboard in set(DASHBOARDS_LIST)  # avoid duplicates
]

# layout for dashboards page
layout = dbc.Container(
    [
        html.H2("Dashboards", className="text-center mt-5"),
        dbc.Nav(
            dashboard_links,
            vertical=True,  # stack links vertically
            pills=True,
            className="flex-column"
        )
    ], fluid=True, style={"padding-top": "50px"}
)
