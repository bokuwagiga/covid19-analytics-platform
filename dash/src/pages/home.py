# dash/src/pages/home.py
import requests
import dash
from dash import html
import dash_bootstrap_components as dbc
from shared.config.config import API_BASE, INFECTION_CASES_PAGE, INFECTION_DEATHS_PAGE

# register this page as home
dash.register_page(__name__, path="/")

def fetch_world_highlight():
    """Fetch latest global snapshot from API"""
    try:
        cases = requests.get(f"{API_BASE}/{INFECTION_CASES_PAGE}", params={"country": "World"}).json()
        deaths = requests.get(f"{API_BASE}/{INFECTION_DEATHS_PAGE}", params={"country": "World"}).json()
        latest_cases = cases[-1] if cases else {}
        latest_deaths = deaths[-1] if deaths else {}
        return {
            "cases": latest_cases.get("CASES_WEEKLY", "N/A"),
            "deaths": latest_deaths.get("DEATHS_WEEKLY", "N/A"),
        }
    except Exception:
        return {"cases": "N/A", "deaths": "N/A"}

highlight = fetch_world_highlight()

layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("COVID-19 Data Analytics Platform", className="text-center mb-3"), width=12),
    ]),
    dbc.Row([
        dbc.Col(html.P(
            "An integrated platform combining Snowflake, MongoDB, and Python to explore "
            "COVID-19 data with interactive dashboards and APIs.",
            className="lead text-center"
        ), width=12)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dbc.Card(
            dbc.CardBody([
                html.H4("Latest Weekly Cases", className="card-title"),
                html.H2(f"{highlight['cases']:,}" if isinstance(highlight['cases'], int) else highlight['cases'],
                        className="text-primary")
            ]), className="shadow-sm text-center"), md=6),

        dbc.Col(dbc.Card(
            dbc.CardBody([
                html.H4("Latest Weekly Deaths", className="card-title"),
                html.H2(f"{highlight['deaths']:,}" if isinstance(highlight['deaths'], int) else highlight['deaths'],
                        className="text-danger")
            ]), className="shadow-sm text-center"), md=6),
    ], className="mb-5 justify-content-center")
], fluid=True)
