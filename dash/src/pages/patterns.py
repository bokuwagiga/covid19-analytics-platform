# dash/src/pages/patterns.py
import requests
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from shared.config.config import API_BASE, PATTERNS_PAGE
from src.components.comments import CommentsSection, register_comment_callbacks

# Register page
dash.register_page(__name__, path=f"/analytics/{PATTERNS_PAGE}", name="Patterns")

# Layout
layout = dbc.Container([

    dbc.Row([
        dbc.Col(html.H1("COVID Patterns (Wave Detection)", className="text-center mb-2"), width=12),
    ]),
    dbc.Row([
        dbc.Col(html.P(
            "This dashboard detects and highlights distinct COVID-19 waves based on reported cases.",
            className="text-center text-muted mb-4"
        ), width=12)
    ]),

    # Controls row
    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                id="patterns-country-dropdown",
                placeholder="Select a country",
                style={"minWidth": "300px"}
            ),
            width=6
        ),
        dbc.Col(
            dbc.Button("Detect Patterns", id="patterns-run-btn", color="primary"),
            width="auto"
        )
    ], className="justify-content-center mb-4"),

    # Graph + comments
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dcc.Loading(
                    type="circle",
                    children=dcc.Graph(id="patterns-graph", style={"height": "500px"})
                ),
                className="shadow-sm mb-3",
                style={"borderRadius": "12px", "overflow": "hidden"}
            ),
            width=12, lg=8
        ),
        CommentsSection(PATTERNS_PAGE, country_dropdown_id="patterns-country-dropdown")
    ])
], fluid=True)


# Callbacks
@dash.callback(
    Output("patterns-country-dropdown", "options"),
    Input("patterns-country-dropdown", "id")
)
def load_countries(_):
    """Load country options from API"""
    try:
        resp = requests.get(f"{API_BASE}/countries?table=ECDC_GLOBAL_WEEKLY")
        if resp.status_code == 200:
            countries = resp.json()
            return [{"label": c, "value": c} for c in countries]
    except Exception:
        return []
    return []


@dash.callback(
    Output("patterns-graph", "figure"),
    Input("patterns-run-btn", "n_clicks"),
    State("patterns-country-dropdown", "value"),
    prevent_initial_call=False
)
def detect_patterns(n_clicks, country):
    if not country:
        # Default placeholder when no country is selected
        fig = px.scatter(title="Please select a country to view detected COVID-19 waves.")
        fig.update_layout(
            template="plotly_dark",
            height=500,
            margin=dict(l=10, r=10, t=40, b=20)
        )
        return fig

    resp = requests.get(f"{API_BASE}/{PATTERNS_PAGE}", params={"country": country})
    if resp.status_code != 200:
        return px.scatter(title=f"Error: {resp.text}")

    waves = resp.json()
    if not waves:
        return px.scatter(title="No patterns detected for this country.")

    # Convert to DataFrame
    df = pd.DataFrame(waves)
    df["wave_start"] = pd.to_datetime(df["wave_start"])
    df["wave_end"] = pd.to_datetime(df["wave_end"])

    # Base line chart
    fig = px.line(
        df.sort_values("wave_start"),
        x="wave_start",
        y="PEAK_CASES",
        markers=True,
        title=f"Detected COVID Waves in {country}"
    )

    # Add shaded wave periods
    for _, row in df.iterrows():
        fig.add_vrect(
            x0=row["wave_start"],
            x1=row["wave_end"],
            fillcolor="LightSkyBlue",
            opacity=0.2,
            line_width=0
        )

    # Style to match other dashboards
    fig.update_layout(
        template="plotly_dark",
        hovermode="x unified",
        xaxis_title="Date",
        yaxis_title="Peak Cases",
        height=500,
        margin=dict(l=10, r=10, t=40, b=20)
    )

    return fig


# Register reusable comment callbacks
register_comment_callbacks(PATTERNS_PAGE, country_dropdown_id="patterns-country-dropdown")
