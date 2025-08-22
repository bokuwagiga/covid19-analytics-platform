import requests
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from src.config.config import EXCESS_MORTALITY_PAGE, API_BASE
from src.components.comments import CommentsSection, register_comment_callbacks
from src.utils import get_country_list

# register this page
dash.register_page(__name__, path=f"/dashboards/{EXCESS_MORTALITY_PAGE}", name="Excess Mortality")



COUNTRIES = get_country_list(table="ECDC_GLOBAL", include_world=False)


# layout
layout = dbc.Container([

    # page title
    dbc.Row([
        dbc.Col(html.H1("COVID-19 Excess Mortality Dashboard", className="text-center"), width=12)
    ], className="mb-4 mt-2"),

    # country dropdown
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="country-dropdown",
                options=[{"label": c, "value": c} for c in COUNTRIES],
                value=COUNTRIES[0] if COUNTRIES else "Lithuania",
                placeholder="Select a country",
                style={"width": "100%"}
            )
        ], width=6)
    ], className="mb-4"),

    # graph + comments
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dcc.Graph(id="mortality-graph", style={"height": "500px"}),
                className="shadow-sm",
                style={"borderRadius": "12px", "overflow": "hidden"}
            ),
            width=12, lg=8
        ),
        CommentsSection("excess-mortality", country_dropdown_id="country-dropdown")
    ])
], fluid=True)


# callback to update graph
@dash.callback(
    Output("mortality-graph", "figure"),
    Input("country-dropdown", "value")
)
def update_mortality_chart(country):
    """
    Updates the mortality chart when a country is selected
    """

    # handle case when no country is selected
    if not country:
        return go.Figure().update_layout(
            title="Please select a country to see the data",
            template="plotly_dark",
            height=500
        )

    # fetch data for selected country
    covid_resp = requests.get(f"{API_BASE}/{EXCESS_MORTALITY_PAGE}", params={"country": country})

    if covid_resp.status_code != 200:
        return go.Figure().update_layout(title="Error fetching data")

    covid_data = covid_resp.json()
    if not covid_data or isinstance(covid_data, dict) and "error" in covid_data:
        return go.Figure().update_layout(title="No data available")

    # extract data for plotting
    dates = [d["date"] for d in covid_data]
    deaths_all = [d["deaths_allcause"] for d in covid_data]
    deaths_counterfactual = [d["deaths_without_covid"] for d in covid_data]
    deaths_covid = [d["deaths_covid"] for d in covid_data]

    # build figure with three lines
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=deaths_all, mode="lines+markers", name="Observed all-cause deaths"))
    fig.add_trace(go.Scatter(x=dates, y=deaths_counterfactual, mode="lines", name="Counterfactual (no COVID)",
                             line=dict(dash="dash")))
    fig.add_trace(go.Scatter(x=dates, y=deaths_covid, mode="lines", name="Reported COVID deaths", line=dict(color="red")))

    # update chart style
    fig.update_layout(
        title=f"Mortality Trends in {country}",
        xaxis_title="Date",
        yaxis_title="Deaths",
        template="plotly_dark",
        hovermode="x unified",
        height=500,
        margin=dict(l=10, r=10, t=40, b=20)
    )

    return fig


# register reusable comment callbacks for this page
register_comment_callbacks("excess-mortality", country_dropdown_id="country-dropdown")
