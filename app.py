"""F1 Analytics Dashboard — entry point."""

from dash_app import app, server  # noqa: F401 — server needed for gunicorn
from layout import build_layout
import callbacks.session_callbacks  # noqa: F401
import callbacks.chart_callbacks    # noqa: F401
import callbacks.sidebar_callbacks  # noqa: F401
import callbacks.laptime_callbacks  # noqa: F401

app.layout = build_layout()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
