# Changelog

All notable changes to this project will be documented in this file.

Format inspired by [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [SemVer](https://semver.org/).

## [Unreleased]

### Added
- `phases/cleanup.py` — deletes old iteration adapters to prevent disk fill (keeps `current_best/` + last 3 by default; tunable via `SUNO_KEEP_ITERATIONS`)
- `scripts/show_progress.py` — terminal sparkline + WER history view (`make status`)
- Enterprise `src/suno/` package layout with proper pyproject.toml + CLI entry points (`suno-loop`, `suno-stt`, `suno-tts`, `suno-eval`, `suno-train`, `suno-plan`)
- `CLAUDE.md` and `AGENTS.md` — protocol files for AI agents working in this repo
- `docs/` folder with architecture, orchestrator, training, evaluation, deployment, and hardware docs
- `docs/decisions/` with 5 initial ADRs documenting open-source-only, Whisper-base, VITS-base, Pakistani-test-set-only, and Python-orchestrator decisions
- Task planner — auto-generates `NEXT_TASK.md` based on observed WER trends, train failures, and disk usage
- Unit tests: `tests/unit/test_manifest.py`, `tests/unit/test_metrics.py`, `tests/unit/test_task_planner.py`
- GitHub Actions CI workflow (lint + tests)
- Issue templates (bug, feature) and PR template
- `LICENSE` (Apache 2.0), `CONTRIBUTING.md`, `Makefile`

### Changed
- Renamed `scripts/run_loop.sh` → `scripts/start_loop.sh` (matches `make loop` convention)
- launchd plist updated to call `start_loop.sh` and run via `python -m suno.orchestrator.loop`
- Moved `DATASETS.md`, `MODELS.md`, `ROADMAP.md`, `HARDWARE_REALITY.md` into `docs/`
- Moved `compass_artifact.md` into `docs/research/`
- Moved `configs/urdu.yaml` → `configs/languages/urdu.yaml`

### Removed
- Top-level `phases/` directory (moved into `src/suno/orchestrator/phases/`)
- Per-task standalone scripts (`scripts/02_download_urdu_data.py` through `scripts/08_eval_lora.py`) — superseded by the `suno-*` CLI entry points

## [0.1.0] — 2026-05-25

### Added
- Initial Phase 0 scaffold
- Whisper STT + MMS TTS inference scripts
- WER/CER evaluation harness
- Autonomous training loop (`orchestrator.py` + phases)
- launchd plist for macOS auto-start
- Documentation: README, ROADMAP, DATASETS, MODELS, HARDWARE_REALITY
