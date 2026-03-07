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
    # Kick Sauber / Audi
    "HUL": "Kick Sauber", "BOR": "Kick Sauber",  "ZHO": "Kick Sauber",
    # Haas
    "OCO": "Haas",       "BEA": "Haas",     "MAG": "Haas",
    # Legacy (pre-2025)
    "PER": "Red Bull",   "SAR": "Williams", "BOT": "Kick Sauber",
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


def assign_driver_colors(driver_list: list[str]) -> dict[str, str]:
    return {driver: get_driver_color(driver) for driver in driver_list}
