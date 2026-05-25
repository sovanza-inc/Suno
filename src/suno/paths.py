"""Canonical paths for the Suno project.

Importing modules pulls these so we never sprinkle path-arithmetic across the
codebase.
"""
from __future__ import annotations

from pathlib import Path

# This file lives at src/suno/paths.py — the project root is three levels up.
ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "data"
MODELS_DIR = ROOT / "models"
OUTPUT_DIR = ROOT / "outputs"
LOG_DIR = ROOT / "logs"
STATE_DIR = ROOT / "state"
CONFIGS_DIR = ROOT / "configs"
DOCS_DIR = ROOT / "docs"
BENCHMARKS_DIR = ROOT / "benchmarks"

MANIFEST_FILE = DATA_DIR / "manifest.jsonl"
STATE_FILE = STATE_DIR / "orchestrator.json"
ERROR_LOG = LOG_DIR / "errors.log"
PROGRESS_FILE = ROOT / "PROGRESS.md"
NEXT_TASK_FILE = ROOT / "NEXT_TASK.md"

BEST_MODEL_DIR = MODELS_DIR / "current_best"

# Ensure ephemeral dirs exist on import
for _d in (DATA_DIR, MODELS_DIR, OUTPUT_DIR, LOG_DIR, STATE_DIR):
    _d.mkdir(exist_ok=True, parents=True)
