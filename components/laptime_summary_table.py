"""Summary table for lap time distribution by tire compound."""

import pandas as pd
from dash import html

_COMPOUND_ORDER = {
    "SOFT": 0,
    "MEDIUM": 1,
    "HARD": 2,
    "INTERMEDIATE": 3,
    "WET": 4,
    "UNKNOWN": 5,
}


def laptime_summary_empty(
    message: str = "Load a session and select drivers to see compound quartiles.",
) -> html.Div:
    return html.Div(
        message,
        style={
            "padding": "10px 2px",
            "fontSize": "13px",
            "color": "#6B7280",
        },
    )


def build_laptime_summary_table(lap_data: pd.DataFrame) -> html.Div:
    """Render compound-level quartiles for the same data shown in the boxplot."""
    if lap_data.empty:
        return laptime_summary_empty("No lap-time samples available for this selection.")

    data = lap_data.copy()
    data["Compound"] = data["Compound"].fillna("UNKNOWN").astype(str).str.upper()

    grouped = data.groupby("Compound")["LapTime"]
    summary = grouped.quantile([0.25, 0.5, 0.75]).unstack()
    summary = summary.rename(columns={0.25: "Q1", 0.5: "Median", 0.75: "Q3"})
    summary["Laps"] = grouped.size()
    summary = summary.reset_index()
    summary["SortKey"] = summary["Compound"].map(lambda c: _COMPOUND_ORDER.get(c, 999))
    summary = summary.sort_values(["SortKey", "Compound"]).drop(columns=["SortKey"])

    rows = []
    for _, row in summary.iterrows():
        rows.append(
            html.Tr(
                style={"borderBottom": "1px solid #E5E7EB"},
                children=[
                    html.Td(row["Compound"].title(), style=_td_style("left", bold=True)),
                    html.Td(str(int(row["Laps"])), style=_td_style("right")),
                    html.Td(_format_laptime(float(row["Q1"])), style=_td_style("right")),
                    html.Td(_format_laptime(float(row["Median"])), style=_td_style("right", bold=True)),
                    html.Td(_format_laptime(float(row["Q3"])), style=_td_style("right")),
                ],
            )
        )

    return html.Div(
        children=[
            html.Div(
                "Lap-Time Summary by Compound",
                style={
                    "fontSize": "12px",
                    "fontWeight": "700",
                    "letterSpacing": "0.06em",
                    "textTransform": "uppercase",
                    "color": "#4B5563",
                    "marginBottom": "10px",
                },
            ),
            html.Table(
                style={"width": "100%", "borderCollapse": "collapse"},
                children=[
                    html.Thead(
                        html.Tr(
                            children=[
                                html.Th("Compound", style=_th_style("left")),
                                html.Th("Laps", style=_th_style("right")),
                                html.Th("Q1", style=_th_style("right")),
                                html.Th("Median", style=_th_style("right")),
                                html.Th("Q3", style=_th_style("right")),
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
        "color": "#6B7280",
        "padding": "8px 10px",
        "textAlign": align,
        "borderBottom": "1px solid #D1D5DB",
        "whiteSpace": "nowrap",
    }


def _td_style(align: str, bold: bool = False) -> dict:
    return {
        "fontSize": "12px",
        "fontFamily": "monospace",
        "color": "#111827" if bold else "#4B5563",
        "fontWeight": "700" if bold else "500",
        "padding": "8px 10px",
        "textAlign": align,
        "whiteSpace": "nowrap",
    }
