# Suno Documentation

Open-source speech AI (STT + TTS) for Urdu and other Pakistani languages.

## Start here

- [Getting started](getting-started.md) — install, smoke-test, first inference
- [Architecture](architecture.md) — how the pieces fit together
- [Orchestrator](orchestrator.md) — the Python ML training loop
- [Two loops](two-loops.md) — Python ML loop + Claude code-improvement loop, side by side
- [Hardware reality](hardware.md) — what 16 GB local can and can't do

## Reference

- [Datasets](datasets.md) — every Urdu speech corpus, license matrix, Pakistani-speaker flag
- [Models](models.md) — STT/TTS candidates, license matrix, hardware requirements
- [Roadmap](roadmap.md) — phased plan from bootstrap to production serving

## Decisions

Locked architectural decisions are in [decisions/](decisions/). These are immutable unless explicitly revisited with a PR + rationale.

## Model cards

When the loop produces a promotable checkpoint, its evaluation report and provenance live in [model-cards/](model-cards/).

## Research notes

- [Compass artifact](research/compass_artifact.md) — research on running Claude Code continuously; methodology for our autonomous loop pattern

## For AI agents

- `CLAUDE.md` (repo root) — Claude Code session protocol
- `AGENTS.md` (repo root) — generic AI agent instructions
