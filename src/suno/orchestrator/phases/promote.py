"""Phase 5: if the latest eval beat the previous best, copy to current_best."""
from __future__ import annotations

import shutil
from datetime import datetime, timezone

from suno.paths import BEST_MODEL_DIR, ROOT


def run(state: dict) -> dict:
    last_wer = state.get("last_wer")
    best_wer = state.get("best_wer")
    adapter_rel = state.get("last_trained_adapter")

    if last_wer is None or not adapter_rel:
        print("  no eval result, skipping promote")
        return state

    src = ROOT / adapter_rel
    if not src.exists():
        print(f"  adapter path missing: {src}")
        return state

    is_better = best_wer is None or last_wer < best_wer
    if is_better:
        if BEST_MODEL_DIR.exists():
            shutil.rmtree(BEST_MODEL_DIR)
        shutil.copytree(src, BEST_MODEL_DIR)
        state["best_wer"] = last_wer
        state["best_wer_iteration"] = state["iteration"]
        state["best_model_path"] = str(BEST_MODEL_DIR.relative_to(ROOT))
        state["best_model_updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        state["promoted_this_iteration"] = True
        prev = f"{best_wer:.4f}" if best_wer is not None else "none"
        print(f"  PROMOTED: {last_wer:.4f} (prev best: {prev})")
    else:
        state["promoted_this_iteration"] = False
        print(f"  not better: {last_wer:.4f} vs best {best_wer:.4f}; keeping current_best")
    return state
