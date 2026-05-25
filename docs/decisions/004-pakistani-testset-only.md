# 004 — Pakistani test set is the only ship-gate

**Status:** accepted
**Date:** 2026-05-25

## Decision

Ship/no-ship decisions for production models are made against test sets recorded by Pakistani speakers. Indian-Urdu test sets (FLEURS ur_in, Shrutilipi Urdu) are transfer-learning material only — never go/no-go gates.

## Rationale

The Pakistani Urdu accent, vocabulary, and code-switching patterns diverge meaningfully from Indian Urdu / Hindi-Urdu. A model that scores 15% WER on Indian Urdu but 35% on Pakistani Urdu fails our customers. Google / Azure / AWS train on Indian-dominant data and have this exact failure mode — beating them on Pakistani test sets is our wedge.

## Consequences

- FLEURS ur_pk test is the current primary eval. Common Voice ur test is a noisier secondary.
- Phase 2 explicitly funds a 50-speaker × 1 hr internal recording program to create a high-quality, accent-balanced Pakistani test set (~50 hr).
- A locked, never-trained-on Pakistani test split is mandatory before any commercial deployment.
- "Beats Google on average" is meaningless if it underperforms on Pakistani audio. Use targeted slices.

## How this shows up in code

- `src/suno/evaluation/stt.py` defaults to `dataset_config="ur_pk"`.
- Train splits explicitly exclude `*_test_*` entries via manifest `split` field.
- Reports in `benchmarks/` must specify Pakistani vs. Indian provenance.
