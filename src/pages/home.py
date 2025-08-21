import dash
from dash import html
import dash_bootstrap_components as dbc

# register this page as the home page
dash.register_page(__name__, path="/")

# layout for home page
layout = html.Div([
    dbc.Row([
        html.H1("Welcome to Health Analytics Portal", className="text-center"),
        html.P("Choose a page from the navbar.", className="text-center")
    ], className="mb-4 mt-2")
])
