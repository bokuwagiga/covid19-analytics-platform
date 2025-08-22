# dash/src/pages/about.py
import dash
from dash import html
import dash_bootstrap_components as dbc

# register page
dash.register_page(__name__, path="/about", name="About")

layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("About This Project", className="text-center mb-4"), width=12),
    ]),
    dbc.Row([
        dbc.Col(html.P(
            "This COVID-19 Data Integration, Analysis, and Visualization Platform was built as part "
            "of the Data Engineering Bootcamp project. It integrates structured and semi-structured data "
            "to provide insights into the spread, effects, and patterns of COVID-19 worldwide.",
            className="lead text-center"
        ), width=12)
    ], className="mb-5"),

    dbc.Row([
        dbc.Col([
            html.H4("Technologies Used"),
            html.Ul([
                html.Li("Snowflake – for structured COVID-19 data from the Marketplace"),
                html.Li("MongoDB (with GridFS) – for comments, annotations, and images"),
                html.Li("Python + Flask – for backend API and data integration"),
                html.Li("Dash (Plotly) – for interactive visualization dashboards"),
                html.Li("Docker & docker-compose – for deployment and reproducibility")
            ])
        ], md=6),
        dbc.Col([
            html.H4("Features"),
            html.Ul([
                html.Li("Interactive dashboards for mortality, cases, deaths, and vaccination"),
                html.Li("User comments and image sharing per dashboard"),
                html.Li("Integration of Snowflake + Kaggle datasets"),
                html.Li("APIs for data access and processing"),
                html.Li("Designed to be modular, scalable, and containerized")
            ])
        ], md=6),
    ], className="mb-5"),


], fluid=True)
