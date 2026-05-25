"""Self-iterating orchestrator for Suno speech AI.

Runs phases in sequence, persists state across crashes, sleeps between iterations.
Designed to run as a launchd-managed background process under caffeinate.

Architecture follows the "Pragmatic Loop" pattern from compass_artifact.md:
- Persistent JSON state machine with re-anchoring after every phase
- Each phase isolated; a phase crash does not abort the iteration
- Atomic state writes
- Signal-driven graceful shutdown

Environment variables:
  SUNO_LOOP_SLEEP        seconds to sleep between iterations (default 600)
  SUNO_LOOP_MAX_ITERS    safety cap per process invocation (default 100)
  SUNO_TRAIN_STEPS       LoRA training steps per iteration (default 200)
  SUNO_EVAL_SAMPLES      held-out test samples per eval (default 50)
  SUNO_FETCH_CV          set to "1" to also pull Common Voice ur
  SUNO_AUTO_PUSH         set to "1" to auto-`git push` after a new best WER
"""
from __future__ import annotations

import os
import signal
import time
import traceback

from suno.orchestrator import state as state_module
from suno.orchestrator.phases import (
    acquire,
    cleanup,
    curate,
    evaluate,
    journal,
    plan_next,
    promote,
    train,
)

PHASES = [
    ("acquire", acquire.run),
    ("curate", curate.run),
    ("train", train.run),
    ("evaluate", evaluate.run),
    ("promote", promote.run),
    ("cleanup", cleanup.run),
    ("journal", journal.run),
    ("plan_next", plan_next.run),
]

DEFAULT_SLEEP_SECONDS = 600
MAX_ITERATIONS_PER_RUN = 100


running = True


def _handle_sig(signum, frame):
    global running
    running = False
    print(f"\n[orchestrator] received signal {signum}; finishing current iteration then exiting", flush=True)


signal.signal(signal.SIGINT, _handle_sig)
signal.signal(signal.SIGTERM, _handle_sig)


def run_iteration(state: dict) -> dict:
    state["iteration"] += 1
    iter_n = state["iteration"]
    iter_start = time.time()
    iter_log = {"iteration": iter_n, "started_at": state_module.now_iso(), "phases": {}}
    print(f"\n{'=' * 60}\nIteration {iter_n} at {state_module.now_iso()}\n{'=' * 60}", flush=True)

    for name, fn in PHASES:
        if not running:
            break
        phase_start = time.time()
        print(f"\n[phase {name}] start", flush=True)
        try:
            state = fn(state)
            duration = time.time() - phase_start
            iter_log["phases"][name] = {"status": "ok", "duration_sec": round(duration, 1)}
            print(f"[phase {name}] ok ({duration:.1f}s)", flush=True)
        except Exception as e:
            tb = traceback.format_exc()
            state_module.log_error(f"iter {iter_n} phase {name}: {e}\n{tb}")
            iter_log["phases"][name] = {"status": "error", "error": str(e)}
            print(f"[phase {name}] FAILED: {e}", flush=True)
        finally:
            state["last_iteration_at"] = state_module.now_iso()
            state_module.save(state)

    iter_log["duration_sec"] = round(time.time() - iter_start, 1)
    state.setdefault("phase_history", []).append(iter_log)
    state["phase_history"] = state["phase_history"][-50:]
    state_module.save(state)
    return state


def main() -> None:
    print(f"[orchestrator] starting at {state_module.now_iso()}", flush=True)
    state = state_module.load()
    sleep_seconds = int(os.environ.get("SUNO_LOOP_SLEEP", DEFAULT_SLEEP_SECONDS))
    max_iters = int(os.environ.get("SUNO_LOOP_MAX_ITERS", MAX_ITERATIONS_PER_RUN))

    completed = 0
    while running and completed < max_iters:
        try:
            state = run_iteration(state)
        except Exception as e:
            state_module.log_error(f"orchestrator-level: {e}\n{traceback.format_exc()}")
            print(f"[orchestrator] error: {e}; cooling down 60s", flush=True)
            time.sleep(60)
            continue

        completed += 1
        if running and completed < max_iters:
            print(
                f"\n[orchestrator] iteration {state['iteration']} complete. Sleeping {sleep_seconds}s.",
                flush=True,
            )
            for _ in range(sleep_seconds):
                if not running:
                    break
                time.sleep(1)

    print(
        f"[orchestrator] exiting cleanly at {state_module.now_iso()} after {completed} iteration(s)",
        flush=True,
    )


if __name__ == "__main__":
    main()
