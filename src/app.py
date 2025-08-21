import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, page_container
from components.navbar import get_navbar
from config.config import DASHBOARDS_LIST

# create dash app
app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.SOLAR,
                          "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css"],
    suppress_callback_exceptions=True
)

# expose flask server
server = app.server

# app layout
app.layout = dbc.Container([
    get_navbar(),
    dcc.Location(id="url"),
    dash.page_container
], fluid=True)

from dash import Output, Input

# clientside callbacks to format comment dates
for page in DASHBOARDS_LIST:
    app.clientside_callback(
        """
        function(children) {
            const nodes = document.querySelectorAll('.comment-date');
            nodes.forEach(el => {
                const utc = el.getAttribute('data-utc');
                if (utc) {
                    const d = new Date(utc);
                    el.textContent = d.toLocaleString([], {
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit'
                    });
                }
            });
            return children;
        }
        """,
        Output(f"{page}-comments-section", "children", allow_duplicate=True),
        Input(f"{page}-comments-section", "children"),
        prevent_initial_call="initial_duplicate"
    )

if __name__ == "__main__":
    app.run(debug=True)
