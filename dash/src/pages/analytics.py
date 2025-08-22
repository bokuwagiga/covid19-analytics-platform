# dash/src/pages/analytics.py
from dash import html
import dash_bootstrap_components as dbc
import dash
from shared.config.config import ANALYTICS_LIST

# register this page with dash
dash.register_page(__name__, path="/analytics", name="Analytics")

# create links for each analytic in the list
analytics_links = [
    dbc.NavLink(
        analytic.title().replace('-', ' ').replace('_', ' '),  # format title
        href=f"/analytics/{analytic}",  # link to analytic page
        className="btn text-white bg-dark common-hover",
        style={"padding": "10px 15px", "margin-bottom": "5px", "border-radius": "5px"}
    )
    for analytic in set(ANALYTICS_LIST)  # no duplicates
]

# layout for analytics page
layout = dbc.Container(
    [
        html.H2("Analytics", className="text-center mt-5"),
        dbc.Nav(
            analytics_links,
            vertical=True,  # stack links vertically
            pills=True,
            className="flex-column"
        )
    ], fluid=True, style={"padding-top": "50px"}
)
