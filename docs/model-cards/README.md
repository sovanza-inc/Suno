# Model cards

Every promoted model in `models/current_best/` gets a card here with provenance, training data, eval results, and known failure modes.

Inspired by [Mitchell et al. (2019) — Model Cards for Model Reporting](https://arxiv.org/abs/1810.03677) and Shisa AI's release notes.

## Naming

`suno-stt-urdu-vMAJ.MIN.iterNNNN.md`

- `MAJ.MIN` follows semver — bump MAJ on architecture change, MIN on dataset change
- `iterNNNN` is the loop iteration that produced this checkpoint

## Template

```markdown
# suno-stt-urdu-v0.1.iter0042

**Released:** YYYY-MM-DD
**Base:** openai/whisper-small (MIT)
**Adapter type:** PEFT LoRA, r=32 alpha=64 on q_proj/v_proj
**Trained on:** FLEURS ur_pk train (~10 hr) [+ Common Voice ur train (~70 hr) if applicable]

## Eval results

| Dataset | Split | Samples | WER | CER |
|---|---|---|---|---|
| FLEURS ur_pk | test | N | X.XXX | X.XXX |
| Common Voice ur | test | N | X.XXX | X.XXX |

## Examples (spot-check)

| Reference | Hypothesis | Note |
|---|---|---|
| اردو متن | ... | ... |

## Known failure modes

- ...

## Hardware used

- M5 Pro 16 GB, MPS backend
- ~N iterations × ~M minutes each = ~K hours total compute

## License

Adapter weights: TBD (Apache-2.0 most likely)
Base weights: MIT (OpenAI Whisper)

## Reproduction

git rev: <sha>
Loop iteration: NNNN
State snapshot: state/orchestrator.json (committed alongside this card)
```
