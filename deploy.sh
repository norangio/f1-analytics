#!/bin/bash
# Deploy f1-analytics to production.
# Usage: ./deploy.sh
set -e

SERVER="root@5.78.109.38"
REMOTE="/opt/f1-analytics"

echo "→ Syncing files..."
rsync -az --delete \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='data/cache/' \
  --exclude='.git' \
  . $SERVER:$REMOTE/

echo "→ Installing dependencies..."
ssh $SERVER "cd $REMOTE && python3 -m venv venv && venv/bin/pip install -q -r requirements.txt"

echo "→ Setting up cache directory..."
ssh $SERVER "mkdir -p $REMOTE/data/cache && chown -R www-data:www-data $REMOTE/data"

echo "→ Installing systemd service (first deploy only)..."
ssh $SERVER "cp $REMOTE/deploy/f1-analytics.service /etc/systemd/system/ && systemctl daemon-reload && systemctl enable f1-analytics" 2>/dev/null || true

echo "→ Restarting service..."
ssh $SERVER "systemctl restart f1-analytics"

echo "✓ Deployed to https://f1.norangio.dev"
