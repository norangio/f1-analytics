"""Lap time violin plot figure builder with tire compound markers."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from utils.theme import FONT_STACK, resolve_plot_theme

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
    robust_axis: bool = False,
    theme_name: str | None = None,
) -> go.Figure:
    """Build violin plot of lap times per driver with tire compound scatter overlay."""
    if lap_data.empty:
        return empty_boxplot_figure(theme_name=theme_name)

    sorted_drivers = driver_order or get_sorted_drivers_by_median(lap_data)
    theme = resolve_plot_theme(theme_name)

    fig = go.Figure()
    rng = np.random.RandomState(42)

    violin_width, point_jitter = _get_plot_spacing(len(sorted_drivers))

    for i, driver in enumerate(sorted_drivers):
        driver_data = lap_data[lap_data["Driver"] == driver]
        color = driver_colors.get(driver, theme["text_primary"])

        fig.add_trace(
            go.Violin(
                y=driver_data["LapTime"].values,
                x=[i] * len(driver_data),
                name=driver,
                points=False,
                line={"color": theme["whisker"], "width": 1.2},
                fillcolor=_hex_to_rgba(color, 0.35),
                width=violin_width,
                box_visible=False,
                meanline_visible=False,
                showlegend=False,
                hoverinfo="skip",
            )
        )

    median_series = lap_data.groupby("Driver")["LapTime"].median().reindex(sorted_drivers)
    fig.add_trace(
        go.Scatter(
            x=list(range(len(sorted_drivers))),
            y=median_series.values,
            mode="markers",
            name="Median",
            marker={
                "color": theme["text_primary"],
                "size": 7,
                "line": {"color": theme["median_outline"], "width": 0.8},
            },
            hovertemplate="<b>%{text}</b><br>Median<br>%{customdata}<extra></extra>",
            text=median_series.index.tolist(),
            customdata=[_format_laptime(value) for value in median_series.values],
        )
    )

    compounds_in_data = sorted(lap_data["Compound"].unique())
    for compound in compounds_in_data:
        marker_info = COMPOUND_MARKERS.get(compound, COMPOUND_MARKERS["UNKNOWN"])
        compound_data = lap_data[lap_data["Compound"] == compound]

        x_positions = []
        for _, row in compound_data.iterrows():
            driver_idx = sorted_drivers.index(row["Driver"])
            jitter = rng.uniform(-point_jitter, point_jitter)
            x_positions.append(driver_idx + jitter)

        fig.add_trace(
            go.Scatter(
                x=x_positions,
                y=compound_data["LapTime"].values,
                mode="markers",
                name=compound.title(),
                marker={
                    "symbol": marker_info["symbol"],
                    "color": marker_info["color"],
                    "size": 5,
                    "opacity": 0.7,
                    "line": {"width": 0.5, "color": theme["whisker"]},
                },
                legendgroup=f"compound-{compound}",
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    + compound.title()
                    + "<br>Lap Time: %{customdata[1]}"
                    + "<br>Lap: %{customdata[2]}"
                    + "<br>Session: %{customdata[3]}<extra></extra>"
                ),
                customdata=np.stack(
                    [
                        compound_data["Driver"].fillna("-").astype(str).values,
                        np.array([_format_laptime(t) for t in compound_data["LapTime"].values]),
                        compound_data.get("LapNumber", pd.Series(index=compound_data.index, dtype="object"))
                        .fillna("-")
                        .astype(int, errors="ignore")
                        .astype(str)
                        .values,
                        compound_data.get("SessionId", pd.Series(index=compound_data.index, dtype="object"))
                        .fillna("-")
                        .astype(str)
                        .values,
                    ],
                    axis=-1,
                ),
            )
        )

    _apply_boxplot_theme(fig, sorted_drivers, lap_data["LapTime"], theme, robust_axis=robust_axis)
    return fig


def get_sorted_drivers_by_median(lap_data: pd.DataFrame) -> list[str]:
    """Return drivers sorted by median lap time (fastest left)."""
    medians = lap_data.groupby("Driver")["LapTime"].median().sort_values()
    return medians.index.tolist()


def empty_boxplot_figure(
    message: str = "Select a session and drivers to view lap time distribution",
    theme_name: str | None = None,
) -> go.Figure:
    theme = resolve_plot_theme(theme_name)
    fig = go.Figure()
    fig.update_layout(
        paper_bgcolor=theme["paper_bg"],
        plot_bgcolor=theme["plot_bg"],
        margin={"l": 55, "r": 20, "t": 32, "b": 40},
        height=520,
        annotations=[
            {
                "text": message,
                "xref": "paper",
                "yref": "paper",
                "x": 0.5,
                "y": 0.5,
                "showarrow": False,
                "font": {"color": theme["text"], "size": 14},
            }
        ],
        xaxis={"visible": False},
        yaxis={"visible": False},
    )
    return fig


def _apply_boxplot_theme(
    fig: go.Figure,
    sorted_drivers: list[str],
    lap_times: pd.Series,
    theme: dict[str, str],
    robust_axis: bool = False,
) -> None:
    y_min = float(lap_times.min())
    y_max = float(lap_times.max())
    if robust_axis:
        p05 = float(np.percentile(lap_times.values, 5))
        p95 = float(np.percentile(lap_times.values, 95))
        y_min, y_max = p05, p95

    y_range = y_max - y_min
    margin = max(y_range * 0.08, 0.35)

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
        "gridcolor": theme["grid"],
        "gridwidth": 1,
        "linecolor": theme["axis"],
        "tickcolor": theme["axis"],
        "tickfont": {"color": theme["text"], "size": 11},
        "zeroline": False,
    }

    fig.update_layout(
        paper_bgcolor=theme["paper_bg"],
        plot_bgcolor=theme["plot_bg"],
        font={"color": theme["text"], "family": FONT_STACK},
        margin={"l": 65, "r": 20, "t": 20, "b": 50},
        hovermode="closest",
        hoverlabel={
            "bgcolor": theme["hover_bg"],
            "bordercolor": theme["hover_border"],
            "font": {"color": theme["text_primary"], "size": 12},
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
            "font": {"size": 12, "color": theme["text_primary"]},
            "bgcolor": "rgba(0,0,0,0)",
            "title": {"text": "Compound", "font": {"size": 11, "color": theme["text"]}},
        },
        height=520,
        dragmode="zoom",
    )

    if robust_axis:
        fig.add_annotation(
            text="Y-axis: 5th–95th percentile range",
            xref="paper",
            yref="paper",
            x=1,
            y=1.13,
            showarrow=False,
            xanchor="right",
            font={"size": 11, "color": theme["text"]},
        )

    fig.update_xaxes(
        tickvals=list(range(len(sorted_drivers))),
        ticktext=sorted_drivers,
        tickfont={"size": 12, "color": theme["text"], "family": FONT_STACK},
        showgrid=False,
        linecolor=theme["axis"],
        tickcolor=theme["axis"],
    )

    fig.update_yaxes(
        tickvals=tick_vals.tolist(),
        ticktext=tick_text,
        range=[y_min - margin, y_max + margin],
        title_text="Lap Time",
        title_font={"size": 11, "color": theme["text"]},
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


def _get_plot_spacing(driver_count: int) -> tuple[float, float]:
    if driver_count <= 3:
        return 0.34, 0.2
    if driver_count <= 6:
        return 0.4, 0.17
    return 0.46, 0.14
