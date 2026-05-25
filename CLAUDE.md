# CLAUDE.md — Instructions for Claude Code in this repo

You are working on **Suno**, Pakistan's commercial-grade open-source speech AI stack (STT + TTS) for Urdu and other Pakistani languages.

## Read these first, in this order

1. `PROGRESS.md` — what the autonomous loop did since last human contact
2. `state/orchestrator.json` — current best WER, iteration count, last error
3. `NEXT_TASK.md` — auto-generated task suggestion from the loop's task planner
4. `git log --oneline -20` — recent commits
5. `docs/decisions/` — immutable architecture decisions, only revisit with explicit reason

## Hard constraints (do not violate)

1. **Hardware budget:** M5 Pro 16 GB unified memory. No cloud GPU. See `docs/hardware.md`.
2. **License purity:** Production model weights must come from Apache/MIT bases only. Meta's MMS / SeamlessM4T are CC-BY-NC = benchmark-only, never ship.
3. **Pakistani data only counts for go/no-go:** Indian Urdu (FLEURS ur_in) is transfer-learning material. Ship decisions use Pakistani test sets only.
4. **Don't break the loop.** It's running. If you must change `src/suno/orchestrator/`, smoke-test with `SUNO_LOOP_MAX_ITERS=1` before pushing.

## Workflow protocol

### When you start a session

1. Read state files listed above.
2. If `NEXT_TASK.md` has a concrete task, default to it unless the user redirects.
3. If `logs/errors.log` has recurring entries, investigate before adding features.

### While working

- Tests: `pytest tests/` (must pass before commit)
- Lint: `ruff check src/ tests/`
- Smoke-test loop: `SUNO_LOOP_MAX_ITERS=1 SUNO_TRAIN_STEPS=5 SUNO_EVAL_SAMPLES=2 python -m suno.orchestrator.loop`

### When you finish a session

1. Update `CHANGELOG.md` under `## [Unreleased]` with what changed.
2. Update memory at `~/.claude/projects/-Users-faseehali-Desktop-Suno/memory/project_suno_next_steps.md`.
3. Commit (imperative mood, ≤72 chars subject) and push if user authorized.

## How to add improvements

| Want to add | Where it goes | Also update |
|---|---|---|
| New orchestrator phase | `src/suno/orchestrator/phases/<name>.py` + register in `loop.py` | `docs/orchestrator.md` |
| New dataset loader | `src/suno/data/acquisition.py` | `docs/datasets.md` (with license row) |
| New STT model | `src/suno/models/stt/<name>.py` | `docs/models.md` |
| New TTS model | `src/suno/models/tts/<name>.py` | `docs/models.md` |
| New eval metric | `src/suno/evaluation/metrics.py` | unit test in `tests/unit/` |
| Architectural decision | `docs/decisions/NNN-<slug>.md` | link from `docs/decisions/README.md` |

## What to avoid

- Cloud-dependent code paths without a CPU/MPS fallback flag.
- Writing to `state/orchestrator.json` from anywhere except the orchestrator itself.
- Dependencies without ARM64 macOS wheels (Apple Silicon).
- Skipping tests on commits that touch `src/suno/`.
- Adding documentation duplication — link to canonical files, don't restate.
- Aggressive refactors when the loop is running. Pause first: `./scripts/stop_loop.sh`.

## Self-improvement protocol

The loop generates `NEXT_TASK.md` based on observed trends:
- WER plateau → suggest enabling Common Voice
- Repeated train crashes → suggest reducing batch size or steps
- High CER but low WER → suggest tokenizer review
- No improvement after N iterations → suggest new model / new technique

When you finish a NEXT_TASK, the loop will regenerate it on its next iteration. Don't manually rewrite NEXT_TASK.md — let the planner do it.

## When in doubt

`PROGRESS.md` is history. `state/orchestrator.json` is present state. `NEXT_TASK.md` is the recommended future. Run `python -m suno.orchestrator.task_planner` to regenerate the next task if you suspect it's stale.
