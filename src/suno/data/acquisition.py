"""Dataset acquisition via HuggingFace `datasets` library.

Idempotent: HF caches locally on first call, fast on subsequent calls.

Currently wired:
- google/fleurs (ur_pk) — CC-BY 4.0, Pakistani speakers, ~12 hr
- mozilla-foundation/common_voice_17_0 (ur) — CC0, mixed (mostly Indian), ~80 hr

Add new sources here, then expose them via `available_datasets()`.
"""
from __future__ import annotations

import os
from typing import Any

from suno.paths import DATA_DIR

CACHE_DIR = str(DATA_DIR / "hf_cache")


def fetch_fleurs_ur_pk(split: str) -> Any:
    from datasets import load_dataset

    return load_dataset("google/fleurs", "ur_pk", split=split, cache_dir=CACHE_DIR)


def fetch_common_voice_ur(split: str) -> Any:
    from datasets import load_dataset

    return load_dataset(
        "mozilla-foundation/common_voice_17_0",
        "ur",
        split=split,
        cache_dir=CACHE_DIR,
    )


def available_datasets() -> dict[str, dict]:
    """Returns a dict of dataset_slug -> metadata.

    Used by the orchestrator's acquire phase to know what to pull.
    """
    return {
        "fleurs_ur_pk": {
            "fetch": fetch_fleurs_ur_pk,
            "splits": ("train", "validation", "test"),
            "license": "CC-BY-4.0",
            "commercial_ok": True,
            "always_fetch": True,
        },
        "common_voice_ur": {
            "fetch": fetch_common_voice_ur,
            "splits": ("train", "test"),
            "license": "CC0",
            "commercial_ok": True,
            "always_fetch": os.environ.get("SUNO_FETCH_CV") == "1",
        },
    }
