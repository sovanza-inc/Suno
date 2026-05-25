"""Evaluate a Whisper (base or LoRA-adapted) model on a HF audio dataset.

Emits a single FINAL_WER line so the orchestrator can grep it. Default
dataset: FLEURS ur_pk test (held out from training).

CLI entry: `suno-eval`
"""
from __future__ import annotations

import argparse

from suno.device import pick_device
from suno.evaluation.metrics import cer, wer


def evaluate(
    model_id: str,
    dataset_id: str = "google/fleurs",
    dataset_config: str = "ur_pk",
    split: str = "test",
    adapter_path: str | None = None,
    max_samples: int = 50,
    device: str | None = None,
) -> tuple[float, float]:
    import torch
    from datasets import load_dataset
    from tqdm import tqdm
    from transformers import WhisperForConditionalGeneration, WhisperProcessor

    device = device or pick_device()
    print(f"device={device}  base={model_id}  adapter={adapter_path}", flush=True)

    processor = WhisperProcessor.from_pretrained(model_id)
    base = WhisperForConditionalGeneration.from_pretrained(model_id)

    if adapter_path:
        from peft import PeftModel

        model = PeftModel.from_pretrained(base, adapter_path).to(device).eval()
    else:
        model = base.to(device).eval()

    model.config.forced_decoder_ids = processor.get_decoder_prompt_ids(
        language="urdu", task="transcribe"
    )

    ds = load_dataset(dataset_id, dataset_config, split=split)
    ds = ds.select(range(min(max_samples, len(ds))))

    refs: list[str] = []
    hyps: list[str] = []
    for sample in tqdm(ds, desc="eval"):
        audio = sample["audio"]["array"]
        sr = sample["audio"]["sampling_rate"]
        ref = sample.get("transcription") or sample.get("raw_transcription") or sample.get("sentence") or ""
        if not ref.strip():
            continue
        inputs = processor(audio, sampling_rate=sr, return_tensors="pt").to(device)
        with torch.no_grad():
            ids = model.generate(inputs.input_features, max_new_tokens=440)
        hyp = processor.batch_decode(ids, skip_special_tokens=True)[0].strip()
        refs.append(ref)
        hyps.append(hyp)

    w = wer(refs, hyps)
    c = cer(refs, hyps)
    print(f"\nEvaluated {len(refs)} samples")
    print(f"FINAL_WER {w:.4f}")
    print(f"FINAL_CER {c:.4f}")
    return w, c


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="openai/whisper-small", dest="model_id")
    p.add_argument("--adapter", default=None, help="Optional path to PEFT adapter")
    p.add_argument("--dataset", default="google/fleurs", dest="dataset_id")
    p.add_argument("--config", default="ur_pk", dest="dataset_config")
    p.add_argument("--split", default="test")
    p.add_argument("--max-samples", type=int, default=50)
    p.add_argument("--device", default=None)
    args = p.parse_args()
    evaluate(
        model_id=args.model_id,
        dataset_id=args.dataset_id,
        dataset_config=args.dataset_config,
        split=args.split,
        adapter_path=args.adapter,
        max_samples=args.max_samples,
        device=args.device,
    )


if __name__ == "__main__":
    main()
