#dash/src/pages/mortality_forecast.py
import requests
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from shared.utils import get_country_list
from shared.config.config import API_BASE, MORTALITY_FORECAST_PAGE
from components.comments import CommentsSection, register_comment_callbacks

dash.register_page(__name__, path=f"/analytics/{MORTALITY_FORECAST_PAGE}", name="Excess Mortality Forecasting")

COUNTRIES = get_country_list(table="ECDC_GLOBAL", include_world=False)
COUNTRIES.insert(0, "World")

layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            [
                html.H1("Excess Mortality Forecasting (Expected vs Observed)", className="text-center"),
                html.H4("What if there was no Covid-19", className="text-center d-block text-muted")
            ],
            width=12
        ), ], className="mb-4 mt-2"),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="forecast-country-dropdown",
                options=[{"label": c, "value": c} for c in COUNTRIES],
                value=COUNTRIES[0] if COUNTRIES else "World",
                style={"width": "100%"}
            )
        ], width=6)
    ], className="mb-4"),

    # KPI cards row
    dbc.Row(id="forecast-kpis", className="mb-4"),

    dbc.Row([
        dbc.Col(
            dbc.Card(
                dcc.Graph(id="forecast-graph", style={"height": "500px"}),
                className="shadow-sm mb-3",
                style={"borderRadius": "12px", "overflow": "hidden"}
            ),
            width=12, lg=8
        ),
        CommentsSection(MORTALITY_FORECAST_PAGE, country_dropdown_id="forecast-country-dropdown")
    ])
], fluid=True)


@dash.callback(
    [Output("forecast-graph", "figure"),
     Output("forecast-kpis", "children")],
    Input("forecast-country-dropdown", "value")
)
def update_forecast(country):
    if not country:
        return go.Figure().update_layout(title="Select a country"), []

    resp = requests.get(f"{API_BASE}/{MORTALITY_FORECAST_PAGE}", params={"country": country})
    if resp.status_code != 200:
        return go.Figure().update_layout(title="Error fetching forecast"), []

    data = resp.json()
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])

    # prepare totals (same value repeated per row, just take first)
    observed_total = df["observed_total"].dropna().iloc[0] if "observed_total" in df else None
    forecast_total = df["forecast_total"].dropna().iloc[0] if "forecast_total" in df else None

    # build figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["observed"],
        mode="lines+markers", name="Observed deaths",
        line=dict(color="red")
    ))
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["forecast"],
        mode="lines", name="Forecasted baseline (expected deaths)",
        line=dict(dash="dot", color="blue")
    ))
    fig.update_layout(
        title=f"Observed vs Forecasted Baseline Mortality ({country})",
        xaxis_title="Date",
        yaxis_title="Deaths",
        template="plotly_dark",
        hovermode="x unified",
        height=500
    )

    # KPI cards for totals
    kpis = dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4("Observed Deaths (2020–2021)", className="card-title"),
            html.H2(f"{int(observed_total):,}" if observed_total else "N/A", className="text-danger")
        ]), className="shadow-sm"), md=6),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4("Forecasted Baseline (2020–2021)", className="card-title"),
            html.H2(f"{int(forecast_total):,}" if forecast_total else "N/A", className="text-primary")
        ]), className="shadow-sm"), md=6)
    ])

    return fig, kpis


# register reusable comment callbacks
register_comment_callbacks(MORTALITY_FORECAST_PAGE, country_dropdown_id="forecast-country-dropdown")
