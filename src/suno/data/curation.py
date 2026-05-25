"""Curate cached datasets into a unified manifest.

Reads HF dataset cache without decoding audio (Audio(decode=False)) — pure
metadata pass, very fast.
"""
from __future__ import annotations

from typing import Any

from suno.data.acquisition import available_datasets
from suno.data.manifest import write_manifest


def _fleurs_row_to_entry(row: dict, split: str, idx: int) -> dict | None:
    text = row.get("transcription") or row.get("raw_transcription") or ""
    if not text.strip():
        return None
    return {
        "id": f"fleurs_ur_pk_{split}_{idx}",
        "source": "fleurs_ur_pk",
        "path": row["audio"]["path"],
        "text": text,
        "num_samples": row.get("num_samples", 0),
        "sampling_rate": 16000,
        "split": "train" if split == "train" else "validation",
    }


def _common_voice_row_to_entry(row: dict, split: str, idx: int) -> dict | None:
    text = row.get("sentence") or ""
    if not text.strip():
        return None
    return {
        "id": f"cv_ur_{split}_{idx}",
        "source": "common_voice_ur",
        "path": row["audio"]["path"],
        "text": text,
        "split": "train" if split == "train" else "validation",
    }


_ROW_HANDLERS = {
    "fleurs_ur_pk": _fleurs_row_to_entry,
    "common_voice_ur": _common_voice_row_to_entry,
}


def build_manifest() -> tuple[int, float]:
    """Rebuild manifest.jsonl from cached datasets.

    Returns (n_entries, approx_hours).
    """
    from datasets import Audio

    entries: list[dict] = []
    total_samples_audio = 0

    for slug, meta in available_datasets().items():
        if not meta["always_fetch"]:
            continue
        handler = _ROW_HANDLERS.get(slug)
        if handler is None:
            continue
        # Only train + validation feed the manifest; test is held out for eval.
        for split in meta["splits"]:
            if split == "test":
                continue
            try:
                ds = meta["fetch"](split)
                ds = ds.cast_column("audio", Audio(decode=False))
                for i, row in enumerate(ds):
                    entry = handler(row, split, i)
                    if entry is None:
                        continue
                    entries.append(entry)
                    total_samples_audio += entry.get("num_samples", 0)
            except Exception as e:
                print(f"  curate {slug}/{split} skipped: {e}")

    write_manifest(entries)
    hours = total_samples_audio / 16000 / 3600 if total_samples_audio else 0.0
    return len(entries), round(hours, 2)


# Keep a typed alias for callers
ManifestStats = tuple[int, float]
_: Any = ManifestStats  # silence unused-import lint
