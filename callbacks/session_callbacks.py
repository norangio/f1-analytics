"""Callbacks for session selector: populate race dropdown, load session data."""

import dash
from dash import Input, Output, State, ctx
from dash.exceptions import PreventUpdate

from dash_app import app
from utils import f1_data
from utils.colors import assign_driver_colors


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
        session = f1_data.load_session(year, round_number, session_key)
        drivers = f1_data.get_drivers_in_session(session)
        colors = assign_driver_colors(drivers)

        session_label = f1_data.SESSION_TYPES.get(session_key, session_key)
        title = f"{year} · {session.event['EventName']} · {session_label}"
        status = f"Loaded — {len(drivers)} drivers"

        driver_numbers = f1_data.get_driver_numbers(session)

        store_data = {
            "year": year,
            "round": round_number,
            "session_key": session_key,
            "drivers": drivers,
            "driver_numbers": driver_numbers,
        }
        return store_data, status, title, colors
    except Exception as e:
        return dash.no_update, f"Error: {str(e)[:60]}", dash.no_update, dash.no_update


@app.callback(
    Output("driver-checklist", "options"),
    Output("driver-checklist", "value"),
    Input("session-store", "data"),
    State("driver-colors-store", "data"),
)
def update_driver_checklist(session_data, driver_colors):
    if session_data is None:
        raise PreventUpdate

    drivers = session_data.get("drivers", [])
    driver_numbers = session_data.get("driver_numbers", {})
    colors = driver_colors or {}

    options = []
    for driver in drivers:
        color = colors.get(driver, "#5C4A3A")
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
