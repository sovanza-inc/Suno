#!/usr/bin/env bash
# Run the Suno autonomous loop with caffeinate so the Mac stays awake.
set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p logs

LOG="logs/loop.$(date +%Y%m%d-%H%M%S).log"

if [ -f .venv/bin/activate ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
fi

echo "Starting Suno loop. PID will write to logs/orchestrator.pid"
echo "Tail with:  tail -f $LOG"
echo "Stop with:  ./scripts/stop_loop.sh"
echo

# -i prevents idle sleep, -m prevents disk sleep, -s prevents system sleep on AC
exec caffeinate -i -m -s python -m suno.orchestrator.loop 2>&1 | tee "$LOG"
