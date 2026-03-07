# F1 Analytics

Interactive F1 telemetry dashboard built with [FastF1](https://docs.fastf1.dev/) and [Plotly Dash](https://dash.plotly.com/). Compare speed, throttle, and brake traces across drivers for any session from 2021 to present.

Live at [f1.norangio.dev](https://f1.norangio.dev)

## Features

- **Session browser** — any race, qualifying, or practice session from 2021–2026
- **Telemetry charts** — speed, throttle, and brake traces per driver, synchronized on lap distance
- **Sector markers** — vertical bands showing S1/S2/S3 boundaries
- **Lap time sidebar** — fastest lap + sector times per driver, sorted fastest to slowest
- **Team colors** — driver pills and traces colored by team

## Stack

- [FastF1](https://docs.fastf1.dev/) — F1 data (telemetry, lap times, sector times)
- [Plotly Dash](https://dash.plotly.com/) — reactive web framework
- [Plotly.js](https://plotly.com/javascript/) — interactive charts

## Local Dev

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app.py
```

App runs at `http://localhost:8050`. FastF1 caches session data to `data/cache/` on first load.
