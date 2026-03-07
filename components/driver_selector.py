"""Driver multi-select pills."""

from dash import dcc, html


def driver_selector() -> html.Div:
    return html.Div(
        id="driver-selector-container",
        style={
            "padding": "12px 24px",
            "backgroundColor": "#EDE3D8",
            "borderBottom": "1px solid #D4C2B0",
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
                    "color": "#8A7060",
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
                    "border": "1.5px solid #C8B8A8",
                    "fontSize": "11px",
                    "fontWeight": "600",
                    "cursor": "pointer",
                    "letterSpacing": "0.04em",
                    "color": "#5C4030",
                    "backgroundColor": "#F5EDE4",
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
                            "border": "1px solid #C8B8A8",
                            "borderRadius": "4px",
                            "color": "#8A7060",
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
                            "border": "1px solid #C8B8A8",
                            "borderRadius": "4px",
                            "color": "#8A7060",
                            "fontSize": "11px",
                            "padding": "4px 10px",
                            "cursor": "pointer",
                        },
                    ),
                ],
            ),
        ],
    )
