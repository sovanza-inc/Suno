"""Phase 3: LoRA fine-tune a Whisper base on the manifest.

Spawns the trainer as a subprocess so a training crash (MPS OOM, segfault)
does not take down the orchestrator. Each iteration writes its own train log.
"""
from __future__ import annotations

import os
import subprocess
import sys

from suno.paths import LOG_DIR, MANIFEST_FILE, MODELS_DIR, ROOT


def run(state: dict) -> dict:
    iter_n = state["iteration"]
    out_dir = MODELS_DIR / f"whisper-small-lora-iter{iter_n:04d}"
    log_path = LOG_DIR / f"train_iter{iter_n:04d}.log"

    steps = os.environ.get("SUNO_TRAIN_STEPS", "200")
    base_model = os.environ.get("SUNO_BASE_MODEL", "openai/whisper-small")

    cmd = [
        sys.executable, "-m", "suno.models.stt.whisper_lora_trainer",
        "--base-model", base_model,
        "--manifest", str(MANIFEST_FILE),
        "--out-dir", str(out_dir),
        "--max-steps", str(steps),
    ]
    last_adapter_rel = state.get("last_trained_adapter")
    if last_adapter_rel and (ROOT / last_adapter_rel).exists():
        cmd += ["--resume-from", str(ROOT / last_adapter_rel)]

    print(f"  log -> {log_path.relative_to(ROOT)}")
    print(f"  out -> {out_dir.relative_to(ROOT)}")

    with log_path.open("w") as f:
        result = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)

    if result.returncode == 0 and out_dir.exists():
        state["last_trained_adapter"] = str(out_dir.relative_to(ROOT))
        print("  trained adapter saved")
    else:
        print(f"  training FAILED (exit {result.returncode}); see {log_path.name}")
    return state
