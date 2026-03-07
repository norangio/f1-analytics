"""Telemetry chart figure builders using Plotly."""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

BG_COLOR = "#F5EDE4"
PAPER_COLOR = "#F5EDE4"
GRID_COLOR = "rgba(0, 0, 0, 0.06)"
AXIS_COLOR = "#C8B8A8"
TEXT_COLOR = "#8A7060"
SECTOR_LINE_COLOR = "rgba(90, 60, 40, 0.18)"


def build_telemetry_figure(
    telemetry_data: dict[str, pd.DataFrame],
    driver_colors: dict[str, str],
    sector_distances: tuple[float | None, float | None] = (None, None),
) -> go.Figure:
    """
    Build stacked Speed / Throttle / Brake subplots sharing x-axis (Distance).
    """
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.45, 0.3, 0.25],
        vertical_spacing=0.04,
        subplot_titles=["Speed (km/h)", "Throttle (%)", "Brake"],
    )

    for driver, tel in telemetry_data.items():
        color = driver_colors.get(driver, "#FFFFFF")

        # Speed
        fig.add_trace(
            go.Scatter(
                x=tel["Distance"],
                y=tel["Speed"],
                mode="lines",
                name=driver,
                line={"color": color, "width": 1.5},
                legendgroup=driver,
                hovertemplate=f"<b>{driver}</b><br>%{{x:.0f}} m<br>%{{y:.0f}} km/h<extra></extra>",
            ),
            row=1,
            col=1,
        )

        # Throttle
        fig.add_trace(
            go.Scatter(
                x=tel["Distance"],
                y=tel["Throttle"],
                mode="lines",
                name=driver,
                line={"color": color, "width": 1.5},
                legendgroup=driver,
                showlegend=False,
                hovertemplate=f"<b>{driver}</b><br>%{{x:.0f}} m<br>%{{y:.0f}}%<extra></extra>",
            ),
            row=2,
            col=1,
        )

        # Brake — render as a filled area (0 or 100)
        brake_y = tel["Brake"].astype(float) * 100
        fig.add_trace(
            go.Scatter(
                x=tel["Distance"],
                y=brake_y,
                mode="lines",
                fill="tozeroy",
                name=driver,
                line={"color": color, "width": 0.8},
                fillcolor=color.replace(")", ", 0.25)").replace("rgb", "rgba") if color.startswith("rgb") else _hex_to_rgba(color, 0.2),
                legendgroup=driver,
                showlegend=False,
                hovertemplate=f"<b>{driver}</b><br>%{{x:.0f}} m<br>Brake: %{{y:.0f}}%<extra></extra>",
            ),
            row=3,
            col=1,
        )

    # Sector boundary lines
    s1_dist, s2_dist = sector_distances
    for dist in [s1_dist, s2_dist]:
        if dist is not None:
            for row in [1, 2, 3]:
                fig.add_vline(
                    x=dist,
                    line_width=1,
                    line_dash="dash",
                    line_color=SECTOR_LINE_COLOR,
                    row=row,
                    col=1,
                )

    _apply_chart_theme(fig)
    return fig


def _apply_chart_theme(fig: go.Figure) -> None:
    axis_defaults = {
        "gridcolor": GRID_COLOR,
        "gridwidth": 1,
        "linecolor": AXIS_COLOR,
        "tickcolor": AXIS_COLOR,
        "tickfont": {"color": TEXT_COLOR, "size": 11},
        "zeroline": False,
        "showgrid": True,
    }

    fig.update_layout(
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=BG_COLOR,
        font={"color": TEXT_COLOR, "family": "Inter, system-ui, sans-serif"},
        margin={"l": 55, "r": 20, "t": 32, "b": 40},
        hovermode="x unified",
        hoverlabel={
            "bgcolor": "#EDE3D8",
            "bordercolor": "#C8B8A8",
            "font": {"color": "#2C1810", "size": 12},
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
            "font": {"size": 12, "color": "#5C4030"},
            "bgcolor": "rgba(0,0,0,0)",
        },
        height=520,
        dragmode="zoom",
    )

    for i in range(1, 4):
        xref = f"x{i if i > 1 else ''} axis"
        yref = f"y{i if i > 1 else ''} axis"

        fig.update_xaxes(row=i, col=1, **axis_defaults)
        fig.update_yaxes(row=i, col=1, **axis_defaults)

    # x-axis label only on bottom
    fig.update_xaxes(row=3, col=1, title_text="Distance (m)", title_font={"size": 11, "color": TEXT_COLOR})
    # Throttle y fixed range
    fig.update_yaxes(row=2, col=1, range=[0, 105])
    # Brake y fixed range
    fig.update_yaxes(row=3, col=1, range=[0, 110], title_text="")

    # Subplot titles styling
    for annotation in fig.layout.annotations:
        annotation.font = {"size": 11, "color": TEXT_COLOR}
        annotation.x = 0
        annotation.xanchor = "left"


def empty_telemetry_figure(message: str = "Select a session and drivers to view telemetry") -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
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
                "font": {"color": "#8A7060", "size": 14},
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
