"""Driver color mapping — pastel team colors."""

# Medium-depth team colors — readable on tan/parchment background
TEAM_COLORS = {
    "Red Bull":       "#3B6BB5",  # deep navy blue
    "Ferrari":        "#D03030",  # deep red
    "Mercedes":       "#0F9B8E",  # deep teal
    "McLaren":        "#D4650A",  # deep papaya orange
    "Aston Martin":   "#1A7A48",  # deep British racing green
    "Alpine":         "#3B68C8",  # deep blue
    "Williams":       "#1A7AB0",  # deep royal blue
    "Racing Bulls":   "#5A38A8",  # deep indigo/purple
    "Kick Sauber":    "#2D8A30",  # deep green
    "Audi":           "#6E6E6E",  # medium-dark grey
    "Cadillac":       "#000000",  # black
    "Haas":           "#B03030",  # deep muted red
}

# Driver abbreviation → team (covers 2025 + 2026 grid)
DRIVER_TEAM = {
    # Red Bull
    "VER": "Red Bull",   "LAW": "Red Bull",
    # McLaren
    "NOR": "McLaren",    "PIA": "McLaren",
    # Ferrari
    "LEC": "Ferrari",    "HAM": "Ferrari",
    # Mercedes
    "RUS": "Mercedes",   "ANT": "Mercedes",
    # Aston Martin
    "ALO": "Aston Martin", "STR": "Aston Martin",
    # Alpine
    "GAS": "Alpine",     "DOO": "Alpine",   "COL": "Alpine",
    # Williams
    "ALB": "Williams",   "SAI": "Williams",
    # Racing Bulls
    "TSU": "Racing Bulls", "HAD": "Racing Bulls", "RIC": "Racing Bulls",
    # Audi
    "HUL": "Audi", "BOR": "Audi",
    # Kick Sauber (legacy)
    "ZHO": "Kick Sauber",
    # Cadillac
    "BOT": "Cadillac", "PER": "Cadillac",
    # Haas
    "OCO": "Haas",       "BEA": "Haas",     "MAG": "Haas",
    # Legacy (pre-2025)
    "SAR": "Williams",
}

# Fallback palette for unrecognised drivers
_FALLBACK = [
    "#4878B0", "#2E8A50", "#C04040", "#7040A8",
    "#B06820", "#207898", "#A03878", "#608830",
]


def get_driver_color(abbreviation: str) -> str:
    team = DRIVER_TEAM.get(abbreviation)
    if team:
        return TEAM_COLORS.get(team, _FALLBACK[0])
    return _FALLBACK[hash(abbreviation) % len(_FALLBACK)]


def get_driver_team(abbreviation: str) -> str | None:
    return DRIVER_TEAM.get(abbreviation)


def assign_driver_colors(driver_list: list[str]) -> dict[str, str]:
    return {driver: get_driver_color(driver) for driver in driver_list}


def assign_driver_line_styles(driver_list: list[str]) -> dict[str, str]:
    """Assign dashed style to teammates so same-color traces stay distinct."""
    seen_by_team = {}
    styles = {}
    for driver in driver_list:
        team = get_driver_team(driver) or driver
        count = seen_by_team.get(team, 0)
        styles[driver] = "solid" if count == 0 else "dot"
        seen_by_team[team] = count + 1
    return styles
