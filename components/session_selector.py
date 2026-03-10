"""Session selector controls: Year → Race → Session/Lap options."""

from dash import dcc, html
from utils.f1_data import SUPPORTED_YEARS, SESSION_TYPES, QUALIFYING_PHASES

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
    "color": "#6B7280",
}

DROPDOWN_STYLE = {
    "backgroundColor": "#FFFFFF",
    "border": "1px solid #D1D5DB",
    "borderRadius": "6px",
    "color": "#111827",
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
            "backgroundColor": "#FFFFFF",
            "borderBottom": "1px solid #E5E7EB",
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
            # Qualifying phase selector (shown only for qualifying sessions)
            html.Div(
                id="qualifying-phase-control",
                style={**CONTROL_STYLE, "minWidth": "120px", "display": "none"},
                children=[
                    html.Label("Quali", style=LABEL_STYLE),
                    dcc.Dropdown(
                        id="qualifying-phase-dropdown",
                        options=[{"label": v, "value": k} for k, v in QUALIFYING_PHASES.items()],
                        value="all",
                        clearable=False,
                        disabled=True,
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
                            {"label": "All Laps", "value": "all"},
                            {"label": "Fastest Lap", "value": "fastest"},
                            {"label": "Session Lap", "value": "specific"},
                        ],
                        value="all",
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
                            "backgroundColor": "#111827",
                            "color": "#F9FAFB",
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
                color="#111827",
                children=html.Div(id="session-load-status", style={"fontSize": "12px", "color": "#6B7280", "alignSelf": "center"}),
            ),
            # Hidden store for loaded session info
            dcc.Store(id="session-store"),
        ],
    )
