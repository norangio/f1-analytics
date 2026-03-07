"""Top-level Dash layout."""

from dash import dcc, html
from components.session_selector import session_selector
from components.driver_selector import driver_selector


def build_layout() -> html.Div:
    return html.Div(
        style={
            "backgroundColor": "#F5EDE4",
            "minHeight": "100vh",
            "fontFamily": "Inter, system-ui, -apple-system, sans-serif",
            "color": "#2C1810",
        },
        children=[
            # Header
            html.Div(
                style={
                    "backgroundColor": "#EDE3D8",
                    "borderBottom": "1px solid #D4C2B0",
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
                            "color": "#C96A2A",
                            "fontWeight": "900",
                            "fontSize": "18px",
                            "letterSpacing": "-0.02em",
                        },
                    ),
                    html.Span(
                        "Analytics",
                        style={
                            "color": "#5C4030",
                            "fontWeight": "300",
                            "fontSize": "18px",
                            "letterSpacing": "0.02em",
                        },
                    ),
                    html.Div(style={"flex": "1"}),
                    html.Span(
                        id="session-title",
                        style={"color": "#8A7060", "fontSize": "13px"},
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
                            "borderLeft": "1px solid #D4C2B0",
                            "backgroundColor": "#EDE3D8",
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
                                    "color": "#8A7060",
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
