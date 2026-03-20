"""Driver multi-select pills."""

from dash import dcc, html

from utils.theme import SECTION_LABEL_STYLE


def driver_selector() -> html.Div:
    return html.Div(
        id="driver-selector-container",
        className="surface-strip driver-selector",
        children=[
            html.Span("Drivers", style={**SECTION_LABEL_STYLE, "whiteSpace": "nowrap"}),
            dcc.Checklist(
                id="driver-checklist",
                options=[],
                value=[],
                inline=True,
                style={"display": "flex", "flexWrap": "wrap", "gap": "8px"},
                inputStyle={"display": "none"},
                className="driver-checklist",
            ),
            html.Div(
                style={"marginLeft": "auto", "display": "flex", "alignItems": "center", "gap": "8px"},
                children=[
                    html.Button(
                        "Select All",
                        id="select-all-drivers-btn",
                        n_clicks=0,
                        className="ghost-pill-button",
                    ),
                    html.Button(
                        "Clear",
                        id="clear-drivers-btn",
                        n_clicks=0,
                        className="ghost-pill-button",
                    ),
                ],
            ),
        ],
    )
