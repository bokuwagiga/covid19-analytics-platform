#dash/src/pages/infection_deaths.py

import requests
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from shared.config.config import API_BASE, INFECTION_DEATHS_PAGE
from components.comments import CommentsSection, register_comment_callbacks
from shared.utils import get_country_list

# register this page
dash.register_page(__name__, path=f"/dashboards/{INFECTION_DEATHS_PAGE}", name="Infection Deaths")


COUNTRIES = get_country_list(table="ECDC_GLOBAL_WEEKLY", include_world=True)



# layout
layout = dbc.Container([

    # page title
    dbc.Row([
        dbc.Col(html.H1("COVID-19 Deaths Trends", className="text-center"), width=12)
    ], className="mb-4 mt-2"),

    # country dropdown
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="deaths-country-dropdown",
                options=[{"label": c, "value": c} for c in COUNTRIES],
                value=COUNTRIES[0] if COUNTRIES else "World",
                placeholder="Select a country",
                style={"width": "100%"}
            )
        ], width=6),
    ], className="mb-4"),

    # graph + comments
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dcc.Graph(id="deaths-graph", style={"height": "600px"}),
                className="shadow-sm mb-3",
                style={"borderRadius": "12px", "overflow": "hidden"}
            ),
            width=12, lg=8
        ),
        CommentsSection(INFECTION_DEATHS_PAGE, country_dropdown_id="deaths-country-dropdown")
    ])
], fluid=True)


# callback to update the deaths graph
@dash.callback(
    Output("deaths-graph", "figure"),
    [Input("deaths-country-dropdown", "value")]
)
def update_deaths_chart(country):
    """
    Updates the weekly and cumulative deaths chart
    based on the selected country
    """
    # handle missing selection
    if not country:
        return go.Figure().update_layout(
            title="Please select a country to see the data",
            template="plotly_dark",
            height=600
        )

    # fetch data from API
    resp = requests.get(f"{API_BASE}/{INFECTION_DEATHS_PAGE}", params={"country": country})
    if resp.status_code != 200:
        return go.Figure().update_layout(title=f"Error fetching data: {resp.text}")

    try:
        data = resp.json()
    except Exception:
        return go.Figure().update_layout(title=f"Invalid response: {resp.text[:200]}")

    # handle empty or error responses
    if not data or isinstance(data, dict) and "error" in data:
        return go.Figure().update_layout(title="No infection data available")

    df = pd.DataFrame(data)
    if df.empty:
        return go.Figure().update_layout(title="No data available")

    # format dates and compute metrics
    df["date"] = pd.to_datetime(df["DATE"]).dt.strftime("%Y-%m-%d")
    df["new_deaths"] = df["DEATHS_WEEKLY"].clip(lower=0)
    df["cumulative_deaths"] = df["new_deaths"].cumsum()

    # build figure
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["date"], y=df["new_deaths"],
        name="Weekly New Deaths",
        marker_color="crimson",
        opacity=0.6,
        yaxis="y1"
    ))
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["cumulative_deaths"],
        name="Cumulative Deaths",
        mode="lines",
        line=dict(color="purple", dash="dot"),
        yaxis="y2"
    ))

    # update chart style
    fig.update_layout(
        title=f"COVID-19 Weekly & Cumulative Deaths in {country}",
        xaxis=dict(title="Week"),
        yaxis=dict(title="Weekly deaths", side="left"),
        yaxis2=dict(title="Cumulative deaths", overlaying="y", side="right"),
        template="plotly_dark",
        hovermode="x unified",
        height=600
    )
    return fig


# register reusable comment callbacks
register_comment_callbacks(INFECTION_DEATHS_PAGE, country_dropdown_id="deaths-country-dropdown")
