from dash import html
import dash_bootstrap_components as dbc
import dash

# register this page with dash
dash.register_page(__name__, path="/about", name="About")

# layout for about page
layout = dbc.Container([
    dbc.Row([
        html.H1("About this project", className="text-center"),
        html.P("This is a multi-page COVID dashboard built with Dash Pages.", className="text-center"),
    ], className="mb-4 mt-2")
], fluid=True)
