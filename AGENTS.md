# AGENTS.md

Follows the [agents.md](https://agents.md/) convention. Any AI agent (Claude, GPT, autonomous worker, CI bot) operating in this repository should read this file first.

## Project

**Suno** — open-source speech AI (STT + TTS) for Urdu and other Pakistani languages. Mission: be the production-grade speech stack for Pakistan, owning the model weights and the data pipeline end-to-end.

## Quick orientation

| File | What it tells you |
|---|---|
| `README.md` | Public-facing overview |
| `docs/architecture.md` | How the pieces fit together |
| `docs/datasets.md` | Every Urdu speech dataset, license matrix |
| `docs/models.md` | STT/TTS model candidates, license matrix |
| `docs/hardware.md` | Why decisions look the way they do (M5 Pro 16 GB constraint) |
| `docs/orchestrator.md` | Autonomous loop architecture |
| `docs/decisions/` | Locked architectural decisions — change with PR + RFC |
| `PROGRESS.md` | Auto-updated journal of every loop iteration |
| `state/orchestrator.json` | Current state (best WER, iteration count) |
| `NEXT_TASK.md` | Loop's auto-generated suggestion for the next improvement |

## Conventions

- Python 3.11+
- `src/` layout: importable package is `suno`
- Tests: `pytest tests/`
- Lint: `ruff check`
- Style: standard ruff defaults, line length 100
- Commits: imperative mood, ≤72 char subject, body optional
- Branch names: `<type>/<short-slug>` e.g. `feat/pseudo-labeling-phase`

## Running things

After `pip install -e ".[dev]"`:

```
suno-loop                 # start the autonomous training loop
suno-stt <audio.wav>      # Whisper inference on one file
suno-tts "اردو متن"       # MMS-TTS inference (benchmark only, CC-BY-NC)
suno-eval                 # WER on FLEURS ur_pk test
suno-train ...            # standalone LoRA training
suno-plan                 # regenerate NEXT_TASK.md from current state
```

Or as a module:
```
python -m suno.orchestrator.loop
python -m suno.orchestrator.task_planner
```

## Critical rules

1. **Production-shipped weights = Apache/MIT only.** Meta's MMS / SeamlessM4T are CC-BY-NC; benchmark only, never ship.
2. **Pakistani test set is the only go/no-go.** Indian Urdu is transfer-learning material.
3. **Hardware: M5 Pro 16 GB**, design accordingly. No cloud assumptions.
4. **Pause the loop before refactoring.** `./scripts/stop_loop.sh`.

For Claude Code specifically, see `CLAUDE.md`.
