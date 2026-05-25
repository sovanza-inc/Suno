# Architectural Decisions

This directory holds locked architectural decisions. Each file is one ADR (Architecture Decision Record). They are immutable in spirit — revisit only with explicit reason, a PR, and a new ADR superseding the old.

## Index

- [001 — Open-source only for production weights](001-open-source-only.md)
- [002 — Whisper is the STT production base](002-whisper-for-stt.md)
- [003 — VITS / StyleTTS2 are the TTS production bases](003-vits-for-tts.md)
- [004 — Pakistani test set is the only ship-gate](004-pakistani-testset-only.md)
- [005 — Deterministic Python orchestrator, not Claude-in-a-loop](005-python-orchestrator-not-claude-loop.md)

## ADR template

```markdown
# NNN — <title>

**Status:** accepted | superseded by NNN | deprecated
**Date:** YYYY-MM-DD

## Context
The problem we faced and why a decision was needed.

## Decision
What we decided.

## Rationale
Why this and not alternatives.

## Consequences
What follows from this decision (good and bad).

## Alternatives considered
What we rejected and why.
```
