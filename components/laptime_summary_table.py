"""Summary table for lap time distribution by driver and tire compound."""

import pandas as pd
from dash import html

from components.laptime_boxplot import get_sorted_drivers_by_median
from utils.theme import BORDER, TEXT_MUTED, TEXT_PRIMARY


def laptime_summary_empty(
    message: str = "Load a session and select drivers to see lap-time summary stats.",
) -> html.Div:
    return html.Div(
        message,
        style={
            "padding": "10px 2px",
            "fontSize": "13px",
            "color": TEXT_MUTED,
        },
    )


def build_laptime_summary_table(
    lap_data: pd.DataFrame,
    driver_order: list[str] | None = None,
) -> html.Div:
    """Render summary stats where each column is a driver and each row is a stat."""
    if lap_data.empty:
        return laptime_summary_empty("No lap-time samples available for this selection.")

    data = lap_data.copy()
    data["Driver"] = data["Driver"].astype(str)
    sorted_drivers = driver_order or get_sorted_drivers_by_median(data)

    grouped = data.groupby("Driver")["LapTime"]
    summary = grouped.agg([
        ("Laps", "size"),
        ("Best", "min"),
        ("q25", lambda s: s.quantile(0.25)),
        ("median", "median"),
        ("q75", lambda s: s.quantile(0.75)),
    ])
    summary = summary.reindex(sorted_drivers)

    stat_rows = [
        ("Laps", False),
        ("Best", True),
        ("q25", True),
        ("median", True),
        ("q75", True),
    ]

    rows = []
    for stat_name, is_time in stat_rows:
        cells = [html.Td(stat_name, style=_td_style("left", bold=True))]
        for driver in sorted_drivers:
            value = summary.at[driver, stat_name] if driver in summary.index else None
            if pd.isna(value):
                display = "-"
            elif is_time:
                display = _format_laptime(float(value))
            else:
                display = str(int(value))
            cells.append(html.Td(display, style=_td_style("right", bold=(stat_name in ("Best", "median")))))

        rows.append(
            html.Tr(
                style={"borderBottom": f"1px solid {BORDER}"},
                children=cells,
            )
        )

    return html.Div(
        children=[
            html.Div("Lap-Time Summary", className="summary-heading"),
            html.Table(
                style={"width": "100%", "borderCollapse": "collapse"},
                children=[
                    html.Thead(
                        html.Tr(
                            children=[
                                html.Th("Stat", style=_th_style("left")),
                                *[html.Th(driver, style=_th_style("right")) for driver in sorted_drivers],
                            ]
                        )
                    ),
                    html.Tbody(rows),
                ],
            ),
        ]
    )


def _format_laptime(seconds: float) -> str:
    minutes = int(seconds // 60)
    secs = seconds % 60
    if minutes > 0:
        return f"{minutes}:{secs:06.3f}"
    return f"{secs:.3f}"


def _th_style(align: str) -> dict:
    return {
        "fontSize": "10px",
        "fontWeight": "700",
        "letterSpacing": "0.08em",
        "textTransform": "uppercase",
        "color": TEXT_MUTED,
        "padding": "8px 10px",
        "textAlign": align,
        "borderBottom": f"1px solid {BORDER}",
        "whiteSpace": "nowrap",
    }


def _td_style(align: str, bold: bool = False) -> dict:
    return {
        "fontSize": "12px",
        "fontFamily": "monospace",
        "color": TEXT_PRIMARY if bold else TEXT_MUTED,
        "fontWeight": "700" if bold else "500",
        "padding": "8px 10px",
        "textAlign": align,
        "whiteSpace": "nowrap",
    }
