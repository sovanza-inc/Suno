# 002 — Whisper is the STT production base

**Status:** accepted
**Date:** 2026-05-25

## Decision

Production STT weights come from OpenAI Whisper (MIT). We start with `whisper-small` for the autonomous loop's hardware envelope and move to `whisper-medium` when data + compute justify.

## Rationale

- **License:** MIT — clean for commercial deployment.
- **Multilingual prior:** Whisper already supports Urdu (`language="urdu"`) — we don't train from scratch, we adapt.
- **Tooling:** mature HF integration, PEFT support for LoRA, `faster-whisper` for production inference, well-documented quantization paths.
- **Hardware fit:** `whisper-small` (244 M params) trains on Apple Silicon MPS with 16 GB; `whisper-medium` (769 M) is tight but works.

## Alternatives considered

| Model | Why rejected (for now) |
|---|---|
| MMS-ASR (Meta) | CC-BY-NC; cannot ship. Benchmark only. |
| SeamlessM4T | Same as MMS. |
| XLS-R 300M / 1B | Apache 2.0 — viable backup but no multilingual decoder, CTC fine-tune is more brittle on small data than Whisper's seq2seq head. |
| NVIDIA Canary / Parakeet | English-only currently. Revisit when multilingual lands. |

## Consequences

- Inference path: `WhisperForConditionalGeneration` + `WhisperProcessor` with `forced_decoder_ids` for Urdu.
- Fine-tune path: PEFT LoRA on `q_proj`/`v_proj`, r=32 alpha=64 (see `src/suno/models/stt/whisper_lora_trainer.py`).
- Deployment path: faster-whisper (CTranslate2) for production inference, int8 quantization for edge.
- We will **not** ship benchmark numbers against MMS-ASR as our own — those are reference only.
