"""Top-level Dash layout."""

from dash import dcc, html

from components.driver_selector import driver_selector
from components.laptime_summary_table import laptime_summary_empty
from components.session_selector import session_selector
from utils.theme import FONT_STACK


def build_layout() -> html.Div:
    return html.Div(
        className="theme-shell",
        style={
            "minHeight": "100vh",
            "fontFamily": FONT_STACK,
            "display": "flex",
            "flexDirection": "column",
        },
        children=[
            html.Div(
                className="surface-strip app-header",
                children=[
                    html.Span("F1", className="app-brand-mark"),
                    html.Span("Analytics", className="app-brand-name"),
                    html.Div(style={"flex": "1"}),
                    html.Span(
                        id="session-title",
                        className="app-session-title",
                        style={"fontSize": "13px"},
                    ),
                ],
            ),
            session_selector(),
            driver_selector(),
            dcc.Tabs(
                id="main-tabs",
                value="telemetry",
                parent_className="tab-parent",
                className="surface-strip app-tabs",
                content_className="tab-content",
                children=[
                    dcc.Tab(
                        label="Telemetry",
                        value="telemetry",
                        className="app-tab",
                        selected_className="app-tab app-tab--selected",
                    ),
                    dcc.Tab(
                        label="Lap Times",
                        value="laptimes",
                        className="app-tab",
                        selected_className="app-tab app-tab--selected",
                    ),
                ],
            ),
            html.Div(
                id="telemetry-content",
                className="telemetry-layout",
                style={"display": "flex", "flex": "1"},
                children=[
                    html.Div(
                        className="surface-card telemetry-main",
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
                    html.Div(
                        className="surface-card telemetry-sidebar",
                        children=[
                            html.Div("Lap Times", className="section-label", style={"marginBottom": "12px", "paddingLeft": "4px"}),
                            html.Div(id="lap-times-sidebar"),
                        ],
                    ),
                ],
            ),
            html.Div(
                id="laptimes-content",
                className="laptimes-layout",
                style={"display": "none"},
                children=[
                    html.Div(
                        className="toggle-row",
                        children=[
                            dcc.Checklist(
                                id="laptime-robust-axis-toggle",
                                options=[{"label": "Robust y-axis (5-95%)", "value": "robust"}],
                                value=["robust"],
                                className="robust-axis-toggle",
                                labelStyle={"display": "inline-flex", "alignItems": "center"},
                            ),
                        ],
                    ),
                    html.Div(
                        className="surface-card chart-card",
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
                    html.Div(
                        id="laptime-summary-table",
                        className="surface-card summary-card",
                        children=laptime_summary_empty(),
                    ),
                ],
            ),
            dcc.Store(id="theme-store", data="dark"),
            dcc.Interval(id="theme-sync-interval", interval=1000, n_intervals=0),
            dcc.Store(id="driver-colors-store"),
            dcc.Store(id="session-data-store"),
        ],
    )
