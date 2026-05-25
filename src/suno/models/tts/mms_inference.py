"""MMS-TTS Urdu baseline (facebook/mms-tts-urd).

License: CC-BY-NC 4.0 — benchmark only. Production TTS must come from our
own VITS / StyleTTS2 / F5-TTS training. See docs/models.md.

CLI entry: `suno-tts`
"""
from __future__ import annotations

import argparse
from pathlib import Path

from suno.device import pick_device


def synthesize(text: str, out_path: str, model_id: str = "facebook/mms-tts-urd", device: str | None = None) -> None:
    import scipy.io.wavfile
    import torch
    from transformers import AutoTokenizer, VitsModel

    device = device or pick_device()
    print(f"Device: {device}  |  Model: {model_id}", flush=True)

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = VitsModel.from_pretrained(model_id).to(device)

    inputs = tokenizer(text, return_tensors="pt").to(device)
    with torch.no_grad():
        output = model(**inputs).waveform

    audio_np = output.detach().cpu().numpy().squeeze()
    sample_rate = model.config.sampling_rate

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    scipy.io.wavfile.write(out_path, rate=sample_rate, data=audio_np)
    print(f"Saved: {out_path}  (sr={sample_rate}, duration={len(audio_np) / sample_rate:.2f}s)")


def main() -> None:
    p = argparse.ArgumentParser(description="MMS-TTS Urdu baseline (benchmark only — CC-BY-NC)")
    p.add_argument("text", help="Urdu text to synthesize")
    p.add_argument("--out", default="outputs/tts_sample.wav")
    p.add_argument("--model", default="facebook/mms-tts-urd")
    p.add_argument("--device", default=None)
    args = p.parse_args()
    synthesize(args.text, args.out, args.model, args.device)


if __name__ == "__main__":
    main()
