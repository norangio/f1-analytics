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


def get_lap_times_table(session: fastf1.core.Session) -> pd.DataFrame:
    """
    Return a DataFrame of fastest lap times + sector times per driver,
    sorted fastest to slowest.
    """
    rows = []
    for driver in get_drivers_in_session(session):
        driver_laps = session.laps.pick_driver(driver)
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
) -> dict[str, pd.DataFrame]:
    """
    Return telemetry DataFrames keyed by driver abbreviation.
    Each DataFrame has columns: Distance, Speed, Throttle, Brake.
    lap_mode: "fastest" | "specific"
    """
    result = {}
    for driver in drivers:
        driver_laps = session.laps.pick_driver(driver)
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


def get_sector_distances(session: fastf1.core.Session, driver: str) -> tuple[float | None, float | None]:
    """
    Return approximate (sector1_end_distance, sector2_end_distance) in meters
    for the fastest lap of a driver.
    """
    try:
        lap = session.laps.pick_driver(driver).pick_fastest()
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


def _format_timedelta(td) -> str:
    if pd.isna(td):
        return "-"
    total_seconds = td.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60
    if minutes > 0:
        return f"{minutes}:{seconds:06.3f}"
    return f"{seconds:.3f}"
