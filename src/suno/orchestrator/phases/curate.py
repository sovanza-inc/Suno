"""Phase 2: rebuild the unified manifest from cached datasets."""
from __future__ import annotations

from suno.data.curation import build_manifest


def run(state: dict) -> dict:
    n, hours = build_manifest()
    state["data_samples_curated"] = n
    state["data_hours_curated"] = hours
    print(f"  manifest: {n} samples (~{hours}h FLEURS audio counted)")
    return state
