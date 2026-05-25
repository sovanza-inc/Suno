# Urdu Speech Datasets — Inventory

| Dataset | Hours | License | Commercial | Pakistani speakers | Notes |
|---|---|---|---|---|---|
| Common Voice 17 (ur) | ~80 | CC0 | ✅ | Mixed | Mostly Indian/Hindi-Urdu; quality varies; large but noisy |
| FLEURS (ur_pk) | ~12 | CC-BY 4.0 | ✅ (attribution) | ✅ | Read news, professional speakers, clean — best small test set |
| FLEURS (ur_in) | ~12 | CC-BY 4.0 | ✅ (attribution) | ❌ (Indian) | Transfer learning only |
| VoxPopuli (ur) | varies | CC0 | ✅ | — | Check availability per release |
| CSALT-LUMS Urdu | ~10 | Academic | Request needed | ✅ | Contact LUMS Center for Speech and Language Technologies |
| CSLU 22 Urdu (LDC) | ~5 | LDC license | Paid | ✅ | Read speech, ~$2k via Linguistic Data Consortium |
| PRUS | ~30 | Academic | Request needed | ✅ | Pakistan Research Urdu Speech corpus |
| Shrutilipi (AI4Bharat) | ~6.4k all Indic | CC-BY 4.0 | ✅ | ❌ (Indian) | Has Urdu subset; transfer-only |
| Pakistan parliamentary recordings | ~500 | Public domain (verify) | Verify | ✅ | Long audio, formal register, possibly noisy |
| Religious recitation (CC tafsir) | varies | Mixed | Verify per source | ✅ | Register mismatch risk for general STT |
| YouTube news scrape (custom) | unlimited | Complicated | ❌ until licensed | ✅ | Research-only; licensing must precede commercial deploy |

## Acquisition priority for Phase 2

1. **FLEURS ur_pk** — auto-downloaded by `scripts/02_download_urdu_data.py`, zero friction
2. **Common Voice ur** — same script, needs `huggingface-cli login`
3. **CSALT-LUMS** — email request, expect 2–4 weeks turnaround
4. **Internal recordings** — fastest path to *guaranteed Pakistani* coverage. Budget ~$5–10/hr/speaker × 50 speakers × 1hr = $250–500 (recording fees only; add coordinator + studio + transcription)
5. **PRUS / CSLU** — formal licensing in parallel, don't block on these

## Diversity targets for production model

Any Pakistani-Urdu STT we ship must cover:
- **Region:** Karachi, Lahore, Islamabad, Peshawar, Quetta urban + rural
- **Gender:** ≥40/60 split either direction
- **Age:** 18–25, 26–45, 46+
- **Register:** news, conversational, technical, religious
- **Code-switching:** English+Urdu hybrid (how most Pakistanis actually speak)
- **Numerals:** spoken numbers (both English-style and Urdu-style)
- **Named entities:** Pakistani place names, person names

For TTS, single-speaker studio quality (≥10hr, ≤1% transcript error) trumps multi-speaker noisy data.

## Manifest format

Every dataset processed for training lands in `data/<dataset_name>/` with a `manifest.jsonl`:

```jsonl
{"audio_path": "data/csalt/wav/0001.wav", "text": "...", "duration_sec": 4.32, "speaker_id": "spk_03", "region": "lahore", "gender": "F", "register": "news"}
```

This contract is non-negotiable — training scripts assume it.
