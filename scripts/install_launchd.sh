#!/usr/bin/env bash
# Install the Suno orchestrator as a user-level launchd agent.
# After install: auto-starts at login, restarts on crash, survives reboots.
set -euo pipefail

PLIST_SRC="$(cd "$(dirname "$0")/.." && pwd)/launchd/com.suno.orchestrator.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.suno.orchestrator.plist"

if [ ! -f "$PLIST_SRC" ]; then
    echo "ERROR: plist source not found at $PLIST_SRC" >&2
    exit 1
fi

mkdir -p "$HOME/Library/LaunchAgents"
cp "$PLIST_SRC" "$PLIST_DST"

launchctl unload "$PLIST_DST" 2>/dev/null || true
launchctl load "$PLIST_DST"

echo "Installed to $PLIST_DST"
echo
echo "Status:"
launchctl list | grep com.suno.orchestrator || echo "  (not yet shown — give it 30s)"
echo
echo "Live logs:"
echo "  tail -f logs/launchd.out.log"
echo "  tail -f logs/launchd.err.log"
echo
echo "Uninstall: ./scripts/uninstall_launchd.sh"
