#!/usr/bin/env bash
# One-time setup: registers and starts the context watcher as a systemd user service.
# Run once: bash scripts/setup_watcher_service.sh

set -e
PROJ="/home/zapostolski/projects/ananas-ai"
ENV_FILE="$PROJ/.env"

echo ""
echo "=== Ananas context watcher — service setup ==="
echo ""

# 1. Create .env if it doesn't exist
if [ ! -f "$ENV_FILE" ]; then
    echo "[1/4] Creating .env from .env.example..."
    cp "$PROJ/.env.example" "$ENV_FILE"
    echo "      .env created. Fill in ANTHROPIC_API_KEY before the service will work:"
    echo "      nano $ENV_FILE"
    echo ""
else
    echo "[1/4] .env already exists — skipping."
fi

# 2. Reload systemd user daemon
echo "[2/4] Reloading systemd user daemon..."
systemctl --user daemon-reload

# 3. Enable (auto-start on login) and start now
echo "[3/4] Enabling and starting ananas-context-watcher..."
systemctl --user enable ananas-context-watcher.service
systemctl --user start ananas-context-watcher.service

# 4. Status check
echo ""
echo "[4/4] Service status:"
systemctl --user status ananas-context-watcher.service --no-pager -l
echo ""
echo "=== Done ==="
echo ""
echo "Useful commands:"
echo "  View live logs:    journalctl --user -u ananas-context-watcher -f"
echo "  Stop watcher:      systemctl --user stop ananas-context-watcher"
echo "  Restart watcher:   systemctl --user restart ananas-context-watcher"
echo "  Disable on boot:   systemctl --user disable ananas-context-watcher"
