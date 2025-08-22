# dash/src/pages/eda.py

import requests
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from shared.config.config import API_BASE, API_BASE_EXTERNAL

# Register page
dash.register_page(__name__, path="/analytics/eda", name="Exploratory Data Analysis")

# Layout
layout = dbc.Container([

    # Title
    dbc.Row([
        dbc.Col(html.H1("Exploratory Data Analysis (EDA)", className="text-center mb-4"), width=12)
    ]),

    # Controls row (dropdown + button + spinner next to button)
    # Controls row (dropdown + button + spinner)
    dbc.Row(
        [
            dbc.Col(
                dcc.Loading(
                    type="circle",
                    color="#0d6efd",
                    children=dcc.Dropdown(
                        id="eda-table-dropdown",
                        placeholder="Choose a Snowflake table",
                        style={"minWidth": "300px"}
                    ),
                    style={"display": "block"}
                ),
                width=6
            ),
            dbc.Col(
                html.Div(
                    [
                        dbc.Button("Run EDA", id="eda-run-btn", color="primary", className="me-3"),
                        dcc.Loading(
                            type="circle",
                            color="#0d6efd",
                            children=html.Div(id="eda-output"),
                            style={"display": "inline-block", "verticalAlign": "middle", "marginLeft": "25px"}
                        )
                    ],
                    style={"display": "flex", "alignItems": "center"}
                ),
                width="auto"
            )
        ],
        className="mb-4 justify-content-center align-items-center",
    ),
    # Download report button
    dbc.Row(
        dbc.Col(
            html.A(
                "Download More Detailed Report",
                id="eda-download-btn",
                className="btn btn-secondary disabled",
                href="#",
                target="_blank"  # open in new tab
            ),
            width="auto",
            className="text-center"
        ),
        className="justify-content-center mt-4 mb-5"
    ),
    # Results section
    dbc.Row(
        dbc.Col(
            html.Div(id="eda-results"),  # results shown here
            width=10
        ),
        className="justify-content-center mb-4 mt-4"
    )


], fluid=True)


# --- Callbacks ---

@dash.callback(
    Output("eda-table-dropdown", "options"),
    Input("eda-table-dropdown", "id")
)
def load_tables(_):
    """Fetch available tables from API"""
    try:
        resp = requests.get(f"{API_BASE}/eda/tables")
        if resp.status_code == 200:
            tables = resp.json()
            return [{"label": t, "value": t} for t in tables]
    except Exception:
        return []
    return []


@dash.callback(
    [
        Output("eda-output", "children"),        # 👈 dummy div to trigger spinner
        Output("eda-results", "children"),       # 👈 actual results below
        Output("eda-download-btn", "className"),
        Output("eda-download-btn", "href")
    ],
    Input("eda-run-btn", "n_clicks"),
    State("eda-table-dropdown", "value"),
    prevent_initial_call=True
)
def run_eda(n_clicks, table):
    """Run EDA and display results, enable download button"""
    if not table:
        return "", html.Div("Please select a table", className="text-danger"), "btn btn-secondary disabled", "#"

    resp = requests.get(f"{API_BASE}/eda", params={"table": table})
    if resp.status_code != 200:
        return "", html.Div(f"Error: {resp.text}", className="text-danger"), "btn btn-secondary disabled", "#"

    results = resp.json()

    # Build output tables
    summary = pd.DataFrame(results["summary_stats"]).round(2).reset_index()
    missing = pd.DataFrame(list(results["missing_values"].items()), columns=["Column", "Missing Values"])
    corr = pd.DataFrame(results["correlations"]).round(2)

    output = dbc.Container([
        html.H4("Shape:"),
        html.P(f"{results['shape'][0]} rows × {results['shape'][1]} columns"),

        html.H4("Columns:"),
        dbc.Table.from_dataframe(
            pd.DataFrame(list(results["columns"].items()), columns=["Column", "Type"]),
            striped=True, bordered=True, hover=True
        ),

        html.H4("Missing Values:"),
        dbc.Table.from_dataframe(missing, striped=True, bordered=True, hover=True),

        html.H4("Summary Statistics:"),
        dbc.Table.from_dataframe(summary, striped=True, bordered=True, hover=True),

        html.H4("Correlations:"),
        dbc.Table.from_dataframe(corr, striped=True, bordered=True, hover=True),
    ])

    # Enable download
    download_url = f"{API_BASE_EXTERNAL}/eda/report?table={table}"
    return "", output, "btn btn-secondary", download_url
