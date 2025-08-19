from dash import html
import dash_bootstrap_components as dbc
import dash

dash.register_page(__name__, path="/about", name="About")

def layout():
    return dbc.Container([
        html.H2("About this project"),
        html.P("This is a multi-page COVID dashboard built with Dash Pages."),
    ], fluid=True)
