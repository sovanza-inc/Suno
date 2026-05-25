"""Manifest is a JSONL file: one audio + transcription pair per line.

Schema (additive; new fields OK, never remove):
    id              str   — globally unique identifier
    source          str   — dataset slug, e.g. "fleurs_ur_pk"
    path            str   — absolute filesystem path to the audio file
    text            str   — reference transcription
    split           str   — "train" | "validation" | "test"
    num_samples     int   — audio length in samples (sampling_rate = 16000)
    sampling_rate   int   — 16000 by default
    speaker_id      str?  — when available
    region          str?  — karachi | lahore | islamabad | peshawar | quetta | rural | ...
    gender          str?  — "M" | "F" | "X"
    register        str?  — news | conversational | technical | religious | code-switched
"""
from __future__ import annotations

import json
from pathlib import Path

from suno.paths import MANIFEST_FILE


def read_manifest(path: Path | None = None) -> list[dict]:
    p = path or MANIFEST_FILE
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def write_manifest(entries: list[dict], path: Path | None = None) -> None:
    p = path or MANIFEST_FILE
    p.parent.mkdir(exist_ok=True, parents=True)
    with p.open("w") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")


def split_filter(entries: list[dict], split: str) -> list[dict]:
    return [e for e in entries if e.get("split") == split and e.get("text", "").strip()]
