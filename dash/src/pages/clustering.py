#dash/src/pages/clustering.py
import requests
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from shared.config.config import API_BASE, CLUSTERING_PAGE
from components.comments import CommentsSection, register_comment_callbacks

dash.register_page(__name__, path=f"/analytics/{CLUSTERING_PAGE}", name="Country Clustering")

layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            [
                html.H1("Clustering Countries by Excess Mortality (2020–2022)", className="text-center"),
                html.H4("Grouping countries by similar Covid-19 impact", className="text-center d-block text-muted")
            ],
            width=12
        )
    ], className="mb-4 mt-2"),

    dbc.Row([
        dbc.Col([
            html.Label("Select number of clusters:"),
            dcc.Slider(
                id="k-slider", min=2, max=6, step=1, value=3,
                marks={i: str(i) for i in range(2, 7)}
            )
        ], width=6)
    ], className="mb-4"),

    dbc.Row([
        # Left side: map + table + explanation
        dbc.Col([
            dbc.Card(
                dcc.Graph(id="cluster-map", style={"height": "500px"}),
                className="shadow-sm mb-3",
                style={"borderRadius": "12px", "overflow": "hidden"}
            ),
            dbc.Card(
                dbc.CardBody(html.Div(id="cluster-explanation")),
                className="shadow-sm"
            ),
            dbc.Card(
                dbc.CardBody(html.Div(id="cluster-table")),
                className="shadow-sm mb-3"
            )
        ], width=12, lg=8),

        # Right side: comments
        CommentsSection(CLUSTERING_PAGE, country_dropdown_id="clustering-filter-country")
    ])
], fluid=True)


@dash.callback(
    [Output("cluster-map", "figure"),
     Output("cluster-table", "children"),
     Output("cluster-explanation", "children")],
    Input("k-slider", "value")
)
def update_clusters(k):
    resp = requests.get(f"{API_BASE}/{CLUSTERING_PAGE}", params={"k": k})
    if resp.status_code != 200:
        return px.scatter(title="Error fetching clusters"), html.Div("Error"), "Error"

    df = pd.DataFrame(resp.json())

    # World map
    fig = px.choropleth(
        df,
        locations="country",
        locationmode="country names",
        color="cluster",
        hover_name="country",
        hover_data=[
            "deaths_2020_per100k", "deaths_2021_per100k", "deaths_2022_per100k",
            "cases_2020_per100k", "cases_2021_per100k", "cases_2022_per100k"
        ],
        title=f"Clusters of Countries by Covid-19 Impact (k={k})"
    )

    # Table
    table = dbc.Table.from_dataframe(
        df[["country", "cluster", "deaths_2020_per100k", "deaths_2021_per100k", "deaths_2022_per100k"]],
        striped=True, bordered=True, hover=True
    )

    explanations = []
    cluster_means = df.groupby("cluster")[[
        "deaths_2020_per100k", "deaths_2021_per100k", "deaths_2022_per100k",
        "cases_2020_per100k", "cases_2021_per100k", "cases_2022_per100k"
    ]].mean().reset_index()

    for _, row in cluster_means.iterrows():
        c = int(row["cluster"])
        d2020, d2021, d2022 = row["deaths_2020_per100k"], row["deaths_2021_per100k"], row["deaths_2022_per100k"]
        c2020, c2021, c2022 = row["cases_2020_per100k"], row["cases_2021_per100k"], row["cases_2022_per100k"]

        # mortality pattern
        if d2021 > d2020 * 1.5 and d2021 > d2022 * 1.5:
            mortality_pattern = "a **sharp mortality spike in 2021**"
        elif d2020 < d2021 < d2022:
            mortality_pattern = "a **steady increase in mortality**"
        elif d2020 > d2021 > d2022:
            mortality_pattern = "a **steady decrease in mortality**"
        else:
            mortality_pattern = "a **mixed mortality trend**"

        # cases intensity
        avg_cases = (c2020 + c2021 + c2022) / 3
        if avg_cases > 20000:
            case_level = "very high case rates"
        elif avg_cases > 10000:
            case_level = "moderate case rates"
        else:
            case_level = "relatively low case rates"

        explanations.append(
            html.P([
                html.Strong(f"Cluster {c}: "),
                f"Countries with {mortality_pattern}. ",
                f"On average, they had {case_level} "
                f"(~{c2020:,.0f} per 100k in 2020, {c2021:,.0f} in 2021, {c2022:,.0f} in 2022)."
            ])
        )

    return fig, table, dbc.Card(dbc.CardBody(explanations))


# register reusable comment callbacks
register_comment_callbacks(CLUSTERING_PAGE, country_dropdown_id="clustering-filter-country")
