#!/usr/bin/env bash
# Run on the VPS to deploy the latest f1-analytics code from GitHub.
# Usage: bash /opt/f1-analytics/deploy/server-deploy.sh [branch]
set -euo pipefail

APP_DIR="/opt/f1-analytics"
SERVICE="f1-analytics"
BRANCH="${1:-main}"

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "This script must run as root." >&2
  exit 1
fi

if [[ ! "$BRANCH" =~ ^[A-Za-z0-9._/-]+$ ]]; then
  echo "Invalid branch name: $BRANCH" >&2
  exit 1
fi

echo "→ Deploying f1-analytics branch: $BRANCH"
cd "$APP_DIR"

echo "→ Fetching latest code from GitHub..."
git fetch origin "$BRANCH"
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"

echo "→ Installing Python dependencies..."
python3 -m venv venv
venv/bin/pip install -q -r requirements.txt

echo "→ Ensuring cache directory permissions..."
mkdir -p data/cache
chown -R www-data:www-data data

echo "→ Updating systemd service..."
cp deploy/f1-analytics.service /etc/systemd/system/f1-analytics.service
systemctl daemon-reload
systemctl enable "$SERVICE" >/dev/null 2>&1 || true

echo "→ Restarting service..."
systemctl restart "$SERVICE"

echo "✓ VPS deploy complete"
