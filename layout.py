"""Top-level Dash layout."""

from dash import dcc, html
from components.session_selector import session_selector
from components.driver_selector import driver_selector


def build_layout() -> html.Div:
    return html.Div(
        style={
            "backgroundColor": "#F3F4F6",
            "minHeight": "100vh",
            "fontFamily": "Inter, system-ui, -apple-system, sans-serif",
            "color": "#111827",
        },
        children=[
            # Header
            html.Div(
                style={
                    "backgroundColor": "#FFFFFF",
                    "borderBottom": "1px solid #E5E7EB",
                    "padding": "0 24px",
                    "display": "flex",
                    "alignItems": "center",
                    "height": "52px",
                    "gap": "12px",
                },
                children=[
                    html.Span(
                        "F1",
                        style={
                            "color": "#DC2626",
                            "fontWeight": "900",
                            "fontSize": "18px",
                            "letterSpacing": "-0.02em",
                        },
                    ),
                    html.Span(
                        "Analytics",
                        style={
                            "color": "#111827",
                            "fontWeight": "400",
                            "fontSize": "18px",
                            "letterSpacing": "0.02em",
                        },
                    ),
                    html.Div(style={"flex": "1"}),
                    html.Span(
                        id="session-title",
                        style={"color": "#6B7280", "fontSize": "13px"},
                    ),
                ],
            ),

            # Controls bar
            session_selector(),
            driver_selector(),

            # Main content: charts + sidebar
            html.Div(
                style={
                    "display": "flex",
                    "gap": "0",
                    "flex": "1",
                },
                children=[
                    # Charts area
                    html.Div(
                        style={"flex": "1", "padding": "20px 24px", "minWidth": "0"},
                        children=[
                            dcc.Graph(
                                id="telemetry-graph",
                                config={
                                    "displayModeBar": True,
                                    "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"],
                                    "displaylogo": False,
                                    "responsive": True,
                                },
                                style={"width": "100%"},
                            ),
                        ],
                    ),

                    # Sidebar
                    html.Div(
                        style={
                            "width": "280px",
                            "flexShrink": "0",
                            "borderLeft": "1px solid #E5E7EB",
                            "backgroundColor": "#FFFFFF",
                            "padding": "16px 12px",
                        },
                        children=[
                            html.Div(
                                "Lap Times",
                                style={
                                    "fontSize": "11px",
                                    "fontWeight": "600",
                                    "letterSpacing": "0.08em",
                                    "textTransform": "uppercase",
                                    "color": "#6B7280",
                                    "marginBottom": "12px",
                                    "paddingLeft": "4px",
                                },
                            ),
                            html.Div(id="lap-times-sidebar"),
                        ],
                    ),
                ],
            ),

            # Hidden stores
            dcc.Store(id="driver-colors-store"),
            dcc.Store(id="session-data-store"),
        ],
    )
