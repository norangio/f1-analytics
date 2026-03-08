"""Driver multi-select pills."""

from dash import dcc, html


def driver_selector() -> html.Div:
    return html.Div(
        id="driver-selector-container",
        style={
            "padding": "12px 24px",
            "backgroundColor": "#FFFFFF",
            "borderBottom": "1px solid #E5E7EB",
            "display": "flex",
            "alignItems": "center",
            "gap": "16px",
            "flexWrap": "wrap",
        },
        children=[
            html.Span(
                "Drivers",
                style={
                    "fontSize": "11px",
                    "fontWeight": "600",
                    "letterSpacing": "0.08em",
                    "textTransform": "uppercase",
                    "color": "#6B7280",
                    "whiteSpace": "nowrap",
                },
            ),
            dcc.Checklist(
                id="driver-checklist",
                options=[],
                value=[],
                inline=True,
                style={"display": "flex", "flexWrap": "wrap", "gap": "6px"},
                inputStyle={"display": "none"},
                labelStyle={
                    "padding": "4px 11px",
                    "borderRadius": "20px",
                    "border": "1.5px solid #D1D5DB",
                    "fontSize": "11px",
                    "fontWeight": "600",
                    "cursor": "pointer",
                    "letterSpacing": "0.04em",
                    "color": "#374151",
                    "backgroundColor": "#F9FAFB",
                    "userSelect": "none",
                },
                className="driver-checklist",
            ),
            html.Div(
                style={"marginLeft": "auto", "display": "flex", "alignItems": "center", "gap": "8px"},
                children=[
                    html.Button(
                        "Select All",
                        id="select-all-drivers-btn",
                        n_clicks=0,
                        style={
                            "background": "none",
                            "border": "1px solid #D1D5DB",
                            "borderRadius": "4px",
                            "color": "#6B7280",
                            "fontSize": "11px",
                            "padding": "4px 10px",
                            "cursor": "pointer",
                        },
                    ),
                    html.Button(
                        "Clear",
                        id="clear-drivers-btn",
                        n_clicks=0,
                        style={
                            "background": "none",
                            "border": "1px solid #D1D5DB",
                            "borderRadius": "4px",
                            "color": "#6B7280",
                            "fontSize": "11px",
                            "padding": "4px 10px",
                            "cursor": "pointer",
                        },
                    ),
                ],
            ),
        ],
    )
