"""FastF1 data loading helpers with disk caching."""

import os
import fastf1
import pandas as pd

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "cache")
fastf1.Cache.enable_cache(os.path.abspath(CACHE_DIR))

SUPPORTED_YEARS = list(range(2021, 2027))
SESSION_TYPES = {
    "FP1": "Practice 1",
    "FP2": "Practice 2",
    "FP3": "Practice 3",
    "Q": "Qualifying",
    "R": "Race",
    "S": "Sprint",
    "SQ": "Sprint Qualifying",
}
QUALIFYING_PHASES = {
    "all": "All",
    "Q1": "Q1",
    "Q2": "Q2",
    "Q3": "Q3",
}


def get_event_schedule(year: int) -> list[dict]:
    """Return list of {round, name} for all events in a season."""
    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        events = []
        for _, row in schedule.iterrows():
            events.append({
                "round": int(row["RoundNumber"]),
                "name": row["EventName"],
            })
        return events
    except Exception:
        return []


def get_available_sessions(year: int, round_number: int) -> list[dict]:
    """Return session types available for a given event."""
    try:
        event = fastf1.get_event(year, round_number)
        available = []
        for key, label in SESSION_TYPES.items():
            try:
                session = event.get_session(key)
                available.append({"key": key, "label": label})
            except Exception:
                pass
        return available
    except Exception:
        return [{"key": k, "label": v} for k, v in SESSION_TYPES.items()]


def load_session(year: int, round_number: int, session_key: str) -> fastf1.core.Session:
    """Load and return a FastF1 session with telemetry data."""
    session = fastf1.get_session(year, round_number, session_key)
    session.load(telemetry=True, laps=True, weather=False, messages=False)
    return session


def get_drivers_in_session(session: fastf1.core.Session) -> list[str]:
    """Return sorted list of driver abbreviations from session results."""
    try:
        results = session.results
        if results is not None and not results.empty and "Abbreviation" in results.columns:
            abbrevs = results["Abbreviation"].dropna().tolist()
            if abbrevs:
                return sorted(abbrevs)
    except Exception:
        pass
    # Fallback: session.drivers is car numbers, return as-is
    return sorted(session.drivers)


def get_driver_numbers(session: fastf1.core.Session) -> dict[str, str]:
    """Return mapping of abbreviation → car number string."""
    try:
        results = session.results
        if results is not None and not results.empty:
            mapping = {}
            for _, row in results.iterrows():
                abbrev = row.get("Abbreviation")
                number = row.get("DriverNumber")
                if abbrev and number:
                    mapping[str(abbrev)] = str(int(float(number)))
            return mapping
    except Exception:
        pass
    return {}


def get_available_lap_numbers(session: fastf1.core.Session) -> list[int]:
    """Return sorted lap numbers in this session that have valid lap times."""
    try:
        laps = session.laps
        if laps is None or laps.empty:
            return []

        valid_laps = laps[laps["LapTime"].notna()]
        lap_numbers = valid_laps["LapNumber"].dropna().astype(int)
        if lap_numbers.empty:
            return []

        return sorted(lap_numbers.unique().tolist())
    except Exception:
        return []


def get_qualifying_phase_lap_numbers(session: fastf1.core.Session) -> dict[str, list[int]]:
    """Return lap numbers grouped by qualifying phase (Q1/Q2/Q3)."""
    phase_laps = {}
    for phase in ("Q1", "Q2", "Q3"):
        laps = _get_qualifying_phase_laps(session, phase)
        if laps is None or laps.empty:
            phase_laps[phase] = []
            continue

        try:
            numbers = laps["LapNumber"].dropna().astype(int).unique().tolist()
            phase_laps[phase] = sorted(numbers)
        except Exception:
            phase_laps[phase] = []
    return phase_laps


def get_lap_times_table(
    session: fastf1.core.Session,
    qualifying_phase: str = "all",
) -> pd.DataFrame:
    """
    Return a DataFrame of fastest lap times + sector times per driver,
    sorted fastest to slowest.
    """
    rows = []
    for driver in get_drivers_in_session(session):
        driver_laps = session.laps.pick_driver(driver)
        driver_laps = _filter_laps_by_qualifying_phase(session, driver_laps, qualifying_phase)
        if driver_laps.empty:
            continue
        try:
            fastest = driver_laps.pick_fastest()
            rows.append({
                "Driver": driver,
                "LapTime": fastest["LapTime"],
                "S1": fastest["Sector1Time"],
                "S2": fastest["Sector2Time"],
                "S3": fastest["Sector3Time"],
            })
        except Exception:
            continue

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df = df.dropna(subset=["LapTime"])
    df = df.sort_values("LapTime").reset_index(drop=True)
    df["LapTime"] = df["LapTime"].apply(_format_timedelta)
    df["S1"] = df["S1"].apply(_format_timedelta)
    df["S2"] = df["S2"].apply(_format_timedelta)
    df["S3"] = df["S3"].apply(_format_timedelta)
    return df


def get_telemetry(
    session: fastf1.core.Session,
    drivers: list[str],
    lap_mode: str = "fastest",
    lap_number: int | None = None,
    qualifying_phase: str = "all",
) -> dict[str, pd.DataFrame]:
    """
    Return telemetry DataFrames keyed by driver abbreviation.
    Each DataFrame has columns: Distance, Speed, Throttle, Brake.
    lap_mode: "fastest" | "specific"
    """
    result = {}
    for driver in drivers:
        driver_laps = session.laps.pick_driver(driver)
        driver_laps = _filter_laps_by_qualifying_phase(session, driver_laps, qualifying_phase)
        if driver_laps.empty:
            continue
        try:
            if lap_mode == "specific" and lap_number is not None:
                lap = driver_laps[driver_laps["LapNumber"] == lap_number]
                if lap.empty:
                    continue
                lap = lap.iloc[0]
            else:
                lap = driver_laps.pick_fastest()

            tel = lap.get_telemetry().add_distance()
            tel = tel[["Distance", "Speed", "Throttle", "Brake"]].dropna()
            result[driver] = tel
        except Exception:
            continue
    return result


def get_sector_distances(
    session: fastf1.core.Session,
    driver: str,
    qualifying_phase: str = "all",
) -> tuple[float | None, float | None]:
    """
    Return approximate (sector1_end_distance, sector2_end_distance) in meters
    for the fastest lap of a driver.
    """
    try:
        driver_laps = session.laps.pick_driver(driver)
        driver_laps = _filter_laps_by_qualifying_phase(session, driver_laps, qualifying_phase)
        if driver_laps.empty:
            return None, None

        lap = driver_laps.pick_fastest()
        tel = lap.get_telemetry().add_distance()
        total = float(tel["Distance"].max())
        # Estimate sector splits from timing if available
        s1 = lap["Sector1Time"]
        s2 = lap["Sector2Time"]
        s3 = lap["Sector3Time"]
        lap_time = lap["LapTime"]
        if pd.isna(s1) or pd.isna(lap_time):
            return None, None
        s1_frac = s1.total_seconds() / lap_time.total_seconds()
        s2_frac = (s1 + s2).total_seconds() / lap_time.total_seconds()
        return total * s1_frac, total * s2_frac
    except Exception:
        return None, None


def get_all_lap_times(
    session: fastf1.core.Session,
    drivers: list[str],
    lap_mode: str = "all",
    lap_number: int | None = None,
    qualifying_phase: str = "all",
) -> pd.DataFrame:
    """
    Return DataFrame of valid lap times for selected drivers and lap mode.
    Columns: Driver, LapTime (float seconds), Compound (str),
    LapNumber (int), SessionId (str).
    Excludes pit in/out laps.
    lap_mode: "all" | "fastest" | "specific"
    """
    rows = []
    session_id = _get_session_id(session)
    selected_qual_phase = qualifying_phase if qualifying_phase in ("Q1", "Q2", "Q3") else None
    qual_phase_lookup = _get_qualifying_phase_lookup(session) if session_id == "Q" and qualifying_phase == "all" else {}
    for driver in drivers:
        driver_laps = session.laps.pick_drivers(driver)
        driver_laps = _filter_laps_by_qualifying_phase(session, driver_laps, qualifying_phase)
        if driver_laps.empty:
            continue

        valid_laps = _filter_valid_non_pit_laps(driver_laps)
        if valid_laps.empty:
            continue

        if lap_mode == "specific":
            if lap_number is None:
                continue
            laps_to_use = valid_laps[valid_laps["LapNumber"] == lap_number]
        elif lap_mode == "fastest":
            fastest = valid_laps.pick_fastest()
            if fastest is None or getattr(fastest, "empty", False):
                continue
            laps_to_use = pd.DataFrame([fastest])
        else:
            laps_to_use = valid_laps

        for _, lap in laps_to_use.iterrows():
            lap_time = lap.get("LapTime")
            if pd.isna(lap_time):
                continue
            compound = str(lap.get("Compound", "UNKNOWN"))
            if compound in ("nan", "None", "NaT", ""):
                compound = "UNKNOWN"
            rows.append({
                "Driver": driver,
                "LapTime": lap_time.total_seconds(),
                "Compound": compound.upper(),
                "LapNumber": int(lap.get("LapNumber")) if not pd.isna(lap.get("LapNumber")) else None,
                "SessionId": selected_qual_phase or qual_phase_lookup.get(lap.name, session_id),
            })

    if not rows:
        return pd.DataFrame(columns=["Driver", "LapTime", "Compound", "LapNumber", "SessionId"])
    return pd.DataFrame(rows)


def _get_session_id(session: fastf1.core.Session) -> str:
    """Best-effort short session identifier (e.g., FP1, Q, R)."""
    name = str(getattr(session, "name", "")).strip()
    reverse_map = {label: key for key, label in SESSION_TYPES.items()}
    if name in reverse_map:
        return reverse_map[name]
    return "Q" if name.lower() == "qualifying" else "SESSION"


def _get_qualifying_phase_lookup(session: fastf1.core.Session) -> dict:
    """Map lap index to qualifying phase for sessions with Q1/Q2/Q3 data."""
    lookup = {}
    split_laps = getattr(session.laps, "split_qualifying_sessions", lambda: [])()
    for phase, phase_laps in zip(("Q1", "Q2", "Q3"), split_laps):
        if phase_laps is None or phase_laps.empty:
            continue
        for idx in phase_laps.index:
            lookup[idx] = phase
    return lookup


def _filter_valid_non_pit_laps(laps):
    """Keep laps with a valid lap time that are not pit in/out laps."""
    if laps is None or laps.empty:
        return laps

    valid_laps = laps[laps["LapTime"].notna()]
    if valid_laps.empty:
        return valid_laps

    no_pit_in = valid_laps["PitInTime"].isna() if "PitInTime" in valid_laps.columns else pd.Series(True, index=valid_laps.index)
    no_pit_out = valid_laps["PitOutTime"].isna() if "PitOutTime" in valid_laps.columns else pd.Series(True, index=valid_laps.index)
    return valid_laps[no_pit_in & no_pit_out]


def _get_qualifying_phase_laps(session: fastf1.core.Session, phase: str):
    """Return laps object for a qualifying phase (Q1/Q2/Q3), or None."""
    if phase not in ("Q1", "Q2", "Q3"):
        return None

    try:
        split_method = getattr(session.laps, "split_qualifying_sessions", None)
        if split_method is None:
            return None
        split_laps = split_method()
        phase_index = {"Q1": 0, "Q2": 1, "Q3": 2}[phase]
        if phase_index >= len(split_laps):
            return None
        return split_laps[phase_index]
    except Exception:
        return None


def _filter_laps_by_qualifying_phase(
    session: fastf1.core.Session,
    laps,
    qualifying_phase: str,
):
    """Filter laps to a qualifying phase; return original laps on fallback."""
    if qualifying_phase not in ("Q1", "Q2", "Q3"):
        return laps

    phase_laps = _get_qualifying_phase_laps(session, qualifying_phase)
    if phase_laps is None:
        return laps
    if phase_laps.empty:
        return laps.iloc[0:0]

    try:
        return laps[laps.index.isin(phase_laps.index)]
    except Exception:
        return laps


def _format_timedelta(td) -> str:
    if pd.isna(td):
        return "-"
    total_seconds = td.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60
    if minutes > 0:
        return f"{minutes}:{seconds:06.3f}"
    return f"{seconds:.3f}"
