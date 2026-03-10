"""Lap time boxplot figure builder with tire compound markers."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

BG_COLOR = "#FFFFFF"
PAPER_COLOR = "#F8FAFC"
GRID_COLOR = "rgba(148, 163, 184, 0.22)"
AXIS_COLOR = "#D1D5DB"
TEXT_COLOR = "#4B5563"
WHISKER_COLOR = "#374151"

# F1 tire compound colors and marker shapes
COMPOUND_MARKERS = {
    "SOFT": {"symbol": "circle", "color": "#DC2626"},
    "MEDIUM": {"symbol": "diamond", "color": "#F59E0B"},
    "HARD": {"symbol": "square", "color": "#6B7280"},
    "INTERMEDIATE": {"symbol": "triangle-up", "color": "#10B981"},
    "WET": {"symbol": "star", "color": "#3B82F6"},
    "UNKNOWN": {"symbol": "x", "color": "#9CA3AF"},
}


def build_laptime_boxplot(
    lap_data: pd.DataFrame,
    driver_colors: dict[str, str],
    driver_order: list[str] | None = None,
) -> go.Figure:
    """
    Build boxplot of lap times per driver with tire compound scatter overlay.
    Drivers sorted by median lap time (fastest left).
    """
    if lap_data.empty:
        return empty_boxplot_figure()

    sorted_drivers = driver_order or get_sorted_drivers_by_median(lap_data)

    fig = go.Figure()
    rng = np.random.RandomState(42)

    # Add box per driver
    for i, driver in enumerate(sorted_drivers):
        driver_data = lap_data[lap_data["Driver"] == driver]
        color = driver_colors.get(driver, "#9CA3AF")

        fig.add_trace(go.Box(
            y=driver_data["LapTime"].values,
            x=[i] * len(driver_data),
            name=driver,
            boxpoints=False,
            line={"color": WHISKER_COLOR, "width": 1.2},
            fillcolor=_hex_to_rgba(color, 0.35),
            whiskerwidth=0.5,
            width=0.45,
            showlegend=False,
            hoverinfo="skip",
        ))

    # Overlay compound scatter points with jitter
    compounds_in_data = sorted(lap_data["Compound"].unique())
    for compound in compounds_in_data:
        marker_info = COMPOUND_MARKERS.get(compound, COMPOUND_MARKERS["UNKNOWN"])
        compound_data = lap_data[lap_data["Compound"] == compound]

        x_positions = []
        for _, row in compound_data.iterrows():
            driver_idx = sorted_drivers.index(row["Driver"])
            jitter = rng.uniform(-0.16, 0.16)
            x_positions.append(driver_idx + jitter)

        fig.add_trace(go.Scatter(
            x=x_positions,
            y=compound_data["LapTime"].values,
            mode="markers",
            name=compound.title(),
            marker={
                "symbol": marker_info["symbol"],
                "color": marker_info["color"],
                "size": 5,
                "opacity": 0.65,
                "line": {"width": 0.5, "color": WHISKER_COLOR},
            },
            legendgroup=f"compound-{compound}",
            hovertemplate=(
                "<b>%{text}</b><br>"
                + compound.title()
                + "<br>%{customdata}<extra></extra>"
            ),
            text=compound_data["Driver"].values,
            customdata=[_format_laptime(t) for t in compound_data["LapTime"].values],
        ))

    _apply_boxplot_theme(fig, sorted_drivers, lap_data["LapTime"])
    return fig


def get_sorted_drivers_by_median(lap_data: pd.DataFrame) -> list[str]:
    """Return drivers sorted by median lap time (fastest left)."""
    medians = lap_data.groupby("Driver")["LapTime"].median().sort_values()
    return medians.index.tolist()


def empty_boxplot_figure(
    message: str = "Select a session and drivers to view lap time distribution",
) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        margin={"l": 55, "r": 20, "t": 32, "b": 40},
        height=520,
        annotations=[{
            "text": message,
            "xref": "paper",
            "yref": "paper",
            "x": 0.5,
            "y": 0.5,
            "showarrow": False,
            "font": {"color": "#6B7280", "size": 14},
        }],
        xaxis={"visible": False},
        yaxis={"visible": False},
    )
    return fig


def _apply_boxplot_theme(
    fig: go.Figure,
    sorted_drivers: list[str],
    lap_times: pd.Series,
) -> None:
    y_min = float(lap_times.min())
    y_max = float(lap_times.max())
    y_range = y_max - y_min
    margin = max(y_range * 0.06, 0.5)

    # Choose tick interval based on range
    if y_range > 30:
        interval = 5.0
    elif y_range > 15:
        interval = 2.0
    else:
        interval = 1.0

    tick_start = np.floor((y_min - margin) / interval) * interval
    tick_end = np.ceil((y_max + margin) / interval) * interval
    tick_vals = np.arange(tick_start, tick_end + interval * 0.5, interval)
    tick_text = [_format_laptime(v) for v in tick_vals]

    axis_defaults = {
        "gridcolor": GRID_COLOR,
        "gridwidth": 1,
        "linecolor": AXIS_COLOR,
        "tickcolor": AXIS_COLOR,
        "tickfont": {"color": TEXT_COLOR, "size": 11},
        "zeroline": False,
    }

    fig.update_layout(
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=BG_COLOR,
        font={"color": TEXT_COLOR, "family": "Inter, system-ui, sans-serif"},
        margin={"l": 65, "r": 20, "t": 20, "b": 50},
        hovermode="closest",
        hoverlabel={
            "bgcolor": "#FFFFFF",
            "bordercolor": "#D1D5DB",
            "font": {"color": "#111827", "size": 12},
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
            "font": {"size": 12, "color": "#374151"},
            "bgcolor": "rgba(0,0,0,0)",
            "title": {"text": "Compound", "font": {"size": 11, "color": "#6B7280"}},
        },
        height=520,
        dragmode="zoom",
    )

    fig.update_xaxes(
        tickvals=list(range(len(sorted_drivers))),
        ticktext=sorted_drivers,
        tickfont={"size": 12, "color": TEXT_COLOR, "family": "Inter, system-ui, sans-serif"},
        showgrid=False,
        linecolor=AXIS_COLOR,
        tickcolor=AXIS_COLOR,
    )

    fig.update_yaxes(
        tickvals=tick_vals.tolist(),
        ticktext=tick_text,
        range=[y_min - margin, y_max + margin],
        title_text="Lap Time",
        title_font={"size": 11, "color": TEXT_COLOR},
        showgrid=True,
        **axis_defaults,
    )


def _format_laptime(seconds: float) -> str:
    minutes = int(seconds // 60)
    secs = seconds % 60
    if minutes > 0:
        return f"{minutes}:{secs:06.3f}"
    return f"{secs:.3f}"


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return f"rgba(156, 163, 175, {alpha})"
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"
