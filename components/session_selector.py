"""Session selector controls: Year → Race → Session/Lap options."""

from dash import dcc, html

from utils.f1_data import QUALIFYING_PHASES, SESSION_TYPES, SUPPORTED_YEARS
from utils.theme import SECTION_LABEL_STYLE

CONTROL_STYLE = {
    "display": "flex",
    "flexDirection": "column",
    "gap": "4px",
}

DROPDOWN_STYLE = {
    "fontSize": "13px",
}


def session_selector() -> html.Div:
    year_options = [{"label": str(y), "value": y} for y in reversed(SUPPORTED_YEARS)]

    return html.Div(
        className="surface-strip session-controls",
        children=[
            html.Div(
                style={**CONTROL_STYLE, "minWidth": "90px"},
                children=[
                    html.Label("Year", style=SECTION_LABEL_STYLE),
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
            html.Div(
                style={**CONTROL_STYLE, "minWidth": "200px", "flex": "1"},
                children=[
                    html.Label("Race", style=SECTION_LABEL_STYLE),
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
            html.Div(
                style={**CONTROL_STYLE, "minWidth": "150px"},
                children=[
                    html.Label("Session", style=SECTION_LABEL_STYLE),
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
            html.Div(
                id="qualifying-phase-control",
                style={**CONTROL_STYLE, "minWidth": "120px", "display": "none"},
                children=[
                    html.Label("Quali", style=SECTION_LABEL_STYLE),
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
            html.Div(
                style={**CONTROL_STYLE, "minWidth": "150px"},
                children=[
                    html.Label("Lap", style=SECTION_LABEL_STYLE),
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
            html.Div(
                id="lap-number-control",
                style={**CONTROL_STYLE, "minWidth": "130px", "display": "none"},
                children=[
                    html.Label("Lap #", style=SECTION_LABEL_STYLE),
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
            html.Div(
                style={**CONTROL_STYLE, "justifyContent": "flex-end"},
                children=[
                    html.Button(
                        "Load Session",
                        id="load-session-btn",
                        n_clicks=0,
                        className="primary-button",
                    )
                ],
            ),
            dcc.Loading(
                id="session-loading",
                type="dot",
                color="var(--accent)",
                children=html.Div(
                    id="session-load-status",
                    className="status-text",
                    style={"fontSize": "12px", "alignSelf": "center"},
                ),
            ),
            dcc.Store(id="session-store"),
        ],
    )
