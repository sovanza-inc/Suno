"""Whisper Urdu STT inference.

Loads a pretrained Whisper checkpoint (MIT, commercial OK) and transcribes a
single audio file. Forces language=urdu so short clips don't auto-detect to
Hindi.

CLI entry point: `suno-stt` (see pyproject.toml).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from suno.device import pick_device


def _load_audio(path: str, target_sr: int = 16000):
    import librosa
    import soundfile as sf

    audio, sr = sf.read(path)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    if sr != target_sr:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)
    return audio, target_sr


def transcribe(model_id: str, audio_path: str, device: str | None = None) -> str:
    import torch
    from transformers import WhisperForConditionalGeneration, WhisperProcessor

    device = device or pick_device()
    print(f"Device: {device}  |  Model: {model_id}", flush=True)

    processor = WhisperProcessor.from_pretrained(model_id)
    model = WhisperForConditionalGeneration.from_pretrained(model_id).to(device)
    model.config.forced_decoder_ids = processor.get_decoder_prompt_ids(
        language="urdu", task="transcribe"
    )

    audio, sr = _load_audio(audio_path)
    inputs = processor(audio, sampling_rate=sr, return_tensors="pt").to(device)
    with torch.no_grad():
        generated = model.generate(inputs.input_features, max_new_tokens=440)
    return processor.batch_decode(generated, skip_special_tokens=True)[0].strip()


def main() -> None:
    p = argparse.ArgumentParser(description="Whisper Urdu STT inference")
    p.add_argument("audio", help="Path to audio file (wav/mp3/flac)")
    p.add_argument(
        "--model",
        default="openai/whisper-small",
        help="HF model id. Production: openai/whisper-large-v3. CPU-friendly: openai/whisper-small.",
    )
    p.add_argument("--device", default=None, help="cuda | mps | cpu (auto-detected if omitted)")
    args = p.parse_args()

    if not Path(args.audio).exists():
        print(f"Error: audio file not found: {args.audio}", file=sys.stderr)
        sys.exit(1)

    text = transcribe(args.model, args.audio, args.device)
    print("\n--- Transcription (Urdu) ---")
    print(text)


if __name__ == "__main__":
    main()
