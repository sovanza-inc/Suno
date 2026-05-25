"""Verify the local environment before running anything heavy."""
from __future__ import annotations

import importlib
import platform
import sys


def check() -> int:
    failures = 0
    print(f"Python: {sys.version.split()[0]} on {platform.platform()}")

    try:
        import torch

        print(f"PyTorch: {torch.__version__}")
        cuda_ok = torch.cuda.is_available()
        print(f"  CUDA available: {cuda_ok}")
        if cuda_ok:
            print(f"  CUDA device: {torch.cuda.get_device_name(0)}")
            print(f"  CUDA capability: {torch.cuda.get_device_capability(0)}")
        mps_ok = hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
        print(f"  MPS (Apple Silicon): {mps_ok}")
        if not (cuda_ok or mps_ok):
            print("  ! No GPU/MPS detected — fine for small-model inference, not for training.")
    except ImportError:
        print("PyTorch: NOT INSTALLED")
        failures += 1

    for pkg in ("transformers", "datasets", "librosa", "soundfile", "jiwer", "scipy", "tqdm", "peft"):
        try:
            mod = importlib.import_module(pkg)
            v = getattr(mod, "__version__", "unknown")
            print(f"{pkg}: {v}")
        except ImportError:
            print(f"{pkg}: NOT INSTALLED")
            failures += 1

    try:
        import suno
        print(f"suno (this package): {suno.__version__}")
    except ImportError:
        print("suno (this package): NOT INSTALLED — run `pip install -e .`")
        failures += 1

    if failures:
        print(f"\n{failures} item(s) missing. Run: pip install -e '.[dev]'")
        return 1
    print("\nEnvironment OK.")
    return 0


if __name__ == "__main__":
    sys.exit(check())
