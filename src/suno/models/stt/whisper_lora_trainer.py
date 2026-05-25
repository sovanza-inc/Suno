"""Whisper LoRA fine-tune for Urdu on Apple Silicon (MPS) with 16 GB RAM.

Tuned defaults:
- Base: openai/whisper-small (244M params, fits MPS comfortably)
- LoRA r=32 alpha=64 on q_proj/v_proj (~5M trainable params)
- batch=1 + grad_accum=8 (effective batch 8) — safe on 16 GB
- fp16/bf16 OFF (MPS still has correctness issues with mixed precision)

The orchestrator calls this once per iteration; each call trains for --max-steps
additional steps and saves the adapter to --out-dir, optionally resuming from
the previous iteration's adapter.

CLI entry: `suno-train`
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from suno.data.manifest import read_manifest, split_filter
from suno.device import pick_device


def _build_dataset(entries: list[dict], processor):
    from datasets import Audio, Dataset

    audios = [{"path": e["path"]} for e in entries]
    texts = [e["text"] for e in entries]
    ds = Dataset.from_dict({"audio": audios, "text": texts})
    ds = ds.cast_column("audio", Audio(sampling_rate=16000))

    def _prep(batch):
        audio = batch["audio"]
        feats = processor.feature_extractor(
            audio["array"], sampling_rate=audio["sampling_rate"]
        ).input_features[0]
        labels = processor.tokenizer(batch["text"]).input_ids
        return {"input_features": feats, "labels": labels}

    return ds.map(_prep, remove_columns=["audio", "text"])


class DataCollator:
    def __init__(self, processor):
        self.processor = processor

    def __call__(self, features):
        in_feats = [{"input_features": f["input_features"]} for f in features]
        batch = self.processor.feature_extractor.pad(in_feats, return_tensors="pt")
        lab_feats = [{"input_ids": f["labels"]} for f in features]
        labels_batch = self.processor.tokenizer.pad(lab_feats, return_tensors="pt")
        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)
        if (labels[:, 0] == self.processor.tokenizer.bos_token_id).all().cpu().item():
            labels = labels[:, 1:]
        batch["labels"] = labels
        return batch


def train(
    base_model: str,
    manifest_path: Path,
    out_dir: Path,
    max_steps: int = 200,
    lr: float = 1e-4,
    batch_size: int = 1,
    grad_accum: int = 8,
    resume_from: Path | None = None,
    lora_r: int = 32,
    lora_alpha: int = 64,
) -> int:
    from peft import LoraConfig, PeftModel, get_peft_model
    from transformers import (
        Seq2SeqTrainer,
        Seq2SeqTrainingArguments,
        WhisperForConditionalGeneration,
        WhisperProcessor,
    )

    device = pick_device()
    print(f"device={device}", flush=True)

    entries = read_manifest(manifest_path)
    train_entries = split_filter(entries, "train")
    print(f"train samples: {len(train_entries)}", flush=True)
    if not train_entries:
        print("no train samples in manifest; exiting", flush=True)
        return 2

    processor = WhisperProcessor.from_pretrained(base_model)
    processor.tokenizer.set_prefix_tokens(language="urdu", task="transcribe")
    model = WhisperForConditionalGeneration.from_pretrained(base_model)
    model.config.forced_decoder_ids = None
    model.config.suppress_tokens = []
    model.generation_config.language = "urdu"
    model.generation_config.task = "transcribe"

    if resume_from and resume_from.exists():
        print(f"resuming from {resume_from}", flush=True)
        model = PeftModel.from_pretrained(model, str(resume_from), is_trainable=True)
    else:
        cfg = LoraConfig(
            r=lora_r,
            lora_alpha=lora_alpha,
            target_modules=["q_proj", "v_proj"],
            lora_dropout=0.05,
            bias="none",
        )
        model = get_peft_model(model, cfg)
    model.print_trainable_parameters()

    ds_train = _build_dataset(train_entries, processor)

    targs = Seq2SeqTrainingArguments(
        output_dir=str(out_dir),
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=grad_accum,
        learning_rate=lr,
        max_steps=max_steps,
        warmup_steps=min(20, max_steps // 10),
        logging_steps=10,
        save_steps=max_steps,
        save_total_limit=2,
        fp16=False,
        bf16=False,
        remove_unused_columns=False,
        label_names=["labels"],
        report_to=[],
        dataloader_num_workers=0,
        dataloader_pin_memory=False,
    )

    trainer = Seq2SeqTrainer(
        args=targs,
        model=model,
        train_dataset=ds_train,
        data_collator=DataCollator(processor),
    )
    trainer.train()

    out_dir.mkdir(exist_ok=True, parents=True)
    model.save_pretrained(out_dir)
    processor.save_pretrained(out_dir)
    print(f"saved adapter to {out_dir}", flush=True)
    return 0


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--base-model", default="openai/whisper-small")
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--out-dir", required=True, type=Path)
    p.add_argument("--max-steps", type=int, default=200)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--batch-size", type=int, default=1)
    p.add_argument("--grad-accum", type=int, default=8)
    p.add_argument("--resume-from", type=Path, default=None)
    p.add_argument("--lora-r", type=int, default=32)
    p.add_argument("--lora-alpha", type=int, default=64)
    args = p.parse_args()

    rc = train(
        base_model=args.base_model,
        manifest_path=args.manifest,
        out_dir=args.out_dir,
        max_steps=args.max_steps,
        lr=args.lr,
        batch_size=args.batch_size,
        grad_accum=args.grad_accum,
        resume_from=args.resume_from,
        lora_r=args.lora_r,
        lora_alpha=args.lora_alpha,
    )
    sys.exit(rc)


if __name__ == "__main__":
    main()
