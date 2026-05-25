# 005 — Deterministic Python orchestrator, not Claude-in-a-loop

**Status:** accepted
**Date:** 2026-05-25

## Context

The `compass_artifact.md` research (saved in [research/](../research/compass_artifact.md)) documents how to run Claude Code itself in a continuous autonomous loop. That works for open-ended coding tasks. For our ML training pipeline it's a poor fit:

- LLM-in-the-loop = token cost. Documented incidents: $30k overnight with 10 agents.
- OAuth expires every 1–4 hours.
- Probabilistic — same input can produce different action.
- Adds prompt-injection surface area.

ML training is deterministic. The work is: pull data, train N steps, eval, promote if better, repeat. None of it requires creative reasoning *during* the loop.

## Decision

The autonomous loop (`src/suno/orchestrator/loop.py`) is pure Python. Claude is invited back *between* iterations via `NEXT_TASK.md`, where the loop has summarized what just happened and what would help next. Claude reads the file, makes the change, commits, and goes away. The loop keeps running.

## Rationale

- **Zero ongoing cost.** Loop runs on local compute only.
- **Crash-recoverable.** Atomic state writes, subprocess-isolated phases, launchd auto-restart.
- **Inspectable.** `git log`, `PROGRESS.md`, `state/orchestrator.json` are the trail.
- **Self-improving.** `task_planner.py` watches WER trends and disk space and writes the next suggestion. Heuristics are simple Python — readable, debuggable, modifiable.

## Consequences

- "Self-improving" here means "improves the model" (loop trains, evals, promotes). Code-level improvements still require a human or Claude session.
- For autonomous *code* improvement, the user can use Claude Code's `/loop` skill to wake Claude at intervals and have it work on the `NEXT_TASK.md` content. That's a separate concern, off the critical path.
- We do not call the Anthropic API from the loop. If we ever need to (e.g. for auto-PR descriptions), that gets its own phase with budget caps.

## Alternatives considered

- **Claude API in the loop** to "decide" what to do each iteration → rejected on cost + reliability.
- **n8n / Airflow** workflow engine → rejected as overkill for a sequence of 7 phases on one machine.
- **No loop, manual runs** → rejected because the project benefit compounds with continuous runs while user sleeps.
