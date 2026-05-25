"""Visualize the loop's progress as a terminal sparkline + summary table.

No external deps beyond Python stdlib + suno (already installed via -e .).
Run any time: `python scripts/show_progress.py` or `make` target (see Makefile).
"""
from __future__ import annotations

import sys

from suno.orchestrator import state as state_module


SPARK = "▁▂▃▄▅▆▇█"


def sparkline(values: list[float]) -> str:
    if not values:
        return "(no data)"
    vmin, vmax = min(values), max(values)
    if vmin == vmax:
        return SPARK[0] * len(values)
    n = len(SPARK) - 1
    return "".join(SPARK[round(n * (v - vmin) / (vmax - vmin))] for v in values)


def main() -> int:
    state = state_module.load()
    iter_n = state.get("iteration", 0)
    best_wer = state.get("best_wer")
    best_iter = state.get("best_wer_iteration")
    last_wer = state.get("last_wer")
    samples = state.get("data_samples_curated", 0)
    hours = state.get("data_hours_curated", 0.0)
    history = state.get("eval_history", [])

    print(f"Suno loop status — iteration {iter_n}")
    print(f"  Manifest:  {samples} samples (~{hours} h)")
    print(f"  Best WER:  {best_wer if best_wer is not None else 'n/a'}"
          f"{f' (iter {best_iter})' if best_iter is not None else ''}")
    print(f"  Last WER:  {last_wer if last_wer is not None else 'n/a'}")

    if history:
        wers = [h["wer"] for h in history if h.get("wer") is not None]
        if wers:
            print()
            print(f"  WER history  ({len(wers)} evals)")
            print(f"    min={min(wers):.4f}  max={max(wers):.4f}  last={wers[-1]:.4f}")
            print(f"    {sparkline(wers)}")
            print()
            print("  Recent (last 10):")
            for h in history[-10:]:
                marker = " ← BEST" if best_iter == h.get("iter") else ""
                print(f"    iter {h.get('iter', '?'):>4}  WER {h.get('wer', float('nan')):.4f}{marker}")

    cleanup = state.get("last_cleanup")
    if cleanup:
        print()
        print(f"  Last cleanup: deleted {cleanup['deleted']} adapter(s), freed {cleanup['freed_mb']} MB")

    return 0


if __name__ == "__main__":
    sys.exit(main())
