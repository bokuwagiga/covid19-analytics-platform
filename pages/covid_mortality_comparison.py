# pages/covid_mortality_comparison.py
"""
COVID-19 Dashboard Page
-----------------------
- Dropdown to select country (from DB via API)
- Mortality chart
- Comments section + Add Comment form
"""
import os
import requests
import dash
from dash import dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv('config/.env')

COVID_MORTALITY_COMPARISON = os.getenv("COVID_MORTALITY_COMPARISON")
API_BASE = os.getenv('API_BASE')

dash.register_page(__name__, path=f"/{COVID_MORTALITY_COMPARISON}", name="COVID Dashboard")


# --- Utilities ---
def get_country_list():
    try:
        resp = requests.get(f"{API_BASE}/covid_mortality_comparison_countries")
        if resp.status_code == 200:
            return resp.json()
    except:
        return ["Lithuania"]
    return ["Lithuania"]


# --- Layout ---
COUNTRIES = get_country_list()

layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("COVID-19 Mortality Dashboard", className="text-center"), width=12)
    ], className="mb-4 mt-2"),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="country-dropdown",
                options=[{"label": c, "value": c} for c in COUNTRIES],
                value=COUNTRIES[0],
                placeholder='Select a country',
                style={"width": "100%"}
            )
        ], width=6)
    ], className="mb-4"),

    dbc.Row([
        # Chart
        dbc.Col(dcc.Graph(id="mortality-graph"), width=8),

        # Comments section
        dbc.Col([
            html.H4("User Comments", className="mb-3"),
            html.Div(id="comments-section", style={"maxHeight": "400px", "overflowY": "auto"}),

            html.Hr(),

            html.H5("Add a Comment"),
            dbc.Input(id="user-input", type="text", placeholder="Your name", className="mb-2"),
            dbc.Input(id="date-input", type="date", className="mb-2"),
            dbc.Input(id="metric-input", type="text", placeholder="Metric (e.g. deaths_covid)", className="mb-2"),
            dbc.Textarea(id="comment-input", placeholder="Write your comment...", className="mb-2"),
            html.Div(id="submit-status", style={"marginTop": "10px","marginBottom": "10px", "color": "lightgreen"}),
            dbc.Button("Submit", id="submit-btn", color="primary", className="mb-2 w-100"),
            dcc.Interval(id="status-clear-timer", interval=4000, n_intervals=0, disabled=True)
        ], width=4)
    ])
], fluid=True)


# --- Callbacks ---
@dash.callback(
    [Output("mortality-graph", "figure"),
     Output("comments-section", "children")],
    [Input("country-dropdown", "value"),
     Input("submit-btn", "n_clicks")],
)
def update_dashboard(country, n_clicks):
    covid_resp = requests.get(f"{API_BASE}/{COVID_MORTALITY_COMPARISON}", params={"country": country})
    covid_data = covid_resp.json()

    if not covid_data or isinstance(covid_data, dict) and "error" in covid_data:
        return go.Figure(), html.P("No data available.")

    dates = [d["date"] for d in covid_data]
    deaths_all = [d["deaths_allcause"] for d in covid_data]
    deaths_counterfactual = [d["deaths_without_covid"] for d in covid_data]
    deaths_covid = [d["deaths_covid"] for d in covid_data]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=deaths_all, mode="lines+markers", name="Observed all-cause deaths"))
    fig.add_trace(go.Scatter(x=dates, y=deaths_counterfactual, mode="lines", name="Counterfactual (no COVID)", line=dict(dash="dash")))
    fig.add_trace(go.Scatter(x=dates, y=deaths_covid, mode="lines", name="Reported COVID deaths", line=dict(color="red")))

    fig.update_layout(
        title=f"Mortality Trends in {country}",
        xaxis_title="Date",
        yaxis_title="Deaths",
        template="plotly_dark",
        hovermode="x unified"
    )

    comments_resp = requests.get(f"{API_BASE}/comments", params={"country": country})
    comments = comments_resp.json()
    if not comments:
        comments_section = html.P("No comments yet.")
    else:
        comments_section = dbc.ListGroup([
            dbc.ListGroupItem([
                html.I(className="bi bi-chat-left-text me-2"),
                html.Span(f"{c['date']}: {c['comment']} "),
                html.Small(f"(by {c['user']})", className="text-muted")
            ]) for c in comments
        ])

    return fig, comments_section


@dash.callback(
    [Output("submit-status", "children"),
     Output("status-clear-timer", "disabled"),
     Output("status-clear-timer", "n_intervals")],
    [Input("submit-btn", "n_clicks"),
     Input("status-clear-timer", "n_intervals")],
    [State("country-dropdown", "value"),
     State("date-input", "value"),
     State("metric-input", "value"),
     State("comment-input", "value"),
     State("user-input", "value")]
)
def handle_comment_and_status(n_clicks, n_intervals, country, date, metric, comment, user):
    trigger = ctx.triggered_id

    # ✅ Timer fired → clear the status
    if trigger == "status-clear-timer" and n_intervals > 0:
        return "", True, 0

    # ✅ Submit button fired → try to add comment
    if trigger == "submit-btn" and n_clicks:
        if not all([country, metric, comment, user]):
            return "⚠️ Error: Missing required fields.", False, 0

        payload = {
            "country": country,
            "date": date or "general",
            "metric": metric,
            "comment": comment,
            "user": user
        }
        resp = requests.post(f"{API_BASE}/comments", json=payload)
        if resp.status_code == 201:
            return "✅ Comment added successfully!", False, 0
        return f"❌ Error: {resp.json()}", False, 0

    # Default → no updates
    return dash.no_update, dash.no_update, dash.no_update
