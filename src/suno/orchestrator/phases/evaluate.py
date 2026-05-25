"""Phase 4: evaluate the latest adapter on held-out FLEURS ur_pk test."""
from __future__ import annotations

import os
import subprocess
import sys

from suno.paths import LOG_DIR, ROOT


def run(state: dict) -> dict:
    iter_n = state["iteration"]
    adapter_rel = state.get("last_trained_adapter")
    if not adapter_rel:
        print("  no trained adapter yet, skipping eval")
        return state

    log_path = LOG_DIR / f"eval_iter{iter_n:04d}.log"
    max_samples = os.environ.get("SUNO_EVAL_SAMPLES", "50")
    cmd = [
        sys.executable, "-m", "suno.evaluation.stt",
        "--adapter", str(ROOT / adapter_rel),
        "--max-samples", max_samples,
    ]
    print(f"  log -> {log_path.relative_to(ROOT)}")
    with log_path.open("w") as f:
        result = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
    _ = result  # we parse the log file regardless of exit code

    wer_val = None
    cer_val = None
    if log_path.exists():
        for line in log_path.read_text().splitlines():
            if line.startswith("FINAL_WER"):
                try:
                    wer_val = float(line.split()[-1])
                except ValueError:
                    pass
            elif line.startswith("FINAL_CER"):
                try:
                    cer_val = float(line.split()[-1])
                except ValueError:
                    pass

    if wer_val is not None:
        state.setdefault("eval_history", []).append({
            "iter": iter_n, "wer": wer_val, "cer": cer_val, "adapter": adapter_rel,
        })
        state["eval_history"] = state["eval_history"][-100:]
        state["last_wer"] = wer_val
        state["last_cer"] = cer_val
        print(f"  WER = {wer_val:.4f}  CER = {cer_val if cer_val is not None else 'n/a'}")
    else:
        print(f"  WER could not be parsed; check {log_path.name}")
    return state
