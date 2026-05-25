"""Phase 1: acquire / verify labeled Urdu speech data via HuggingFace cache."""
from __future__ import annotations

from suno.data.acquisition import available_datasets


def run(state: dict) -> dict:
    acquired: list[dict] = []
    for slug, meta in available_datasets().items():
        if not meta["always_fetch"]:
            continue
        for split in meta["splits"]:
            try:
                ds = meta["fetch"](split)
                acquired.append({"dataset": slug, "split": split, "n": len(ds)})
            except Exception as e:
                print(f"  {slug}/{split} skipped: {e}")

    total = sum(a["n"] for a in acquired)
    state["acquire_last_run"] = {"acquired": acquired, "total_samples": total}
    print(f"  total samples available: {total} across {len(acquired)} dataset/split combos")
    return state
