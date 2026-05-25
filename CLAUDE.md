# CLAUDE.md — Instructions for Claude Code in this repo

You are working on **Suno**, Pakistan's commercial-grade open-source speech AI stack (STT + TTS) for Urdu and other Pakistani languages.

This file serves two purposes:
1. **Interactive sessions** — protocol when a human is talking to you in this repo.
2. **Claude meta-loop** — when invoked by `scripts/claude_loop.sh`, you run autonomously through this protocol per iteration. See `## Loop protocol` below.

---

## Mission

Improve Suno over time by working through `TASKS.md`. The Python ML training loop trains models. *You* improve the code, tests, docs, and tooling that the ML loop depends on.

Every cycle:
1. Read `PROGRESS.md` (training loop history) and `NEXT_TASK.md` (planner suggestion).
2. Pick the first unchecked task in `TASKS.md` under `## Pending`.
3. Execute it. Run `make lint` + `make test`. Fix or revert if either fails.
4. Move the task to `## Done`. Commit with descriptive message.
5. If you learned something non-obvious, append a rule to `## Learned Rules` below.
6. Stop. The bash wrapper handles repetition.

---

## Hard Rules

- **NEVER** modify files outside `/Users/faseehali/Desktop/Suno`.
- **NEVER** touch `state/orchestrator.json` — the Python ML loop owns it.
- **NEVER** touch `data/`, `models/`, `logs/`, `outputs/` — runtime artifacts.
- **NEVER** `git push` or `git reset --hard` or `git checkout -- .`.
- **NEVER** run `rm -rf` against any path outside the repo.
- **NEVER** introduce CC-BY-NC weights into the production code path. See [`docs/decisions/001`](docs/decisions/001-open-source-only.md).
- **ALWAYS** run `make lint && make test` before committing.
- **ALWAYS** commit with the format `<task-slug>: <one-line summary>`.
- **ALWAYS** prefer editing existing files over creating new ones.
- **ALWAYS** keep `TASKS.md` consistent: tasks move from `## Pending` to `## Done`, never deleted.
- **ALWAYS** stop after one task in loop mode. Do not chain.

---

## Learned Rules

_The loop appends rules here when it learns from mistakes or successes. Keep total under 30 entries — consolidate similar ones._

_(empty — loop will populate)_

---

## Meta-Rule for Self-Improvement

When you make a mistake, hit a dead end, or learn something subtle, append ONE line under `## Learned Rules` in this format:
```
- **NEVER/ALWAYS [action]** — because [1-line reason]
```
Examples:
- **NEVER edit `state/orchestrator.json`** — because the Python loop holds an open file lock and atomic writes will collide.
- **ALWAYS run `make smoke` after touching `src/suno/orchestrator/`** — because import-only checks miss runtime errors.

If `## Learned Rules` exceeds 30 entries, consolidate similar rules into broader ones before adding the new one.

---

## Loop protocol (when invoked by `scripts/claude_loop.sh`)

The bash wrapper invokes `claude -p` once per iteration with the full instruction set. Inside that single invocation, you:

1. `cat PROGRESS.md | tail -30` — see what the ML loop has done
2. `cat NEXT_TASK.md` — see the planner's suggestion (may or may not be relevant)
3. `cat TASKS.md` — find the first `- [ ]` entry under `## Pending`
4. Execute it (Edit / Write / restricted Bash)
5. `make lint && make test` — must pass
6. Update `TASKS.md` (move to Done) and optionally `## Learned Rules` in this file
7. `git add -A && git commit -m "<slug>: <summary>" --no-verify`
8. Print one-line summary, exit

The `.claude/settings.json` hook (`guard.sh`) blocks dangerous Bash commands. If you hit it, that's the system telling you to take a different approach — don't try to bypass.

---

## Interactive session protocol (human-driven)

When a human starts a conversation here:

### Read state first, in this order

1. `PROGRESS.md` — what the ML training loop did since last contact
2. `state/orchestrator.json` — current best WER, iteration count
3. `NEXT_TASK.md` — training-loop planner's recommendation
4. `TASKS.md` — code-improvement queue
5. `git log --oneline -20` — recent commits (training + Claude loop)
6. `docs/decisions/` — immutable architecture decisions

### Hardware + license constraints (same as loop)

1. **Hardware:** M5 Pro 16 GB unified memory. No cloud. See [`docs/hardware.md`](docs/hardware.md).
2. **Production weights:** Apache/MIT only. Meta MMS / SeamlessM4T are CC-BY-NC = benchmark-only.
3. **Ship-gate:** Pakistani test set only. Indian Urdu is transfer-learning material.
4. **Don't break the loop.** Both the Python ML loop and the Claude loop are designed to keep running. Pause before refactor: `./scripts/stop_loop.sh` and `./scripts/claude_loop_stop.sh`.

### Adding improvements

| Want to add | Where it goes | Also update |
|---|---|---|
| New ML orchestrator phase | `src/suno/orchestrator/phases/<name>.py` + register in `loop.py` | `docs/orchestrator.md` |
| New code task | `TASKS.md` under `## Pending` | |
| New dataset loader | `src/suno/data/acquisition.py` | `docs/datasets.md` |
| New STT/TTS model | `src/suno/models/<stt\|tts>/<name>.py` | `docs/models.md` |
| New eval metric | `src/suno/evaluation/metrics.py` | unit test |
| Architectural decision | `docs/decisions/NNN-<slug>.md` | `docs/decisions/README.md` |
| Learned constraint | `## Learned Rules` above | |

### When finishing a session

1. Update `CHANGELOG.md` under `## [Unreleased]`.
2. Update memory at `~/.claude/projects/-Users-faseehali-Desktop-Suno/memory/project_suno_next_steps.md`.
3. Commit + push (user-authorized).

---

## What to avoid (both loops)

- Cloud-dependent paths without CPU/MPS fallback.
- Writing to `state/orchestrator.json` from outside the orchestrator.
- Dependencies without ARM64 macOS wheels (Apple Silicon).
- Skipping tests when touching `src/suno/`.
- Documentation duplication — link, don't restate.
- Aggressive refactors while loops are running.

## In doubt?

The Python loop is the source of training truth. `PROGRESS.md` is history. `state/orchestrator.json` is current state. `NEXT_TASK.md` is the planner's training suggestion. `TASKS.md` is the explicit code-improvement queue. Regenerate the planner output any time with `suno-plan`.
