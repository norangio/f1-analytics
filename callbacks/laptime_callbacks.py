"""Callbacks for lap time boxplot tab and tab switching."""

from dash import Input, Output, State, clientside_callback

from dash_app import app
from utils import f1_data
from components.laptime_boxplot import build_laptime_boxplot, empty_boxplot_figure

TELEMETRY_CONTENT_STYLE = {
    "display": "flex",
    "gap": "0",
    "flex": "1",
}
LAPTIMES_CONTENT_STYLE = {
    "flex": "1",
    "padding": "20px 24px",
}


@app.callback(
    Output("telemetry-content", "style"),
    Output("laptimes-content", "style"),
    Input("main-tabs", "value"),
)
def switch_tab(tab):
    if tab == "telemetry":
        return TELEMETRY_CONTENT_STYLE, {"display": "none"}
    return {"display": "none"}, LAPTIMES_CONTENT_STYLE


# Trigger Plotly resize after tab content becomes visible
app.clientside_callback(
    """
    function(tab) {
        if (tab === 'laptimes') {
            setTimeout(function() {
                window.dispatchEvent(new Event('resize'));
            }, 80);
        }
        return dash_clientside.no_update;
    }
    """,
    Output("laptime-boxplot-graph", "className"),
    Input("main-tabs", "value"),
)


@app.callback(
    Output("laptime-boxplot-graph", "figure"),
    Input("main-tabs", "value"),
    Input("driver-checklist", "value"),
    Input("qualifying-phase-dropdown", "value"),
    State("session-store", "data"),
    State("driver-colors-store", "data"),
    prevent_initial_call=True,
)
def update_laptime_boxplot(tab, selected_drivers, qualifying_phase, session_data, driver_colors):
    if tab != "laptimes" or not selected_drivers or session_data is None:
        return empty_boxplot_figure()

    year = session_data["year"]
    round_number = session_data["round"]
    session_key = session_data["session_key"]
    colors = driver_colors or {}

    try:
        session = f1_data.load_session(year, round_number, session_key)
        effective_phase = qualifying_phase if session_key == "Q" else "all"
        lap_data = f1_data.get_all_lap_times(
            session,
            selected_drivers,
            qualifying_phase=effective_phase or "all",
        )

        if lap_data.empty:
            return empty_boxplot_figure("No lap time data available for selected drivers")

        return build_laptime_boxplot(lap_data, colors)

    except Exception as e:
        return empty_boxplot_figure(f"Error loading lap times: {str(e)[:80]}")
