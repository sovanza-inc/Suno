"""Phases for the autonomous orchestrator loop.

Each phase is a module exposing `run(state: dict) -> dict`. Phases are pure
state-transformers; they read+write state, may produce side effects (files,
subprocesses), and must NOT raise — orchestrator catches but phases that
swallow their own errors keep the loop healthier.

Add new phases here, then register them in `suno.orchestrator.loop.PHASES`.
"""
