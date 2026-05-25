# Candidate Models

## STT (Speech-to-Text)

| Model | Size | Urdu support | License | Commercial | Notes |
|---|---|---|---|---|---|
| Whisper-large-v3 | 1.5B | Yes (multilingual) | MIT | ✅ | Best out-of-box Urdu; ~30% WER on FLEURS ur expected pre-tune |
| Whisper-medium | 769M | Yes | MIT | ✅ | Phase 3 fine-tune target; trains on single A100 |
| Whisper-small | 244M | Yes | MIT | ✅ | Fits CPU / edge deployment |
| Faster-Whisper (CTranslate2) | varies | inherits | MIT | ✅ | 4× faster inference, lower memory; same weights |
| MMS-ASR (`facebook/mms-1b-all`) | 1B | Yes | CC-BY-NC 4.0 | ❌ | **Benchmark only** — cannot ship without Meta agreement |
| XLS-R 300M / 1B | 300M / 1B | Yes via fine-tune | Apache 2.0 | ✅ | Strong base for CTC fine-tune; pre-Whisper alternative |
| SeamlessM4T v2 | 2.3B | Yes | CC-BY-NC 4.0 | ❌ | Same non-commercial constraint as MMS |
| NVIDIA Canary / Parakeet | varies | English-only currently | varies | varies | Watch for multilingual variants |

**Primary choice for Phase 3 fine-tune: Whisper-medium.** MIT, manageable size, multilingual prior gives Urdu a strong head start.

## TTS (Text-to-Speech)

| Model | Urdu support | License | Commercial | Notes |
|---|---|---|---|---|
| MMS-TTS-urd (`facebook/mms-tts-urd`) | ✅ direct | CC-BY-NC 4.0 | ❌ | Baseline for measuring quality; cannot ship |
| Coqui XTTS-v2 | ❌ (no Urdu) | Coqui PL | Restricted | Voice cloning, but locked language list |
| VITS / VITS2 (open impl) | Train from scratch | MIT | ✅ | Phase 4 primary target |
| StyleTTS2 | Train from scratch | MIT | ✅ | Higher quality than VITS; more complex training |
| Bark (Suno) | Some Urdu via prompts | MIT | ✅ | Worth experimenting; quality unpredictable |
| F5-TTS / E2-TTS | Multilingual via fine-tune | varies | check | New flow-matching models; strong English; viable Urdu fine-tune target |
| Tortoise | English-focused | Apache 2.0 | ✅ | Skip — multilingual quality not there |

**Primary choice for Phase 4 fine-tune: VITS** on cleaned single-speaker Urdu, with StyleTTS2 as upgrade once we have enough clean data.

## License substitution plan

Where a Meta CC-BY-NC model gives best zero-shot results, we use it for *benchmarking only*. Production weights must be retrained on Apache/MIT bases (XLS-R for STT, VITS for TTS). Any commercial deployment using MMS weights requires written agreement with Meta — assume that path is closed.

## Hardware requirements (single-language Urdu, fine-tuning)

| Stage | Model | GPU | Time | Approx cloud cost |
|---|---|---|---|---|
| Phase 1 eval | Whisper-large-v3 inference | 1× A100 40GB or 1× 4090 | ~6h on 20hr test | $5–15 |
| Phase 3 fine-tune (LoRA) | Whisper-medium on 100hr | 1× A100 80GB | ~3 days | $200–400 |
| Phase 3 fine-tune (full) | Whisper-medium on 500hr | 4× A100 80GB | ~5 days | $1500–3000 |
| Phase 4 TTS train | VITS from scratch on 20hr | 1× A100 40GB | ~5 days | $300–600 |
| Phase 4 TTS fine-tune | StyleTTS2 on 50hr | 2× A100 80GB | ~7 days | $1500 |

CPU/MPS (Apple Silicon) is fine for inference of small/medium Whisper and MMS-TTS, not for any training of consequence.
