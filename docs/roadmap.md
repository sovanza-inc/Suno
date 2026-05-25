# Roadmap

## Phase 0 — Bootstrap ✅ (this commit)

- [x] Project structure
- [x] Document datasets, models, licensing
- [x] Working Whisper STT baseline (inference)
- [x] Working MMS-TTS baseline (inference)
- [x] WER/CER evaluation harness on FLEURS

**Definition of done:** Anyone with a Python env can run inference end-to-end and reproduce baseline numbers.

## Phase 1 — Establish baselines (1–2 weeks)

- [ ] Run Whisper-large-v3 on FLEURS ur_pk test → record baseline WER
- [ ] Run Whisper-large-v3 on Common Voice ur test → record baseline WER
- [ ] Run Whisper-medium and Whisper-small on same → size/quality curve
- [ ] Compare against MMS-ASR (`facebook/mms-1b-all`) — for benchmarking only, never production
- [ ] Listen to MMS-TTS-urd on 20 sentences (news, conversational, religious, technical, code-switched)
- [ ] Identify systematic failure modes: numerals, English code-switching, Pakistani named entities, Punjabi-influenced Urdu

**Deliverable:** `benchmarks/phase1.md` with concrete WER/CER numbers and top 10 systematic errors.

## Phase 2 — Pakistani data acquisition (2–4 weeks)

Priorities:
- [ ] CSALT-LUMS Urdu corpus — formal request to LUMS Center for Speech and Language Technologies
- [ ] CSLU Urdu (LDC) — paid, ~$2k, ~5 hours read speech
- [ ] PRUS (Pakistan Research Urdu Speech) — academic license
- [ ] YouTube — Geo News, ARY, Dawn News bulletins (research-only until licensing cleared)
- [ ] **Internal recording program** — pay ~50 speakers across regions to record ~1hr each = 50hr clean speech with diversity guarantees

**Deliverable:** ≥100 hours of transcribed Pakistani-Urdu speech in `data/urdu_pk/` with manifest.json.

## Phase 3 — Fine-tune Urdu STT (2–3 weeks, GPU-bound)

- [ ] Fine-tune Whisper-medium on Pakistani-Urdu corpus (LoRA, ~3 GPU-days on A100)
- [ ] Beat baseline WER by ≥15% relative on Pakistani test set
- [ ] Build streaming wrapper (faster-whisper with VAD chunking)
- [ ] Quantize to int8 for CPU deployment

**Deliverable:** `models/suno-stt-urdu-v0.1` with model card, WER report, latency numbers.

## Phase 4 — Fine-tune Urdu TTS (2–3 weeks)

- [ ] Fine-tune VITS on cleaned single-speaker Pakistani Urdu (need ≥10hr studio-quality from one speaker)
- [ ] Or train StyleTTS2 if data quality permits
- [ ] MOS evaluation against MMS-TTS-urd baseline

**Deliverable:** `models/suno-tts-urdu-v0.1` with samples and MOS report.

## Phase 5 — Serving + product (3–4 weeks)

- [ ] FastAPI inference server with batched streaming
- [ ] gRPC for low-latency clients
- [ ] Dockerized deployment, GPU + CPU variants
- [ ] Web demo
- [ ] Pricing model + commercial license terms

## Phase 6 — Expand languages

Repeat Phase 2–4 for: Punjabi (Shahmukhi), Sindhi, Pashto, Saraiki, Balochi. Each language needs its own dataset acquisition and fine-tune cycle.

## Cross-cutting

- **Cost budget:** track GPU-hours and dataset costs in `BUDGET.md`
- **Legal:** every dataset and pretrained model has a row in `MODELS.md` / `DATASETS.md` with license, commercial usability, substitution plan
- **Eval:** WER+CER on held-out test sets, MOS on TTS, real-time-factor (RTF) on inference, monthly regression report
