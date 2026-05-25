# Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  orchestrator.loop  ── state-machine, runs forever         │
│                                                             │
│  ┌────────┐  ┌────────┐  ┌──────┐  ┌────────┐  ┌─────────┐ │
│  │acquire │→ │curate  │→ │train │→ │evaluate│→ │promote  │ │
│  └────────┘  └────────┘  └──────┘  └────────┘  └─────────┘ │
│       ↓                                                     │
│  ┌─────────┐                                                │
│  │journal  │→ git commit + (opt) git push                  │
│  └─────────┘                                                │
│       ↓                                                     │
│  ┌──────────┐                                               │
│  │plan_next │→ writes NEXT_TASK.md                          │
│  └──────────┘                                               │
│                                                             │
│  state/orchestrator.json    ← atomic, crash-recoverable    │
│  PROGRESS.md                ← human-readable history       │
└─────────────────────────────────────────────────────────────┘
       │                            │
       ▼                            ▼
  src/suno/data/             src/suno/models/
    manifest.py              stt/whisper_inference.py
    acquisition.py           stt/whisper_lora_trainer.py
    curation.py              tts/mms_inference.py
                             
       │                            │
       ▼                            ▼
  data/                       models/
    hf_cache/                   whisper-small-lora-iter0001/
    manifest.jsonl              whisper-small-lora-iter0002/
                                current_best/  ← shipped pointer
```

## Package layout

```
src/suno/
├── paths.py            single source of truth for filesystem paths
├── device.py           CUDA > MPS > CPU picker
├── data/
│   ├── manifest.py     read/write JSONL manifest contract
│   ├── acquisition.py  HuggingFace dataset loaders + license registry
│   └── curation.py     manifest builder (metadata pass, no audio decode)
├── models/
│   ├── stt/
│   │   ├── whisper_inference.py     production inference CLI
│   │   └── whisper_lora_trainer.py  LoRA fine-tune (MPS-safe)
│   └── tts/
│       └── mms_inference.py         benchmark-only TTS
├── evaluation/
│   ├── metrics.py      WER/CER with Urdu normalization
│   └── stt.py          eval-on-dataset CLI (FINAL_WER stdout)
└── orchestrator/
    ├── loop.py         main self-iterating state machine
    ├── state.py        JSON persistence (atomic writes)
    ├── task_planner.py NEXT_TASK.md generator (the self-improvement brain)
    └── phases/
        ├── acquire.py
        ├── curate.py
        ├── train.py
        ├── evaluate.py
        ├── promote.py
        ├── journal.py
        └── plan_next.py
```

## Phase contract

Every phase is a module exposing `run(state: dict) -> dict`. The orchestrator:
- isolates each phase in its own try/except so one phase failing doesn't abort the iteration
- saves state atomically after every phase (file rename trick)
- skips remaining phases on SIGTERM but always saves before exiting

Side effects allowed inside phases: writing files, spawning subprocesses, calling git. Phases must NOT raise — they should swallow errors and record them in the returned state.

## Data contract

The orchestrator and trainers communicate exclusively through `data/manifest.jsonl`. Schema in [`src/suno/data/manifest.py`](../src/suno/data/manifest.py). Any new dataset loader must produce manifest entries with this shape.

## Model promotion

A trained adapter at `models/whisper-small-lora-iterNNNN/` is promoted to `models/current_best/` only if its WER on the held-out FLEURS ur_pk test split improves on the previous best. `current_best/` is what production code loads.

## Self-improvement loop

After every iteration, `phases/plan_next.py` calls `task_planner.plan(state)` which reads:
- recent WER trend (window=5)
- recent train log failure count
- disk space
- whether Common Voice is enabled

and writes a markdown recommendation to `NEXT_TASK.md`. A human or future Claude session picks this up at session start.

This is **not** an autonomous-Claude loop — it's a deterministic Python loop that recommends what a human/agent should work on next. No LLM tokens spent until a session opens.

See [orchestrator.md](orchestrator.md) for runtime details.
