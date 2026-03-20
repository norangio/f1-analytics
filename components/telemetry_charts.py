"""Telemetry chart figure builders using Plotly."""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.theme import FONT_STACK, resolve_plot_theme


def build_telemetry_figure(
    telemetry_data: dict[str, pd.DataFrame],
    driver_colors: dict[str, str],
    sector_distances: tuple[float | None, float | None] = (None, None),
    driver_line_styles: dict[str, str] | None = None,
    theme_name: str | None = None,
) -> go.Figure:
    """Build stacked Speed / Throttle / Brake subplots sharing x-axis (Distance)."""
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.45, 0.3, 0.25],
        vertical_spacing=0.04,
        subplot_titles=["Speed (km/h)", "Throttle (%)", "Brake"],
    )

    theme = resolve_plot_theme(theme_name)

    for driver, tel in telemetry_data.items():
        color = driver_colors.get(driver, theme["text_primary"])
        line_style = (driver_line_styles or {}).get(driver, "solid")

        fig.add_trace(
            go.Scatter(
                x=tel["Distance"],
                y=tel["Speed"],
                mode="lines",
                name=driver,
                line={"color": color, "width": 1.5, "dash": line_style},
                legendgroup=driver,
                hovertemplate=f"<b>{driver}</b><br>%{{x:.0f}} m<br>%{{y:.0f}} km/h<extra></extra>",
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=tel["Distance"],
                y=tel["Throttle"],
                mode="lines",
                name=driver,
                line={"color": color, "width": 1.5, "dash": line_style},
                legendgroup=driver,
                showlegend=False,
                hovertemplate=f"<b>{driver}</b><br>%{{x:.0f}} m<br>%{{y:.0f}}%<extra></extra>",
            ),
            row=2,
            col=1,
        )

        brake_y = tel["Brake"].astype(float) * 100
        fig.add_trace(
            go.Scatter(
                x=tel["Distance"],
                y=brake_y,
                mode="lines",
                fill="tozeroy",
                name=driver,
                line={"color": color, "width": 0.8, "dash": line_style},
                fillcolor=(
                    color.replace(")", ", 0.25)").replace("rgb", "rgba")
                    if color.startswith("rgb")
                    else _hex_to_rgba(color, 0.2)
                ),
                legendgroup=driver,
                showlegend=False,
                hovertemplate=f"<b>{driver}</b><br>%{{x:.0f}} m<br>Brake: %{{y:.0f}}%<extra></extra>",
            ),
            row=3,
            col=1,
        )

    s1_dist, s2_dist = sector_distances
    for dist in [s1_dist, s2_dist]:
        if dist is not None:
            for row in [1, 2, 3]:
                fig.add_vline(
                    x=dist,
                    line_width=1,
                    line_dash="dash",
                    line_color=theme["sector_line"],
                    row=row,
                    col=1,
                )

    _apply_chart_theme(fig, theme)
    return fig


def _apply_chart_theme(fig: go.Figure, theme: dict[str, str]) -> None:
    axis_defaults = {
        "gridcolor": theme["grid"],
        "gridwidth": 1,
        "linecolor": theme["axis"],
        "tickcolor": theme["axis"],
        "tickfont": {"color": theme["text"], "size": 11},
        "zeroline": False,
        "showgrid": True,
    }

    fig.update_layout(
        paper_bgcolor=theme["paper_bg"],
        plot_bgcolor=theme["plot_bg"],
        font={"color": theme["text"], "family": FONT_STACK},
        margin={"l": 55, "r": 20, "t": 32, "b": 40},
        hovermode="x unified",
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
        },
        height=520,
        dragmode="zoom",
    )

    for row in range(1, 4):
        fig.update_xaxes(row=row, col=1, **axis_defaults)
        fig.update_yaxes(row=row, col=1, **axis_defaults)

    fig.update_xaxes(row=3, col=1, title_text="Distance (m)", title_font={"size": 11, "color": theme["text"]})
    fig.update_yaxes(row=2, col=1, range=[0, 105])
    fig.update_yaxes(row=3, col=1, range=[0, 110], title_text="")

    for annotation in fig.layout.annotations:
        annotation.font = {"size": 11, "color": theme["text"]}
        annotation.x = 0
        annotation.xanchor = "left"


def empty_telemetry_figure(
    message: str = "Select a session and drivers to view telemetry",
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


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"
