<div align="center">

# Suno

**Pakistan's open-source speech AI stack — STT and TTS for Urdu and other Pakistani languages**

[![ci](https://github.com/sovanza-inc/Suno/actions/workflows/ci.yml/badge.svg)](https://github.com/sovanza-inc/Suno/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

</div>

---

Suno is an open-source effort to ship commercial-grade STT and TTS for Pakistani languages, starting with **Urdu**, expanding to Punjabi (Shahmukhi), Sindhi, Pashto, Saraiki, and Balochi.

## Why this exists

No production-grade speech AI today is optimized for **Pakistani** accents, Urdu/English code-switching, or local register. Google/Azure/AWS train on Indian-dominant data and mishandle Pakistani phonetics, place names, and conversational register. Suno's wedge is being #1 in a niche that's invisible to global vendors — then expanding.

## Key features

- **Open weights end-to-end** — Apache/MIT bases only. No CC-BY-NC weights ship.
- **Pakistani-first eval** — go/no-go decisions only against Pakistani test sets.
- **Autonomous training loop** — deterministic Python orchestrator trains and evaluates Whisper LoRA adapters continuously while you sleep. Runs on a 16 GB Mac via MPS.
- **Self-improving** — the loop's task planner writes `NEXT_TASK.md` after every iteration so the next session (human or AI) wakes up to a concrete to-do.

## Quickstart

```bash
git clone https://github.com/sovanza-inc/Suno.git
cd Suno
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# verify environment
make smoke

# start the autonomous loop (foreground, with caffeinate)
make loop

# install as a launchd service (auto-start on login, restart on crash)
make loop-install
```

## What's where

```
.
├── README.md, CLAUDE.md, AGENTS.md, LICENSE
├── pyproject.toml         installable package + CLI entry points
├── Makefile               common dev commands
├── PROGRESS.md            auto-updated journal (newest at bottom)
├── NEXT_TASK.md           auto-generated suggestion for the next session
├── src/suno/              the package
│   ├── data/              acquisition, curation, manifest
│   ├── models/stt/        Whisper inference + LoRA trainer
│   ├── models/tts/        MMS-TTS (benchmark) — VITS coming in Phase 4
│   ├── evaluation/        WER/CER + Urdu normalization
│   └── orchestrator/      the autonomous loop + 7 phases + task planner
├── docs/
│   ├── architecture.md, orchestrator.md, hardware.md, training.md, evaluation.md
│   ├── datasets.md        license matrix + Pakistani-speaker flag
│   ├── models.md          STT/TTS candidates + license matrix
│   ├── roadmap.md         phased plan
│   ├── decisions/         architectural decision records (ADRs)
│   └── model-cards/       release notes for each promoted model
├── tests/                 pytest unit tests
├── scripts/               start_loop.sh, stop_loop.sh, install_launchd.sh, ...
├── configs/languages/     per-language config (urdu.yaml)
├── launchd/               com.suno.orchestrator.plist for macOS autostart
├── .github/               CI workflows + issue/PR templates
├── data/, models/, logs/, outputs/, state/  (gitignored)
```

## CLI

After `pip install -e .`:

| Command | What it does |
|---|---|
| `suno-loop` | Start the autonomous training loop |
| `suno-stt <audio>` | Whisper inference on one audio file |
| `suno-tts <text>` | MMS-TTS synthesis (benchmark only — CC-BY-NC) |
| `suno-eval` | WER on a HF dataset (default FLEURS ur_pk) |
| `suno-train` | Standalone LoRA trainer |
| `suno-plan` | Regenerate `NEXT_TASK.md` from current state |

## How "best in market" works on local hardware

Realistically: we won't beat Google STT on overall Urdu WER while running on a single 16 GB Mac. We **can** beat them on:

1. Pakistani Urdu accent + named entities (they train on Indian-dominant data)
2. Urdu↔English code-switching (they treat it as edge case)
3. Vertical domains — banking, telecom, government — fine-tuned on customer data they can't access
4. On-device deployment (small distilled models offline in Pakistan)
5. Unit economics (owning weights collapses per-minute cost to compute)

See [`docs/hardware.md`](docs/hardware.md) for the full reality check and path to scale.

## Inspiration

[Shisa AI](https://github.com/shisa-ai) showed what a small focused team can do for Japanese LLMs — open releases, transparent eval, language-specific datasets. Suno aims to do the same for Pakistani speech AI.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). New work usually starts with the recommendation in `NEXT_TASK.md`.

## License

[Apache 2.0](LICENSE). Model weights produced by this repo are released under their own per-model licenses (typically Apache 2.0); see each model card in [`docs/model-cards/`](docs/model-cards/).
