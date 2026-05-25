#!/usr/bin/env bash
set -euo pipefail
PLIST="$HOME/Library/LaunchAgents/com.suno.orchestrator.plist"
launchctl unload "$PLIST" 2>/dev/null || true
rm -f "$PLIST"
echo "Uninstalled. Existing orchestrator process (if any) is NOT killed."
echo "Run ./scripts/stop_loop.sh to stop a running instance."
