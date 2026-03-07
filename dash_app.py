"""Dash app instance — imported by both app.py and callbacks."""

import dash

app = dash.Dash(
    __name__,
    title="F1 Analytics",
    update_title=None,
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

server = app.server
