import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, page_container

from components.navbar import get_navbar

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.SOLAR,
                          "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css"],
    suppress_callback_exceptions=True
)

server = app.server

app.layout = dbc.Container([
    get_navbar(),
    dcc.Location(id="url"),
    dash.page_container
], fluid=True)


if __name__ == "__main__":
    app.run(debug=True)
