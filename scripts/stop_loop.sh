#!/usr/bin/env bash
# Send SIGTERM to the running orchestrator. It finishes the current iteration then exits.
set -euo pipefail

if pgrep -fl "suno.orchestrator.loop" >/dev/null 2>&1; then
    pkill -TERM -f "suno.orchestrator.loop"
    echo "SIGTERM sent. Loop will exit after current iteration."
else
    echo "No orchestrator process found."
fi
