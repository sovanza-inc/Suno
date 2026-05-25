"""Phase 6: append iteration summary to PROGRESS.md, auto-commit, optionally push."""
from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone

from suno.paths import PROGRESS_FILE, ROOT


def _git(*args: str) -> int:
    return subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True).returncode


def run(state: dict) -> dict:
    iter_n = state["iteration"]
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    best_wer = state.get("best_wer")
    best_iter = state.get("best_wer_iteration")
    promoted = state.get("promoted_this_iteration", False)
    block = (
        f"\n## Iteration {iter_n} — {ts}\n\n"
        f"- Manifest samples: {state.get('data_samples_curated', 'n/a')} "
        f"(~{state.get('data_hours_curated', 'n/a')}h FLEURS)\n"
        f"- Trained adapter: `{state.get('last_trained_adapter', 'n/a')}`\n"
        f"- Last WER: {state.get('last_wer', 'n/a')} "
        f"| Last CER: {state.get('last_cer', 'n/a')}\n"
        f"- Best WER: {best_wer if best_wer is not None else 'n/a'} "
        f"(iter {best_iter if best_iter is not None else 'n/a'})"
        f"{' — **new best**' if promoted else ''}\n"
    )

    if not PROGRESS_FILE.exists():
        PROGRESS_FILE.write_text("# Suno — Autonomous Loop Progress Log\n")
    with PROGRESS_FILE.open("a") as f:
        f.write(block)

    try:
        _git("add", "PROGRESS.md", "state/orchestrator.json", "NEXT_TASK.md")
        msg = f"loop iter {iter_n}"
        if state.get("last_wer") is not None:
            msg += f" — WER {state['last_wer']:.4f}"
        if promoted:
            msg += " (new best)"
        _git("commit", "-m", msg, "--no-verify")
        if os.environ.get("SUNO_AUTO_PUSH") == "1" and promoted:
            _git("push")
    except Exception as e:
        print(f"  git commit/push skipped: {e}")

    print("  journal updated")
    return state
