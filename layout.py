"""Top-level Dash layout."""

from dash import dcc, html
from components.session_selector import session_selector
from components.driver_selector import driver_selector

_TAB_STYLE = {
    "padding": "10px 16px",
    "fontSize": "12px",
    "fontWeight": "600",
    "letterSpacing": "0.04em",
    "color": "#6B7280",
    "border": "none",
    "borderBottom": "2px solid transparent",
    "backgroundColor": "#FFFFFF",
    "fontFamily": "Inter, system-ui, -apple-system, sans-serif",
    "cursor": "pointer",
}
_TAB_SELECTED_STYLE = {
    **_TAB_STYLE,
    "color": "#111827",
    "borderBottom": "2px solid #111827",
}


def build_layout() -> html.Div:
    return html.Div(
        style={
            "backgroundColor": "#F3F4F6",
            "minHeight": "100vh",
            "fontFamily": "Inter, system-ui, -apple-system, sans-serif",
            "color": "#111827",
            "display": "flex",
            "flexDirection": "column",
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

            # Tab bar
            dcc.Tabs(
                id="main-tabs",
                value="telemetry",
                children=[
                    dcc.Tab(
                        label="Telemetry",
                        value="telemetry",
                        style=_TAB_STYLE,
                        selected_style=_TAB_SELECTED_STYLE,
                    ),
                    dcc.Tab(
                        label="Lap Times",
                        value="laptimes",
                        style=_TAB_STYLE,
                        selected_style=_TAB_SELECTED_STYLE,
                    ),
                ],
                style={
                    "backgroundColor": "#FFFFFF",
                    "borderBottom": "1px solid #E5E7EB",
                    "padding": "0 24px",
                    "height": "40px",
                },
                colors={
                    "border": "transparent",
                    "primary": "#111827",
                    "background": "#FFFFFF",
                },
            ),

            # Telemetry content (existing)
            html.Div(
                id="telemetry-content",
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

            # Lap Times content (new)
            html.Div(
                id="laptimes-content",
                style={"display": "none"},
                children=[
                    dcc.Graph(
                        id="laptime-boxplot-graph",
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

            # Hidden stores
            dcc.Store(id="driver-colors-store"),
            dcc.Store(id="session-data-store"),
        ],
    )
