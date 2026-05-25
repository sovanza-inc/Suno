# Deployment

Not yet implemented — Phase 5 in [roadmap.md](roadmap.md). This is the planned shape.

## Production inference targets

| Surface | Latency budget | Approach |
|---|---|---|
| Server batch transcription | minutes OK | Whisper-medium LoRA on cloud GPU when available |
| Server streaming | <1s end-of-utterance | faster-whisper (CTranslate2) with VAD chunking on CPU |
| On-device (mobile/edge) | <500ms first chunk | Quantized Whisper-small (int8) + ONNX runtime |

## Inference path

After Phase 5 the planned API surface:

```python
from suno.inference import SunoSTT

stt = SunoSTT.load("current_best")        # loads models/current_best/
text = stt.transcribe("audio.wav")
for chunk in stt.transcribe_stream(audio_stream):
    print(chunk)
```

## Model packaging

Promoted models in `models/current_best/` are PEFT adapter directories. For deployment:

1. **Merge adapter → base** to get a single Whisper model that doesn't need PEFT at runtime
2. **Convert to CTranslate2** with `ct2-transformers-converter` for faster-whisper
3. **Quantize to int8** for edge
4. Publish with a model card from [`docs/model-cards/`](model-cards/)

## Hosting

TBD. Likely path:
- Self-host on a Pakistani VPS (cost, sovereignty, low-latency to PK users)
- HuggingFace Hub mirrors for open distribution
- Customer on-prem packaging (Docker image) for enterprise contracts

## License at deployment

- Code: Apache-2.0 (this repo)
- Whisper base weights: MIT (commercial OK)
- Adapter weights: produced by us → license TBD per release
- MMS-TTS samples in `outputs/`: CC-BY-NC, **never ship**

See [decision 001](decisions/001-open-source-only.md).
