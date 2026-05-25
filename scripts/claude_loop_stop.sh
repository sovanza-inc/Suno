#!/usr/bin/env bash
# Send SIGTERM to the Suno Claude loop. Current iteration finishes; loop exits.
set -euo pipefail

if pgrep -fl "scripts/claude_loop.sh" >/dev/null 2>&1; then
    pkill -TERM -f "scripts/claude_loop.sh"
    echo "SIGTERM sent to Claude loop."
else
    echo "No Claude loop process found."
fi
