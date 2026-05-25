# 003 — VITS / StyleTTS2 are the TTS production bases

**Status:** accepted
**Date:** 2026-05-25

## Decision

Production TTS weights come from VITS (MIT) trained on our own data, with StyleTTS2 (MIT) as an upgrade path once data quality justifies it. MMS-TTS (Meta, CC-BY-NC) is benchmark-only.

## Rationale

- **License:** MIT — commercial-clean.
- **Single-speaker quality:** VITS produces strong single-speaker voices with ~10 hr of clean studio data. StyleTTS2 can do similar quality with less data but requires more careful training.
- **Mature ecosystem:** Coqui TTS reference impl, official paper repos, well-understood failure modes.

## Alternatives considered

| Model | Why deferred |
|---|---|
| MMS-TTS-urd | CC-BY-NC; benchmark only. |
| Coqui XTTS-v2 | License restrictions + no Urdu in supported list. |
| F5-TTS / E2-TTS | New flow-matching models, very high quality, but Urdu fine-tune unproven. Worth experimenting in Phase 4 — promote to ADR if it beats VITS. |
| Bark | MIT but Urdu quality unpredictable. Possible voice-cloning backup. |
| Tortoise | English-focused — skip. |

## Consequences

- Phase 4 priority: acquire ≥10 hr of single-speaker Pakistani-Urdu studio audio.
- TTS training loop will mirror STT loop architecture (see [orchestrator.md](../orchestrator.md)).
- Until we have a trained VITS, `suno-tts` defaults to MMS-TTS-urd with a banner warning that this is benchmark-only.

## Open questions

- Multi-speaker training: do we need it? Pakistani users probably want one canonical voice + a few alternatives. Decide after first VITS run.
- Voice cloning: out of scope until we have a stable base voice and a privacy/ethics policy.
