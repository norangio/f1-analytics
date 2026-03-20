"""Callbacks for lap time boxplot tab and tab switching."""

from dash import Input, Output, State, clientside_callback

from dash_app import app
from utils import f1_data
from components.laptime_boxplot import (
    build_laptime_boxplot,
    empty_boxplot_figure,
    get_sorted_drivers_by_median,
)
from components.laptime_summary_table import build_laptime_summary_table, laptime_summary_empty

TELEMETRY_CONTENT_STYLE = {
    "display": "flex",
    "flex": "1",
}
LAPTIMES_CONTENT_STYLE = {
    "display": "flex",
    "flex": "1",
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


# Keep the theme store aligned with the OS-level preferred color scheme.
clientside_callback(
    """
    function(n, currentTheme) {
        const nextTheme = window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
        if (currentTheme === nextTheme) {
            return window.dash_clientside.no_update;
        }
        return nextTheme;
    }
    """,
    Output("theme-store", "data"),
    Input("theme-sync-interval", "n_intervals"),
    State("theme-store", "data"),
)


# Trigger Plotly resize after tab content becomes visible
clientside_callback(
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
    Output("laptime-summary-table", "children"),
    Input("main-tabs", "value"),
    Input("driver-checklist", "value"),
    Input("qualifying-phase-dropdown", "value"),
    Input("lap-mode-dropdown", "value"),
    Input("lap-number-dropdown", "value"),
    Input("laptime-robust-axis-toggle", "value"),
    Input("theme-store", "data"),
    State("session-store", "data"),
    State("driver-colors-store", "data"),
    prevent_initial_call=True,
)
def update_laptime_boxplot(
    tab,
    selected_drivers,
    qualifying_phase,
    lap_mode,
    lap_number,
    robust_axis_toggle,
    theme_name,
    session_data,
    driver_colors,
):
    if tab != "laptimes" or not selected_drivers or session_data is None:
        return empty_boxplot_figure(theme_name=theme_name), laptime_summary_empty()

    year = session_data["year"]
    round_number = session_data["round"]
    session_key = session_data["session_key"]
    colors = driver_colors or {}

    try:
        session = f1_data.load_session_laps(year, round_number, session_key)
        effective_phase = qualifying_phase if session_key == "Q" else "all"
        lap_data = f1_data.get_all_lap_times(
            session,
            selected_drivers,
            lap_mode=lap_mode or "all",
            lap_number=lap_number if lap_mode == "specific" else None,
            qualifying_phase=effective_phase or "all",
        )

        if lap_data.empty:
            return (
                empty_boxplot_figure("No lap time data available for selected drivers", theme_name=theme_name),
                laptime_summary_empty("No lap-time samples available for this selection."),
            )

        driver_order = get_sorted_drivers_by_median(lap_data)
        robust_axis = "robust" in (robust_axis_toggle or [])
        return (
            build_laptime_boxplot(
                lap_data,
                colors,
                driver_order=driver_order,
                robust_axis=robust_axis,
                theme_name=theme_name,
            ),
            build_laptime_summary_table(lap_data, driver_order=driver_order),
        )

    except Exception as e:
        return (
            empty_boxplot_figure(f"Error loading lap times: {str(e)[:80]}", theme_name=theme_name),
            laptime_summary_empty("Error loading lap-time summary."),
        )
