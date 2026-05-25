"""Persistent state for the orchestrator.

State is a JSON file written atomically (write to temp + rename) so crashes
mid-write don't corrupt it. The file format is intentionally flat and stable
so future Claude sessions can read it without any project knowledge.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from suno.paths import LOG_DIR, STATE_FILE


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError as e:
            log_error(f"state corrupted, starting fresh: {e}")
    return {
        "iteration": 0,
        "started_at": now_iso(),
        "last_iteration_at": None,
        "data_samples_curated": 0,
        "data_hours_curated": 0.0,
        "best_wer": None,
        "best_wer_iteration": None,
        "best_model_path": None,
        "last_trained_adapter": None,
        "last_wer": None,
        "eval_history": [],
        "phase_history": [],
    }


def save(state: dict) -> None:
    STATE_FILE.parent.mkdir(exist_ok=True, parents=True)
    tmp = STATE_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    tmp.replace(STATE_FILE)


def log_error(msg: str) -> None:
    LOG_DIR.mkdir(exist_ok=True, parents=True)
    with (LOG_DIR / "errors.log").open("a") as f:
        f.write(f"[{now_iso()}] {msg}\n")
