# F1 Analytics

Interactive F1 telemetry dashboard built with [FastF1](https://docs.fastf1.dev/) and [Plotly Dash](https://dash.plotly.com/). Compare speed, throttle, and brake traces across drivers for any session from 2021 to present.

Live at [f1.norangio.dev](https://f1.norangio.dev)

## Features

- **Session browser** — any race, qualifying, or practice session from 2021–2026
- **Qualifying phase filter** — for qualifying sessions, compare All laps or only Q1/Q2/Q3
- **Lap selection** — compare either each driver's fastest lap (default) or a specific lap number from the selected session
- **Telemetry charts** — speed, throttle, and brake traces per driver, synchronized on lap distance
- **Sector markers** — vertical bands showing S1/S2/S3 boundaries
- **Lap time sidebar** — fastest lap + sector times per driver, sorted fastest to slowest and filtered by qualifying phase when applicable
- **Team colors + teammate styling** — traces are team-colored, and when both teammates are selected one trace renders dotted for clarity
- **Driver pill styling** — selected drivers use a darker filled pill with white text and no extra outer box
- **Driver action states** — `Select All` and `Clear` buttons visibly show active state based on current selection

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

## Deployment

Deploys now use GitHub as the source of truth (no rsync from local machine).

```bash
# Push current branch to GitHub, then deploy that branch on VPS
./deploy.sh

# Deploy a specific branch
./deploy.sh main

# Skip local push (useful in CI/CD where code is already on GitHub)
SKIP_PUSH=1 ./deploy.sh main
```

`./deploy.sh` SSHes to the server and runs:

```bash
bash /opt/f1-analytics/deploy/server-deploy.sh main
```

The server script does:
- `git fetch/pull` from GitHub
- `venv` + `pip install -r requirements.txt`
- `systemctl restart f1-analytics`

### GitHub Actions Auto Deploy

`.github/workflows/deploy.yml` deploys automatically on pushes to `main` (and supports manual runs).
It bootstraps/syncs `/opt/f1-analytics` from GitHub before running the server deploy script.

Required repository secrets:
- `VPS_HOST` (example: `5.78.109.38`)
- `VPS_USER` (example: `root`)
- `VPS_SSH_KEY` (private key content used by Actions)

One-time key setup:
```bash
# local machine
ssh-keygen -t ed25519 -f ~/.ssh/github-actions-hetzner -C "github-actions-deploy"

# server
cat ~/.ssh/github-actions-hetzner.pub | ssh root@5.78.109.38 'cat >> /root/.ssh/authorized_keys'
```
Then paste `~/.ssh/github-actions-hetzner` (private key) into the `VPS_SSH_KEY` secret.
