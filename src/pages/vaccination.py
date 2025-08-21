import requests
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from src.config.config import API_BASE, VACCINATION_PAGE
from src.components.comments import CommentsSection, register_comment_callbacks
from src.utils import get_country_list

# register this page
dash.register_page(__name__, path=f"/dashboards/{VACCINATION_PAGE}", name="Vaccination Impact")


COUNTRIES = get_country_list(table="ECDC_GLOBAL")



# layout
layout = dbc.Container([

    # page title
    dbc.Row([
        dbc.Col(html.H1("COVID-19 Vaccination Dashboard", className="text-center"), width=12)
    ], className="mb-4 mt-2"),

    # country dropdown
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="vax-country-dropdown",
                options=[{"label": "World", "value": "World"}] + [{"label": c, "value": c} for c in COUNTRIES],
                value="World",
                placeholder='Select a country',
                style={"width": "100%"}
            )
        ], width=6)
    ], className="mb-4"),

    # graph + comments
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dcc.Graph(id="vaccination-graph", style={"height": "500px"}),
                className="shadow-sm",
                style={"borderRadius": "12px", "overflow": "hidden"}
            ),
            width=12, lg=8
        ),
        CommentsSection("vaccination", country_dropdown_id="vax-country-dropdown")
    ])
], fluid=True)


# callback to update vaccination graph
@dash.callback(
    Output("vaccination-graph", "figure"),
    Input("vax-country-dropdown", "value")
)
def update_vaccination_chart(country):
    """
    Updates the vaccination chart for the selected country
    shows partially vaccinated, fully vaccinated, and total doses per person
    """
    # handle missing selection
    if not country:
        return go.Figure().update_layout(
            title="Please select a country to see the data",
            template="plotly_dark",
            height=500
        )

    # fetch vaccination data
    resp = requests.get(f"{API_BASE}/{VACCINATION_PAGE}", params={"country": country})
    if resp.status_code != 200:
        return go.Figure().update_layout(title=f"Error fetching data: {resp.text}")

    try:
        data = resp.json()
    except Exception:
        return go.Figure().update_layout(title=f"Invalid response: {resp.text[:200]}")

    # handle no data
    if not data or isinstance(data, dict) and "error" in data:
        return go.Figure().update_layout(title="No vaccination data available")

    # extract fields from data
    dates = [d["date"] for d in data]
    people_vax = [d["PEOPLE_VACCINATED"] for d in data]
    fully_vax = [d["PEOPLE_FULLY_VACCINATED"] for d in data]
    total_vax = [d["TOTAL_VACCINATIONS"] for d in data]
    population = data[0].get("POPULATION")

    # normalize values to percent of population
    if population:
        people_vax_pct = [(p / population) * 100 if p else 0 for p in people_vax]
        fully_vax_pct = [(f / population) * 100 if f else 0 for f in fully_vax]
        doses_per_person_pct = [(tv / population) * 100 if tv else 0 for tv in total_vax]
    else:
        people_vax_pct, fully_vax_pct, doses_per_person_pct = [], [], []

    # build figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=people_vax_pct, mode="lines", name="≥1 Dose (% of population)"))
    fig.add_trace(go.Scatter(x=dates, y=fully_vax_pct, mode="lines", name="Fully Vaccinated (% of population)"))
    fig.add_trace(go.Scatter(
        x=dates, y=doses_per_person_pct, mode="lines",
        name="Total Doses per 100 People", line=dict(dash="dot"))
    )

    # reference lines at 100% and 200%
    fig.add_trace(go.Scatter(
        x=dates, y=[100]*len(dates),
        mode="lines", name="= 1 dose per person",
        line=dict(color="gray", dash="dash")
    ))
    fig.add_trace(go.Scatter(
        x=dates, y=[200]*len(dates),
        mode="lines", name="= 2 doses per person",
        line=dict(color="lightgray", dash="dot")
    ))

    # update chart style
    fig.update_layout(
        title=f"Vaccination Progress in {country}",
        xaxis_title="Date",
        yaxis_title="% of Population",
        template="plotly_dark",
        hovermode="x unified",
        height=500,
        yaxis=dict(range=[0, max(220, max(doses_per_person_pct or [0]))])  # keeps y-axis consistent
    )
    return fig


# register reusable comment callbacks
register_comment_callbacks("vaccination", country_dropdown_id="vax-country-dropdown")
