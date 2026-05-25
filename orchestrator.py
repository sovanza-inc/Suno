"""Top-level shim — keeps `python orchestrator.py` working after restructure.

Prefer `python -m suno.orchestrator.loop` or the `suno-loop` CLI entry point
after `pip install -e .`.
"""
from suno.orchestrator.loop import main

if __name__ == "__main__":
    main()
