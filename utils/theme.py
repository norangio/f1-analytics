"""Shared theme tokens for Dash layout styles and Plotly figures."""

FONT_STACK = 'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'


def css_var(token: str) -> str:
    """Return a CSS custom property reference."""
    return f"var(--{token})"


BG_BASE = css_var("bg-base")
BG_SURFACE = css_var("bg-surface")
BG_SURFACE_HOVER = css_var("bg-surface-hover")
BORDER = css_var("border")
ACCENT = css_var("accent")
ACCENT_DIM = css_var("accent-dim")
TEXT_PRIMARY = css_var("text-primary")
TEXT_MUTED = css_var("text-muted")
SHADOW_SUBTLE = css_var("shadow-subtle")
CARD_RADIUS = css_var("radius-card")
PILL_RADIUS = css_var("radius-pill")

SECTION_LABEL_STYLE = {
    "fontSize": "11px",
    "fontWeight": "600",
    "letterSpacing": "0.08em",
    "textTransform": "uppercase",
    "color": TEXT_MUTED,
}

PLOT_THEMES = {
    "dark": {
        "paper_bg": "#1A1F2E",
        "plot_bg": "#1A1F2E",
        "grid": "rgba(100, 116, 139, 0.18)",
        "axis": "#252D3D",
        "text": "#64748B",
        "text_primary": "#F1F5F9",
        "hover_bg": "#1E2536",
        "hover_border": "#252D3D",
        "sector_line": "rgba(100, 116, 139, 0.28)",
        "median_outline": "#1A1F2E",
        "whisker": "#F1F5F9",
    },
    "light": {
        "paper_bg": "#FFFFFF",
        "plot_bg": "#FFFFFF",
        "grid": "rgba(100, 116, 139, 0.16)",
        "axis": "#E2E8F0",
        "text": "#64748B",
        "text_primary": "#0F172A",
        "hover_bg": "#F1F5F9",
        "hover_border": "#E2E8F0",
        "sector_line": "rgba(100, 116, 139, 0.22)",
        "median_outline": "#FFFFFF",
        "whisker": "#334155",
    },
}


def resolve_plot_theme(theme_name: str | None) -> dict[str, str]:
    """Return the requested Plotly theme, defaulting to the app's dark mode."""
    return PLOT_THEMES["light"] if theme_name == "light" else PLOT_THEMES["dark"]
