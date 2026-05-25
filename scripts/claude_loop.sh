#!/usr/bin/env bash
# Suno Claude meta-loop: iteratively invokes `claude -p` to work on TASKS.md.
#
# This is SEPARATE from the Python ML training loop (scripts/start_loop.sh).
# The Python loop trains models. This loop improves code.
#
# Each iteration:
#   1. Reads TASKS.md, picks first unchecked task
#   2. Asks Claude to execute it (acceptEdits mode, hook-protected)
#   3. Sleeps SUNO_CLAUDE_SLEEP (default 600s) — rate-limit friendly
#
# Stops on:
#   - all tasks complete
#   - max iterations reached
#   - SIGINT (Ctrl-C) or SIGTERM
#
# Environment:
#   SUNO_CLAUDE_SLEEP        seconds between iters (default 600 = 10min)
#   SUNO_CLAUDE_MAX_ITERS    safety cap per process (default 100)
#   SUNO_CLAUDE_MODEL        --model flag (default: unset, uses CLI default)
#   SUNO_CLAUDE_DRY_RUN      "1" prints the prompt without invoking claude

set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p logs

SLEEP="${SUNO_CLAUDE_SLEEP:-600}"
MAX_ITERS="${SUNO_CLAUDE_MAX_ITERS:-100}"
LOG="logs/claude_loop.$(date +%Y%m%d-%H%M%S).log"

trap 'echo "[claude-loop] received signal, exiting after current iter" >&2; exit 0' INT TERM

echo "Suno Claude loop starting at $(date)" | tee -a "$LOG"
echo "  log:        $LOG"
echo "  sleep:      ${SLEEP}s between iterations"
echo "  max iters:  $MAX_ITERS"
echo "  hook:       $(pwd)/.claude/guard.sh"
echo

if ! command -v claude >/dev/null 2>&1; then
    echo "ERROR: claude CLI not found. Install: npm install -g @anthropic-ai/claude-code" >&2
    exit 1
fi

# Reusable prompt — same every iteration. Claude's state lives in the files.
PROMPT='You are running in the Suno autonomous code-improvement loop. One iteration only.

PROTOCOL:
1. Run `cat PROGRESS.md | tail -30` to see what the training loop has been doing.
2. Run `cat NEXT_TASK.md` to see the training-loop planner'"'"'s suggestion.
3. Run `cat TASKS.md` and pick the FIRST unchecked task under "## Pending".
4. Execute that task. Use Edit/Write for code. Use Bash only via the make/git/python allowlist.
5. Before declaring done: run `make lint` and `make test`. If either fails, fix or revert with `git restore`.
6. When the task is complete and tests pass:
   - move it from "## Pending" to "## Done" in TASKS.md (mark `[x]`)
   - update CLAUDE.md "## Learned Rules" ONLY if you learned something non-obvious this cycle (1 line, format: NEVER/ALWAYS X — because Y)
   - `git add -A && git commit -m "<task slug>: <one-line summary>" --no-verify`
7. Print a one-line summary of what changed, then STOP.

Hard rules:
- Do not touch files outside /Users/faseehali/Desktop/Suno.
- Do not modify state/orchestrator.json (the Python loop owns it).
- Do not modify files under data/, models/, logs/, outputs/.
- Do not push to remote. Do not reset hard.
- If you cannot complete the task safely, leave it unchecked and write a short blocker note inline.

That is one full iteration. Do not loop. The bash wrapper handles repetition.'

ITER=0
while [ "$ITER" -lt "$MAX_ITERS" ]; do
    ITER=$((ITER + 1))
    echo "===== Iteration $ITER at $(date) =====" >> "$LOG"
    echo "[claude-loop] iteration $ITER"

    # Stop early if no pending tasks
    if ! grep -q "^- \[ \]" TASKS.md; then
        echo "[claude-loop] all tasks complete — exiting" | tee -a "$LOG"
        break
    fi

    if [ "${SUNO_CLAUDE_DRY_RUN:-0}" = "1" ]; then
        echo "DRY RUN — would invoke claude -p with prompt"
        echo "$PROMPT"
        break
    fi

    # Run one cycle. acceptEdits = auto-approve file edits, hook still blocks bad bash.
    set +e
    claude -p "$PROMPT" \
        --permission-mode acceptEdits \
        ${SUNO_CLAUDE_MODEL:+--model "$SUNO_CLAUDE_MODEL"} \
        >> "$LOG" 2>&1
    EXIT=$?
    set -e
    echo "Exit: $EXIT" >> "$LOG"

    if [ "$EXIT" -ne 0 ]; then
        echo "[claude-loop] iter $ITER non-zero exit ($EXIT); cooling 60s" | tee -a "$LOG"
        sleep 60
        continue
    fi

    echo "[claude-loop] iter $ITER done; sleeping ${SLEEP}s"
    sleep "$SLEEP"
done

echo "[claude-loop] exiting cleanly at $(date) after $ITER iteration(s)" | tee -a "$LOG"
