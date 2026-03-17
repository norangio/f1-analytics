# F1 Analytics — CLAUDE.md

## Project Overview
A Plotly Dash app serving real F1 telemetry data via the FastF1 Python SDK. Deployed at `f1.norangio.dev` on a Hetzner VPS alongside other norangio.dev apps.

## Stack
- **Framework**: Plotly Dash (gunicorn, port 8003)
- **Data**: FastF1 (disk-cached in `data/cache/`, gitignored)
- **Styling**: Neutral light theme (white/gray surfaces with muted slate text)
- **Deployment**: GitHub pull on VPS via `./deploy.sh` + `deploy/server-deploy.sh`

## Project Structure
```
app.py                    # Entry point — imports from dash_app.py, mounts layout + callbacks
dash_app.py               # Dash instance (singleton to avoid circular imports)
layout.py                 # Top-level HTML layout
callbacks/
  session_callbacks.py    # Populates year/race/session/lap controls + driver checklist
  chart_callbacks.py      # Renders telemetry charts (lap mode + qualifying phase)
  sidebar_callbacks.py    # Renders lap time + sector sidebar table (phase-aware for qualifying)
  laptime_callbacks.py    # Renders lap-time boxplot tab + compound summary table
components/
  session_selector.py     # Dropdown controls (year, race, session, qualifying phase, lap mode)
  driver_selector.py      # Driver pill checklist
  telemetry_charts.py     # Plotly figure builders (3-subplot, shared x-axis)
  lap_sidebar.py          # Lap time table component
  laptime_boxplot.py      # Lap-time boxplot with tire compound markers
  laptime_summary_table.py  # Driver+compound quartiles (q25/median/q75) for selected data
utils/
  f1_data.py              # FastF1 loading helpers, telemetry + lap time extraction
  colors.py               # Team → color mapping, driver → team mapping
assets/style.css          # Global CSS overrides (Dash dropdowns, pills, scrollbar)
deploy/
  f1-analytics.service    # systemd unit
  Caddyfile.snippet        # Caddy reverse proxy block
  server-deploy.sh         # Runs on VPS: git pull + pip install + restart
deploy.sh                 # One-command deploy script
```

## Key Architecture Notes

### Circular Import Prevention
The Dash app instance lives in `dash_app.py` only. `app.py` imports from it, and all callbacks import from `dash_app` — never from `app.py`.

### FastF1 Data Model (Important)
- `session.drivers` returns a **frozenset of car number strings** (e.g. `{'11', '44', '63'}`), NOT abbreviations
- Always use `session.results["Abbreviation"]` and `session.results["DriverNumber"]` to get driver abbreviations and numbers
- `get_drivers_in_session()` and `get_driver_numbers()` in `utils/f1_data.py` handle this correctly

### Driver Colors
Colors are team-based, keyed by 3-letter abbreviation. See `utils/colors.py`. The `DRIVER_TEAM` dict covers 2025 + 2026 grid plus legacy drivers.

Current custom mappings include:
- `BOT`/`PER` → Cadillac (`#000000`)
- `BOR`/`HUL` → Audi (`#6E6E6E`)
- `LAW`/`LIN` → Racing Bulls (with Lawson blue override)
- Alpine (`GAS`/`COL`) uses a darker blue (`#2456B3`)

When two selected drivers share the same team, one trace is rendered dotted so same-color teammates remain distinguishable.

### Qualifying Views
When session type is `Q`, the UI exposes a qualifying phase dropdown (`All`, `Q1`, `Q2`, `Q3`).
Telemetry, lap-number options, the right-hand lap-time sidebar, and Lap Times tab outputs are filtered to the selected phase.

### Lap Times Tab
- Boxplot chart uses all valid laps for selected drivers (excluding pit in/out laps) with compound markers and explicit median dots.
- Summary table under the chart is computed from the exact same filtered lap set and reports per-driver/per-compound `Laps`, `q25`, `median`, and `q75`, ordered by the same driver sequence as the boxplot.

### Telemetry Performance
- `utils/f1_data.load_session()` is memoized in-process, so repeated driver/lap selections reuse the already loaded FastF1 session.
- Telemetry charts use `lap.get_car_data().add_distance()` because the UI only needs `Distance`, `Speed`, `Throttle`, and `Brake`; avoid `get_telemetry()` unless merged channels are actually required.

### Driver Pills
Selected driver pills are rendered as a darker fill with white text, without an extra outer box.
`Select All` and `Clear` buttons are stateful and highlight when all or none are selected.

## Deployment
```bash
./deploy.sh   # push branch → SSH to VPS → git pull + pip install + restart
```
- Server: `root@5.78.109.38`, app lives at `/opt/f1-analytics`
- Service port: 8003
- Caddy handles TLS and reverse proxy for `f1.norangio.dev`
- GitHub Actions auto-deploy: `.github/workflows/deploy.yml` on push to `main`
- Required GitHub secrets: `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`
- The workflow bootstraps/syncs `/opt/f1-analytics` from GitHub before deployment

## Supported Years
`SUPPORTED_YEARS = list(range(2021, 2027))` — update upper bound each new season.

## Local Dev
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app.py   # runs on http://localhost:8050
```
FastF1 caches session data to `data/cache/` on first load, and the app reuses loaded sessions in-process for fast chart updates.
