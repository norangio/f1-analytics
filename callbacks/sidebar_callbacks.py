"""Callback to render the lap times sidebar."""

from dash import Input, Output, State
from dash.exceptions import PreventUpdate

from dash_app import app
from utils import f1_data
from components.lap_sidebar import lap_sidebar_table, lap_sidebar_empty


@app.callback(
    Output("lap-times-sidebar", "children"),
    Input("session-store", "data"),
    Input("qualifying-phase-dropdown", "value"),
    State("driver-colors-store", "data"),
)
def update_lap_sidebar(session_data, qualifying_phase, driver_colors):
    if session_data is None:
        return lap_sidebar_empty()

    year = session_data["year"]
    round_number = session_data["round"]
    session_key = session_data["session_key"]
    colors = driver_colors or {}

    try:
        session = f1_data.load_session(year, round_number, session_key)
        effective_phase = qualifying_phase if session_key == "Q" else "all"
        df = f1_data.get_lap_times_table(session, qualifying_phase=effective_phase or "all")
        driver_numbers = session_data.get("driver_numbers", {})
        return lap_sidebar_table(df, colors, driver_numbers)
    except Exception as e:
        return lap_sidebar_empty()
