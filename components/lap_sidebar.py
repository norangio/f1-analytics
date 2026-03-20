"""Lap time sidebar table component."""

import pandas as pd
from dash import html

from utils.theme import BORDER, PILL_RADIUS, TEXT_MUTED, TEXT_PRIMARY


def lap_sidebar_empty() -> html.Div:
    return html.Div(
        style={
            "padding": "24px 16px",
            "color": TEXT_MUTED,
            "fontSize": "13px",
            "textAlign": "center",
        },
        children="Load a session to see lap times.",
    )


def lap_sidebar_table(
    df: pd.DataFrame,
    driver_colors: dict[str, str],
    driver_numbers: dict[str, str] | None = None,
) -> html.Div:
    """Render sorted lap time + sector time table with restrained driver labels."""
    if df.empty:
        return lap_sidebar_empty()

    numbers = driver_numbers or {}
    rows = []
    for _, row in df.iterrows():
        driver = row["Driver"]
        color = driver_colors.get(driver, "#64748B")
        number = numbers.get(driver, "")
        label = f"{number} {driver}" if number else driver

        rows.append(
            html.Tr(
                style={"borderBottom": f"1px solid {BORDER}"},
                children=[
                    html.Td(
                        html.Span(
                            label,
                            style={
                                "color": "#FFFFFF",
                                "fontWeight": "700",
                                "fontSize": "11px",
                                "padding": "2px 6px",
                                "borderRadius": PILL_RADIUS,
                                "backgroundColor": _hex_to_rgba(color, 0.85),
                                "whiteSpace": "nowrap",
                            },
                        ),
                        style={"padding": "7px 8px 7px 4px"},
                    ),
                    html.Td(row["LapTime"], style=_td_style(bold=True)),
                    html.Td(row["S1"], style=_td_style()),
                    html.Td(row["S2"], style=_td_style()),
                    html.Td(row["S3"], style=_td_style()),
                ],
            )
        )

    return html.Div(
        style={"overflowY": "auto", "maxHeight": "calc(100vh - 300px)"},
        children=[
            html.Table(
                style={"width": "100%", "borderCollapse": "collapse"},
                children=[
                    html.Thead(
                        html.Tr(
                            children=[
                                html.Th(col, style=_th_style())
                                for col in ["Driver", "Lap", "S1", "S2", "S3"]
                            ]
                        )
                    ),
                    html.Tbody(rows),
                ],
            )
        ],
    )


def _th_style() -> dict:
    return {
        "fontSize": "10px",
        "fontWeight": "600",
        "letterSpacing": "0.08em",
        "textTransform": "uppercase",
        "color": TEXT_MUTED,
        "padding": "6px 8px",
        "textAlign": "left",
        "borderBottom": f"1px solid {BORDER}",
        "whiteSpace": "nowrap",
    }


def _td_style(bold: bool = False) -> dict:
    return {
        "fontSize": "12px",
        "fontFamily": "monospace",
        "color": TEXT_PRIMARY if bold else TEXT_MUTED,
        "fontWeight": "600" if bold else "400",
        "padding": "7px 8px",
        "whiteSpace": "nowrap",
    }


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"
