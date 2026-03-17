"""Callbacks for session selector: populate race dropdown, load session data."""

import dash
from dash import Input, Output, State, ctx
from dash.exceptions import PreventUpdate

from dash_app import app
from utils import f1_data
from utils.colors import assign_driver_colors

LAP_NUMBER_CONTROL_STYLE = {
    "display": "flex",
    "flexDirection": "column",
    "gap": "4px",
    "minWidth": "130px",
}
QUALIFYING_PHASE_CONTROL_STYLE = {
    "display": "flex",
    "flexDirection": "column",
    "gap": "4px",
    "minWidth": "120px",
}
DRIVER_ACTION_BUTTON_BASE_STYLE = {
    "background": "none",
    "border": "1px solid #D1D5DB",
    "borderRadius": "4px",
    "color": "#6B7280",
    "fontSize": "11px",
    "padding": "4px 10px",
    "cursor": "pointer",
}
DRIVER_ACTION_BUTTON_ACTIVE_STYLE = {
    **DRIVER_ACTION_BUTTON_BASE_STYLE,
    "backgroundColor": "#111827",
    "border": "1px solid #111827",
    "color": "#F9FAFB",
    "fontWeight": "700",
}


@app.callback(
    Output("race-dropdown", "options"),
    Output("race-dropdown", "value"),
    Input("year-dropdown", "value"),
)
def update_race_options(year):
    if year is None:
        raise PreventUpdate
    events = f1_data.get_event_schedule(year)
    options = [{"label": e["name"], "value": e["round"]} for e in events]
    default = options[-1]["value"] if options else None
    return options, default


@app.callback(
    Output("session-store", "data"),
    Output("session-load-status", "children"),
    Output("session-title", "children"),
    Output("driver-colors-store", "data"),
    Input("load-session-btn", "n_clicks"),
    State("year-dropdown", "value"),
    State("race-dropdown", "value"),
    State("session-dropdown", "value"),
    prevent_initial_call=True,
)
def load_session(n_clicks, year, round_number, session_key):
    if not n_clicks or year is None or round_number is None or session_key is None:
        raise PreventUpdate

    try:
        session = f1_data.load_session_laps(year, round_number, session_key)
        drivers = f1_data.get_drivers_in_session(session)
        colors = assign_driver_colors(drivers)

        session_label = f1_data.SESSION_TYPES.get(session_key, session_key)
        title = f"{year} · {session.event['EventName']} · {session_label}"
        status = f"Loaded — {len(drivers)} drivers"

        driver_numbers = f1_data.get_driver_numbers(session)
        available_laps = f1_data.get_available_lap_numbers(session)
        qualifying_phase_laps = f1_data.get_qualifying_phase_lap_numbers(session) if session_key == "Q" else {}
        available_qualifying_phases = [phase for phase in ("Q1", "Q2", "Q3") if qualifying_phase_laps.get(phase)]

        store_data = {
            "year": year,
            "round": round_number,
            "session_key": session_key,
            "drivers": drivers,
            "driver_numbers": driver_numbers,
            "available_laps": available_laps,
            "qualifying_phase_laps": qualifying_phase_laps,
            "available_qualifying_phases": available_qualifying_phases,
        }
        return store_data, status, title, colors
    except Exception as e:
        return dash.no_update, f"Error: {str(e)[:60]}", dash.no_update, dash.no_update


@app.callback(
    Output("qualifying-phase-dropdown", "options"),
    Output("qualifying-phase-dropdown", "value"),
    Output("qualifying-phase-dropdown", "disabled"),
    Output("qualifying-phase-control", "style"),
    Input("session-dropdown", "value"),
    Input("session-store", "data"),
    State("qualifying-phase-dropdown", "value"),
)
def update_qualifying_phase_options(selected_session_key, session_data, current_value):
    default_options = [{"label": "All", "value": "all"}]

    if selected_session_key != "Q":
        return default_options, "all", True, {**QUALIFYING_PHASE_CONTROL_STYLE, "display": "none"}

    if session_data is None or session_data.get("session_key") != "Q":
        return default_options, "all", True, QUALIFYING_PHASE_CONTROL_STYLE

    available_phases = session_data.get("available_qualifying_phases", [])
    options = default_options + [{"label": phase, "value": phase} for phase in available_phases]
    disabled = len(options) == 1
    if current_value in {opt["value"] for opt in options}:
        value = current_value
    else:
        value = "all"
    return options, value, disabled, QUALIFYING_PHASE_CONTROL_STYLE


@app.callback(
    Output("lap-number-dropdown", "options"),
    Output("lap-number-dropdown", "value"),
    Output("lap-number-dropdown", "disabled"),
    Output("lap-number-control", "style"),
    Input("lap-mode-dropdown", "value"),
    Input("qualifying-phase-dropdown", "value"),
    Input("session-store", "data"),
)
def update_lap_number_options(lap_mode, qualifying_phase, session_data):
    if lap_mode != "specific":
        return [], None, True, {**LAP_NUMBER_CONTROL_STYLE, "display": "none"}

    if session_data is None:
        return [], None, True, LAP_NUMBER_CONTROL_STYLE

    available_laps = session_data.get("available_laps", [])
    if session_data.get("session_key") == "Q" and qualifying_phase in ("Q1", "Q2", "Q3"):
        phase_laps = session_data.get("qualifying_phase_laps", {})
        available_laps = phase_laps.get(qualifying_phase, [])

    options = [{"label": str(lap), "value": lap} for lap in available_laps]
    default_value = options[0]["value"] if options else None
    disabled = not bool(options)
    return options, default_value, disabled, LAP_NUMBER_CONTROL_STYLE


@app.callback(
    Output("driver-checklist", "options"),
    Output("driver-checklist", "value"),
    Input("session-store", "data"),
)
def update_driver_checklist(session_data):
    if session_data is None:
        raise PreventUpdate

    drivers = session_data.get("drivers", [])
    driver_numbers = session_data.get("driver_numbers", {})

    options = []
    for driver in drivers:
        number = driver_numbers.get(driver, "")
        label = f"{number} {driver}" if number else driver
        options.append({
            "label": label,
            "value": driver,
        })

    # Default: first 5 drivers selected
    default_selected = drivers[:5]
    return options, default_selected


@app.callback(
    Output("driver-checklist", "value", allow_duplicate=True),
    Input("select-all-drivers-btn", "n_clicks"),
    Input("clear-drivers-btn", "n_clicks"),
    State("driver-checklist", "options"),
    prevent_initial_call=True,
)
def handle_select_all_clear(select_all, clear, options):
    triggered = ctx.triggered_id
    if triggered == "select-all-drivers-btn":
        return [o["value"] for o in options]
    if triggered == "clear-drivers-btn":
        return []
    raise PreventUpdate


@app.callback(
    Output("select-all-drivers-btn", "style"),
    Output("clear-drivers-btn", "style"),
    Input("driver-checklist", "value"),
    State("driver-checklist", "options"),
)
def update_driver_action_button_styles(selected_values, options):
    if not options:
        return DRIVER_ACTION_BUTTON_BASE_STYLE, DRIVER_ACTION_BUTTON_BASE_STYLE

    selected = set(selected_values or [])
    all_values = {option["value"] for option in options}
    all_selected = bool(all_values) and selected == all_values
    none_selected = not selected

    select_style = DRIVER_ACTION_BUTTON_ACTIVE_STYLE if all_selected else DRIVER_ACTION_BUTTON_BASE_STYLE
    clear_style = DRIVER_ACTION_BUTTON_ACTIVE_STYLE if none_selected else DRIVER_ACTION_BUTTON_BASE_STYLE
    return select_style, clear_style
