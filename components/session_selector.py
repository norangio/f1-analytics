"""Session selector controls: Year → Race → Session Type."""

from dash import dcc, html
from utils.f1_data import SUPPORTED_YEARS, SESSION_TYPES

CONTROL_STYLE = {
    "display": "flex",
    "flexDirection": "column",
    "gap": "4px",
}

LABEL_STYLE = {
    "fontSize": "11px",
    "fontWeight": "600",
    "letterSpacing": "0.08em",
    "textTransform": "uppercase",
    "color": "#8A7060",
}

DROPDOWN_STYLE = {
    "backgroundColor": "#EDE3D8",
    "border": "1px solid #C8B8A8",
    "borderRadius": "6px",
    "color": "#2C1810",
    "fontSize": "13px",
}


def session_selector() -> html.Div:
    year_options = [{"label": str(y), "value": y} for y in reversed(SUPPORTED_YEARS)]

    return html.Div(
        style={
            "display": "flex",
            "flexWrap": "wrap",
            "gap": "16px",
            "alignItems": "flex-end",
            "padding": "16px 24px",
            "backgroundColor": "#F5EDE4",
            "borderBottom": "1px solid #D4C2B0",
        },
        children=[
            # Year
            html.Div(
                style={**CONTROL_STYLE, "minWidth": "90px"},
                children=[
                    html.Label("Year", style=LABEL_STYLE),
                    dcc.Dropdown(
                        id="year-dropdown",
                        options=year_options,
                        value=2026,
                        clearable=False,
                        style=DROPDOWN_STYLE,
                        className="f1-dropdown",
                    ),
                ],
            ),
            # Race
            html.Div(
                style={**CONTROL_STYLE, "minWidth": "200px", "flex": "1"},
                children=[
                    html.Label("Race", style=LABEL_STYLE),
                    dcc.Dropdown(
                        id="race-dropdown",
                        options=[],
                        placeholder="Select a race...",
                        clearable=False,
                        style=DROPDOWN_STYLE,
                        className="f1-dropdown",
                    ),
                ],
            ),
            # Session type
            html.Div(
                style={**CONTROL_STYLE, "minWidth": "150px"},
                children=[
                    html.Label("Session", style=LABEL_STYLE),
                    dcc.Dropdown(
                        id="session-dropdown",
                        options=[{"label": v, "value": k} for k, v in SESSION_TYPES.items()],
                        value="Q",
                        clearable=False,
                        style=DROPDOWN_STYLE,
                        className="f1-dropdown",
                    ),
                ],
            ),
            # Lap mode
            html.Div(
                style={**CONTROL_STYLE, "minWidth": "150px"},
                children=[
                    html.Label("Lap", style=LABEL_STYLE),
                    dcc.Dropdown(
                        id="lap-mode-dropdown",
                        options=[
                            {"label": "Fastest Lap", "value": "fastest"},
                            {"label": "Session Lap", "value": "specific"},
                        ],
                        value="fastest",
                        clearable=False,
                        style=DROPDOWN_STYLE,
                        className="f1-dropdown",
                    ),
                ],
            ),
            # Specific lap selector (shown only in session-lap mode)
            html.Div(
                id="lap-number-control",
                style={**CONTROL_STYLE, "minWidth": "130px", "display": "none"},
                children=[
                    html.Label("Lap #", style=LABEL_STYLE),
                    dcc.Dropdown(
                        id="lap-number-dropdown",
                        options=[],
                        placeholder="Select lap...",
                        clearable=False,
                        disabled=True,
                        style=DROPDOWN_STYLE,
                        className="f1-dropdown",
                    ),
                ],
            ),
            # Load button
            html.Div(
                style={**CONTROL_STYLE, "justifyContent": "flex-end"},
                children=[
                    html.Button(
                        "Load Session",
                        id="load-session-btn",
                        n_clicks=0,
                        style={
                            "backgroundColor": "#C96A2A",
                            "color": "#FDF8F4",
                            "border": "none",
                            "borderRadius": "6px",
                            "padding": "8px 18px",
                            "fontSize": "13px",
                            "fontWeight": "700",
                            "cursor": "pointer",
                            "letterSpacing": "0.04em",
                            "height": "36px",
                        },
                    )
                ],
            ),
            # Loading indicator
            dcc.Loading(
                id="session-loading",
                type="dot",
                color="#C96A2A",
                children=html.Div(id="session-load-status", style={"fontSize": "12px", "color": "#8A7060", "alignSelf": "center"}),
            ),
            # Hidden store for loaded session info
            dcc.Store(id="session-store"),
        ],
    )
