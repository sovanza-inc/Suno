"""Phase: housekeeping. Delete old iteration adapters to keep disk usable.

Each LoRA adapter is ~30-100 MB but with checkpoint metadata it can be 500 MB+.
Over 100 iterations that's 50 GB. We retain:
- `models/current_best/` (the shipped pointer)
- the N most recent iteration adapters (default 3) so we can rollback
- any directory whose name does NOT match `whisper-small-lora-iter*` (manual runs)
"""
from __future__ import annotations

import os
import re
import shutil

from suno.paths import BEST_MODEL_DIR, MODELS_DIR

ITER_DIR_PATTERN = re.compile(r"^whisper-(?:small|medium|tiny|large-v3)-lora-iter(\d+)$")
DEFAULT_KEEP = 3


def run(state: dict) -> dict:
    keep = int(os.environ.get("SUNO_KEEP_ITERATIONS", DEFAULT_KEEP))
    if not MODELS_DIR.exists():
        return state

    candidates: list[tuple[int, object]] = []
    for child in MODELS_DIR.iterdir():
        if not child.is_dir():
            continue
        if child == BEST_MODEL_DIR:
            continue
        m = ITER_DIR_PATTERN.match(child.name)
        if not m:
            continue
        candidates.append((int(m.group(1)), child))

    if len(candidates) <= keep:
        print(f"  {len(candidates)} iter adapters, under limit ({keep}) — keeping all")
        return state

    candidates.sort(key=lambda t: t[0])
    to_delete = candidates[: -keep]
    freed_mb = 0.0
    for _, path in to_delete:
        try:
            size = sum(p.stat().st_size for p in path.rglob("*") if p.is_file())
            shutil.rmtree(path)
            freed_mb += size / (1024 * 1024)
            print(f"  deleted {path.name}")
        except Exception as e:
            print(f"  cleanup of {path.name} failed: {e}")

    state["last_cleanup"] = {
        "deleted": len(to_delete),
        "kept": keep,
        "freed_mb": round(freed_mb, 1),
    }
    print(f"  freed {freed_mb:.1f} MB across {len(to_delete)} adapter(s)")
    return state
