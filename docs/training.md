# Training

## STT — Whisper LoRA fine-tune

The autonomous loop calls `python -m suno.models.stt.whisper_lora_trainer` once per iteration. You can also run it standalone:

```bash
suno-train \
  --base-model openai/whisper-small \
  --manifest data/manifest.jsonl \
  --out-dir models/manual-run \
  --max-steps 500
```

### Defaults (tuned for M5 Pro 16 GB / MPS)

| Setting | Value | Why |
|---|---|---|
| Base model | `openai/whisper-small` (244M) | Fits MPS comfortably |
| LoRA target | `q_proj`, `v_proj` | Sweet spot for attention adaptation |
| LoRA r / alpha | 32 / 64 | Standard mid-range capacity |
| LoRA dropout | 0.05 | |
| Batch size | 1 | Audio inputs are large |
| Grad accum | 8 | Effective batch 8 |
| LR | 1e-4 | Conservative for LoRA |
| Warmup | min(20, steps/10) | |
| Precision | fp32 | MPS still has correctness issues with bf16/fp16 |

### Resuming

If `--resume-from PATH` is passed and the path exists, the trainer loads the existing PEFT adapter and continues training. The orchestrator passes `state["last_trained_adapter"]` automatically.

### Scaling up

When data + compute allow:

1. Move base to `openai/whisper-medium` — set `SUNO_BASE_MODEL=openai/whisper-medium` in the launchd plist. Watch memory.
2. Increase `r` to 64 once dataset > 50 hr.
3. Replace LoRA with full fine-tune once dataset > 500 hr (will need cloud).

## TTS — VITS / StyleTTS2 (planned, Phase 4)

Not yet implemented. The plan:

1. Acquire ≥10 hr of single-speaker, studio-quality, transcript-clean Pakistani-Urdu audio.
2. Build a mirror of the STT loop with phases: acquire → curate → train_vits → eval_mos → promote → journal.
3. Initial training run from VITS reference impl (Coqui or original repo) for ~5 days on Mac.
4. Compare MOS subjectively against MMS-TTS-urd baseline.

See [decisions/003-vits-for-tts.md](decisions/003-vits-for-tts.md) for the model choice rationale.

## Evaluation during training

The loop's `evaluate` phase runs after every `train` phase, so each iteration produces a WER number against the held-out FLEURS ur_pk test split. Plot the trajectory:

```bash
python -c "
import json, pathlib
state = json.loads(pathlib.Path('state/orchestrator.json').read_text())
for e in state.get('eval_history', []):
    print(f\"iter {e['iter']:>4}  WER {e['wer']:.4f}\")
"
```
