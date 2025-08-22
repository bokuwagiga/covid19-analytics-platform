#src/components/comments.py
import requests
from dash import html, dcc, Output, Input, State, callback, ctx
import dash_bootstrap_components as dbc
from config.config import API_BASE, API_BASE_EXTERNAL


def CommentsSection(page_id: str, country_dropdown_id: str = None):
    """
    Creates the comments section layout
    page_id is the unique name of the page
    country_dropdown_id is optional for filtering comments by country
    """
    return dbc.Col([

        # comment list card
        dbc.Card([
            dbc.CardHeader(
                dbc.Row([
                    dbc.Col("User Comments", className="fw-bold"),
                    dbc.Col(
                        dbc.Checklist(
                            options=[{"label": "Show only this country", "value": "filter"}],
                            value=["filter"],  # default is ON
                            id=f"{page_id}-filter-country",
                            switch=True,
                            className="text-end"
                        ),
                        width="auto"
                    )
                ], align="center", justify="between")
            ),
            dbc.CardBody(
                html.Div(id=f"{page_id}-comments-section"),
                style={"overflowY": "auto"},
                className="flex-grow-1 p-0"
            )
        ], className="mb-3 d-flex flex-column",
            style={"height": "450px", "border": "1px solid #444", "borderRadius": "8px", "overflow": "hidden"}),

        # comment form card
        dbc.Card([
            dbc.CardHeader("Add a Comment"),
            dbc.CardBody([
                dbc.Input(id=f"{page_id}-user-input", type="text", placeholder="Your name", className="mb-2"),
                dbc.Textarea(id=f"{page_id}-comment-input", placeholder="Write your comment...", className="mb-2"),

                # file upload area
                html.Div("Share what interested you on the dashboard:", className="mb-2 text-muted small"),
                dcc.Upload(id=f"{page_id}-image-upload",
                           children=html.Div(["Drag and Drop or ", html.A("Select an Image")]),
                           style={"width": "100%", "height": "60px", "lineHeight": "60px", "borderWidth": "1px",
                                  "borderStyle": "dashed", "borderRadius": "5px", "textAlign": "center",
                                  "marginBottom": "10px"}, multiple=False),
                html.Div(id=f"{page_id}-image-preview", className="text-muted mb-2"),

                # submit area
                html.Div(id=f"{page_id}-submit-status", style={"marginTop": "10px", "marginBottom": "10px", "color": "lightgreen"}),
                dbc.Button("Submit", id=f"{page_id}-submit-btn", color="primary", className="mb-2 w-100"),
                dcc.Interval(id=f"{page_id}-status-clear-timer", interval=4000, n_intervals=0, disabled=True)
            ])
        ])
    ], width=12, lg=4)


def register_comment_callbacks(page_id: str, country_dropdown_id: str = None):
    """
    Registers all callbacks for comments
    This includes loading comments, submitting a comment, and updating image preview
    """

    # callback to load comments
    @callback(
        Output(f"{page_id}-comments-section", "children"),
        [Input(f"{page_id}-filter-country", "value"),
         Input(f"{page_id}-submit-btn", "n_clicks"),
         Input(f"{page_id}-status-clear-timer", "n_intervals"),
         Input(country_dropdown_id, "value")] if country_dropdown_id else
        [Input(f"{page_id}-filter-country", "value"),
         Input(f"{page_id}-submit-btn", "n_clicks"),
         Input(f"{page_id}-status-clear-timer", "n_intervals")]
    )
    def load_comments(filter_value, *_args):
        # build request params
        params = {"page": page_id}
        country = _args[-1] if (country_dropdown_id and len(_args) > 0) else None

        # only show comments for selected country if filter is on
        if ("filter" in filter_value) and country:
            params["country"] = country

        comments_resp = requests.get(f"{API_BASE}/comments", params=params)
        comments = comments_resp.json() if comments_resp.status_code == 200 else []

        if not comments:
            return html.Div(html.P("No comments yet.", className="text-muted m-2"))

        # if filter is off show country badge
        show_country = not ("filter" in filter_value)

        # build comment list items
        return dbc.ListGroup([
            dbc.ListGroupItem([
                html.Div([
                    html.I(className="bi bi-person-circle me-2"),
                    html.Strong(c["user"], className="me-2"),
                    html.Small("", className="comment-date text-muted", **{"data-utc": c["created_at"]}),
                    html.Span(c["country"], className="badge bg-secondary ms-2") if show_country and c.get("country") else None
                ], className="d-flex align-items-center"),

                html.P(c["comment"], className="mt-2 mb-1"),

                # show image if it exists
                html.Img(src=f"{API_BASE_EXTERNAL}{c['image_url']}", style={"maxWidth": "100%", "maxHeight": "200px", "marginTop": "5px", "borderRadius": "6px"}) if c.get("image_url") else None
            ]) for c in comments
        ], flush=True, style={"maxHeight": "400px"})

    # callback to handle comment submission
    @callback(
        [Output(f"{page_id}-submit-status", "children"),
         Output(f"{page_id}-status-clear-timer", "disabled"),
         Output(f"{page_id}-status-clear-timer", "n_intervals")],
        [Input(f"{page_id}-submit-btn", "n_clicks"),
         Input(f"{page_id}-status-clear-timer", "n_intervals")],
        [State(f"{page_id}-user-input", "value"),
         State(f"{page_id}-comment-input", "value"),
         State(f"{page_id}-image-upload", "contents"),
         State(f"{page_id}-image-upload", "filename"),
         State(country_dropdown_id, "value")] if country_dropdown_id else
        [State(f"{page_id}-user-input", "value"),
         State(f"{page_id}-comment-input", "value"),
         State(f"{page_id}-image-upload", "contents"),
         State(f"{page_id}-image-upload", "filename")]
    )
    def submit_comment(n_clicks, n_intervals, user, comment, image_content, image_name, *state):
        trigger = ctx.triggered_id

        # clear message after timer ends
        if trigger == f"{page_id}-status-clear-timer" and n_intervals > 0:
            return "", True, 0

        # handle submit button click
        if trigger == f"{page_id}-submit-btn" and n_clicks:
            if not all([user, comment]):
                return "Error: Missing required fields.", False, 0

            country = state[0] if country_dropdown_id and state else None

            # build request payload
            files = {}
            data = {"user": user, "comment": comment, "page": page_id}
            if country:
                data["country"] = country

            if image_content and image_name:
                # decode base64 image into raw file
                import base64
                header, b64data = image_content.split(",")
                raw = base64.b64decode(b64data)
                files["image"] = (image_name, raw)

            # send request with or without image
            if files:
                resp = requests.post(f"{API_BASE}/comments", data=data, files=files)
            else:
                resp = requests.post(f"{API_BASE}/comments", json=data)

            if resp.status_code == 201:
                return "Comment added successfully", False, 0
            return f"Error: {resp.json()}", False, 0

        return "", True, 0

    # callback to update filename preview
    @callback(
        Output(f"{page_id}-image-preview", "children"),
        Input(f"{page_id}-image-upload", "filename")
    )
    def update_preview(filename):
        if filename:
            return f"Selected: {filename}"
        return ""
