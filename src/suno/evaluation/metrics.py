"""Evaluation metrics.

For now we use jiwer's WER/CER directly. Add Urdu-specific normalization here
when needed (e.g. Arabic-Indic numeral handling, common punctuation strip).
"""
from __future__ import annotations

import re
import unicodedata

from jiwer import cer as _cer
from jiwer import wer as _wer


def normalize_urdu(text: str) -> str:
    """Light normalization: NFC, strip punctuation, collapse whitespace.

    Conservative — does NOT touch numerals or transliterated English (those
    are signal for code-switching evaluation, not noise).
    """
    t = unicodedata.normalize("NFC", text)
    t = re.sub(r"[\.,!?؛،۔:;\"'\-—()]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def wer(refs: list[str], hyps: list[str], normalize: bool = True) -> float:
    if normalize:
        refs = [normalize_urdu(r) for r in refs]
        hyps = [normalize_urdu(h) for h in hyps]
    return float(_wer(refs, hyps))


def cer(refs: list[str], hyps: list[str], normalize: bool = True) -> float:
    if normalize:
        refs = [normalize_urdu(r) for r in refs]
        hyps = [normalize_urdu(h) for h in hyps]
    return float(_cer(refs, hyps))
