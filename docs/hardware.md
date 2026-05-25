# Hardware Reality

You have: M5 Pro, 16 GB unified memory. No cloud GPU.

## What this hardware CAN do

- ✅ Inference of Whisper-small/medium and (slowly) Whisper-large-v3
- ✅ LoRA fine-tuning of Whisper-small (244M params) on MPS — the autonomous loop's primary job
- ✅ Inference of MMS-TTS and small VITS
- ✅ Run the loop 24/7 with `caffeinate` + `launchd` auto-restart
- ✅ Build the *best Pakistani Urdu STT for code-switched conversational speech* — because no global vendor targets it

## What this hardware CAN'T do

- ❌ Full fine-tune of Whisper-large-v3 (needs an 80 GB GPU + days)
- ❌ Train StyleTTS2 from scratch in any reasonable wall-clock time
- ❌ Match Google/Azure on *general* multilingual WER (they have hundreds of GPUs)
- ❌ Process thousands of hours of training data per pass

## What "best in market" means here, honestly

You will not beat Google STT on overall WER for arbitrary Urdu by running on a 16 GB Mac. That's not physically possible. What you *can* beat them on:

1. **Pakistani Urdu accent + Pakistani named entities** — they train on Indian-dominant data
2. **Urdu ↔ English code-switching** — they treat this as edge case; we make it first-class
3. **Specific verticals** (banking, telecom, government) — fine-tuned on customer data they can't access
4. **On-device deployment** — small distilled models running offline in Pakistan
5. **Unit economics** — owning the weights makes per-minute pricing unbeatable

This is the realistic "best in market" play: be #1 in a niche that's invisible to global vendors, then expand.

## Realistic path without cloud

| Window | Goal | How |
|---|---|---|
| Now → 1 month | LoRA fine-tune Whisper-small on FLEURS + (opt) Common Voice via the loop | Loop runs nightly; iterates ~50–100 times; aim ≥15% relative WER improvement vs base |
| 1 → 3 months | Acquire 50–100 hr of internal Pakistani recordings | LUMS CSALT request + paid recording program |
| 3 → 6 months | Move to Whisper-medium LoRA (tight fit on 16 GB, doable) | Same loop, larger base |
| 6 → 12 months | One-time cloud rental ($2–4 k) for full Whisper-large-v3 fine-tune | By then your data moat is what matters, not the base model |
| TTS track (parallel) | Train VITS on cleaned single-speaker corpus | Patient: 2–3 weeks of loop time on Mac |

Don't wait on perfect compute. Ship iteration 1 with what you have; the loop compounds while you sleep.

## Thermal + battery notes (from `compass_artifact.md`)

- Keep Mac plugged in. Continuous training on battery = ~3hr life and accelerated battery degradation.
- Elevate for airflow. Sustained 90 °C+ kills lifespan.
- `caffeinate -i -m -s` (already in `scripts/run_loop.sh`) prevents idle/disk/system sleep on AC.
- Plan for one human checkpoint per week to verify the loop hasn't stalled (`tail PROGRESS.md`).
