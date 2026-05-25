# Getting started

## Prerequisites

- macOS or Linux
- Python 3.11+
- ~10 GB free disk (for FLEURS cache + iteration adapters)
- For Apple Silicon: ARM64 Python (`uname -m` should show `arm64`)

## Install

```bash
git clone https://github.com/sovanza-inc/Suno.git
cd Suno
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Or use the Makefile:
```bash
make install
```

## Verify

```bash
# Environment check (torch, MPS, transformers, etc.)
python scripts/01_check_env.py

# Smoke-test one loop iteration (~5 minutes on M5 Pro)
make smoke
```

A green smoke test means: data downloads work, manifest builds, training runs, eval emits `FINAL_WER`. If smoke fails, see `logs/train_iter0001.log` and `logs/errors.log`.

## First inference

```bash
# STT — Whisper on Urdu audio
suno-stt path/to/audio.wav --model openai/whisper-small

# TTS — synthesize Urdu (MMS, benchmark only — CC-BY-NC)
suno-tts "پاکستان زندہ باد" --out outputs/hello.wav

# Eval — baseline WER on FLEURS ur_pk
suno-eval --max-samples 20
```

## Start the autonomous loop

Foreground (visible logs):
```bash
make loop
# or:  ./scripts/start_loop.sh
```

Stop:
```bash
make stop
```

Auto-start at login + restart on crash:
```bash
make loop-install        # installs launchd plist
make loop-uninstall      # removes it
```

## What to read next

- [Architecture](architecture.md) — how phases compose
- [Orchestrator](orchestrator.md) — state machine + self-improvement
- [Hardware](hardware.md) — why settings look the way they do
