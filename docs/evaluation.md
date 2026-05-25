# Evaluation

## Primary metric

**WER (Word Error Rate)** on FLEURS ur_pk test split. Pakistani speakers, news-register, ~1 hr held-out. Normalization in [`src/suno/evaluation/metrics.py`](../src/suno/evaluation/metrics.py) — light: NFC + punctuation strip + whitespace collapse. Numerals and English-transliterated words are NOT stripped (they are signal for code-switching evaluation).

## Secondary metrics

- **CER (Character Error Rate)** — useful when WER spikes due to tokenization artifacts
- **Real-Time Factor (RTF)** — production deployment only (not yet wired)
- **MOS (Mean Opinion Score)** — TTS only (Phase 4)

## Eval datasets

| Dataset | Provenance | Use |
|---|---|---|
| FLEURS ur_pk test | Pakistani news read speech | **Primary ship-gate** |
| Common Voice 17 ur test | Mostly Indian Urdu | Secondary signal — not ship-gate per [decision 004](decisions/004-pakistani-testset-only.md) |
| Pakistani code-switching test | Hand-curated, planned | Future — see [roadmap.md](roadmap.md) |
| Internal recordings test | Phase 2 deliverable | Future ship-gate replacement |

## Running an eval

```bash
# Base whisper-small, no adapter, 50 samples
suno-eval --max-samples 50

# Adapter eval
suno-eval --adapter models/current_best --max-samples 200

# Different dataset/split
suno-eval --dataset google/fleurs --config ur_in --split test
```

## Reading loop eval history

`state["eval_history"]` keeps the last 100 evals. Quick view:

```bash
python -c "
import json
hist = json.load(open('state/orchestrator.json'))['eval_history']
for e in hist[-20:]:
    print(f\"iter {e['iter']:>4}  WER {e['wer']:.4f}\")
"
```

## Benchmark commitment

Every promoted model (new `current_best/`) gets a model card in [`docs/model-cards/`](model-cards/) with:
- training data sources + hours
- LoRA config
- WER + CER on FLEURS ur_pk test (and Common Voice ur test when available)
- example transcriptions with reference for spot-checking
- known failure modes
