"""Phase 7: rewrite NEXT_TASK.md based on observed loop trends.

Always runs last. Idempotent — safe to call any time.
"""
from __future__ import annotations

from suno.orchestrator.task_planner import write_next_task


def run(state: dict) -> dict:
    path = write_next_task(state)
    print(f"  wrote {path.name}")
    return state
