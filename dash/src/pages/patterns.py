import requests
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from shared.config.config import API_BASE, PATTERNS_PAGE

# Register page
dash.register_page(__name__, path=f"/analytics/{PATTERNS_PAGE}", name="Patterns")

# Layout
layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("COVID Patterns (Wave Detection)", className="text-center mb-4"), width=12)
    ]),

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

    dbc.Row([
        dbc.Col(
            dcc.Loading(
                type="circle",
                children=html.Div(id="patterns-output")
            ),
            width=10
        )
    ], className="justify-content-center mb-5")
], fluid=True)


#  Callbacks 

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
    Output("patterns-output", "children"),
    Input("patterns-run-btn", "n_clicks"),
    State("patterns-country-dropdown", "value"),
    prevent_initial_call=True
)
def detect_patterns(n_clicks, country):
    if not country:
        return html.Div("Please select a country", className="text-danger")

    resp = requests.get(f"{API_BASE}/{PATTERNS_PAGE}", params={"country": country})
    if resp.status_code != 200:
        return html.Div(f"Error: {resp.text}", className="text-danger")

    waves = resp.json()
    if not waves:
        return html.Div("No patterns detected for this country.", className="text-warning")

    # Plot patterns on timeline
    fig = go.Figure()
    for wave in waves:
        fig.add_vrect(
            x0=wave["wave_start"], x1=wave["wave_end"],
            fillcolor="LightSkyBlue", opacity=0.3,
            annotation_text=f"Peak: {wave['PEAK_CASES']}", annotation_position="top left"
        )

    fig.update_layout(
        title=f"Detected COVID Waves in {country}",
        xaxis_title="Date",
        yaxis_title="Cases",
        template="plotly_white"
    )

    return dcc.Graph(figure=fig)
