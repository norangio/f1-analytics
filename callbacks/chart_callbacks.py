"""Callback to render telemetry charts."""

from dash import Input, Output, State

from dash_app import app
from utils import f1_data
from utils.colors import assign_driver_line_styles
from components.telemetry_charts import build_telemetry_figure, empty_telemetry_figure


@app.callback(
    Output("telemetry-graph", "figure"),
    Input("driver-checklist", "value"),
    Input("lap-mode-dropdown", "value"),
    Input("lap-number-dropdown", "value"),
    State("session-store", "data"),
    State("driver-colors-store", "data"),
    prevent_initial_call=True,
)
def update_telemetry_chart(selected_drivers, lap_mode, lap_number, session_data, driver_colors):
    if not selected_drivers or session_data is None:
        return empty_telemetry_figure()
    if lap_mode == "specific" and lap_number is None:
        return empty_telemetry_figure("No valid lap numbers available for this session")

    year = session_data["year"]
    round_number = session_data["round"]
    session_key = session_data["session_key"]
    colors = driver_colors or {}
    line_styles = assign_driver_line_styles(selected_drivers)

    try:
        session = f1_data.load_session(year, round_number, session_key)
        effective_lap_number = lap_number if lap_mode == "specific" else None
        telemetry_data = f1_data.get_telemetry(
            session,
            selected_drivers,
            lap_mode=lap_mode,
            lap_number=effective_lap_number,
        )

        if not telemetry_data:
            if lap_mode == "specific":
                return empty_telemetry_figure("No telemetry for selected drivers on this lap")
            return empty_telemetry_figure("No telemetry data available for selected drivers")

        # Get sector distances using first available driver
        first_driver = next(iter(telemetry_data))
        sector_distances = f1_data.get_sector_distances(session, first_driver)

        return build_telemetry_figure(telemetry_data, colors, sector_distances, line_styles)

    except Exception as e:
        return empty_telemetry_figure(f"Error loading telemetry: {str(e)[:80]}")
