# 006 — Claude-in-loop as a separate code-improvement layer

**Status:** accepted (amends [005](005-python-orchestrator-not-claude-loop.md))
**Date:** 2026-05-25

## Context

ADR-005 ruled out putting Claude inside the **ML training loop** — for that workload (data → train → eval → promote), an LLM in the loop is wasteful (cost, latency, OAuth expiry) since the work is fully deterministic.

But there's a second category of work the ML loop *cannot* do: writing new orchestrator phases, fixing code bugs, adding tests, updating documentation, drafting model cards. That work is open-ended and benefits from an LLM.

## Decision

Add a **second autonomous loop** (`scripts/claude_loop.sh`) that invokes `claude -p` per iteration to work through `TASKS.md`. It runs **alongside** the Python ML loop, never replacing it. ADR-005 stands for the ML loop; ADR-006 covers this second layer.

## Rationale

- Two loops, two layers, two cost profiles. Clear separation prevents the failure modes called out in ADR-005 (token cost in tight loops, OAuth churn, prompt-injection inside training).
- Loop 2's surface area is small: it edits code files, runs `make test` / `make lint`, commits. It never touches `state/orchestrator.json`, `data/`, `models/`, or pushes to remote.
- Safety is defense-in-depth: `.claude/guard.sh` PreToolUse hook + `acceptEdits` permission mode + `Hard Rules` in CLAUDE.md + a curated `TASKS.md` queue (no open-ended self-direction).

## Consequences

- Two scripts, two stop scripts, two Makefile targets, two log streams.
- Both loops read/write a small set of well-defined files (PROGRESS.md, NEXT_TASK.md, TASKS.md, CLAUDE.md). The interface is markdown — easy to inspect.
- Documentation: `docs/two-loops.md` describes the interaction model.
- Cost ceiling: Max plan caps usage at ~50–200 prompts/5h. With default `SUNO_CLAUDE_SLEEP=600s`, this is ~30 prompts/5h — well under the lower bound.

## Alternatives considered

- **Single combined loop (Claude wraps Python)**: rejected — couples a deterministic workload to a probabilistic one, and would burn tokens on ML phases that don't need an LLM.
- **No Claude loop, manual code work only**: rejected — user explicitly asked for self-iterating code improvement.
- **Claude API in a Python harness instead of `claude -p` CLI**: feasible alternative for the future; the CLI is faster to ship now. Worth re-evaluating if we need more programmatic control (parallel agents, custom tools).

## Off-by-default

The loop does not auto-start. Run it explicitly: `make claude-loop`. The ML loop (via launchd) runs autonomously; this one is human-triggered, because each iteration consumes tokens.
