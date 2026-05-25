# The autonomous orchestrator

A deterministic Python loop that trains and evaluates Whisper LoRA adapters continuously while you sleep. Architecture follows the "Pragmatic Loop" pattern from [research/compass_artifact.md](research/compass_artifact.md).

## Lifecycle of one iteration

1. **acquire** — verify FLEURS ur_pk is cached locally (HF datasets); opt-in pull Common Voice if `SUNO_FETCH_CV=1`. Idempotent — fast on subsequent runs.
2. **curate** — rebuild `data/manifest.jsonl` from cached datasets, metadata-only (no audio decoding).
3. **train** — subprocess `python -m suno.models.stt.whisper_lora_trainer` for `SUNO_TRAIN_STEPS` LoRA steps, resuming from the previous iteration's adapter if it exists.
4. **evaluate** — subprocess `python -m suno.evaluation.stt` on FLEURS ur_pk test, `SUNO_EVAL_SAMPLES` samples. Emits `FINAL_WER` to log; phase parses it back into state.
5. **promote** — if WER improved, copy the new adapter to `models/current_best/`.
6. **journal** — append summary to `PROGRESS.md`, `git add` + `git commit` + (opt) `git push`.
7. **plan_next** — task_planner rewrites `NEXT_TASK.md` based on recent trends.

Then sleep `SUNO_LOOP_SLEEP` seconds (default 600) and repeat.

## Environment variables

| Var | Default | Effect |
|---|---|---|
| `SUNO_LOOP_SLEEP` | 600 | Seconds between iterations |
| `SUNO_LOOP_MAX_ITERS` | 100 | Safety cap per process invocation |
| `SUNO_TRAIN_STEPS` | 200 | LoRA steps per training subphase |
| `SUNO_EVAL_SAMPLES` | 50 | Held-out test samples per eval |
| `SUNO_BASE_MODEL` | `openai/whisper-small` | Base model for LoRA |
| `SUNO_FETCH_CV` | unset | `1` enables Common Voice ur (~80 hr) |
| `SUNO_AUTO_PUSH` | unset | `1` runs `git push` after every new-best promotion |

## Running

```bash
# foreground (logs visible)
make loop
# or
./scripts/start_loop.sh

# stop
make stop
```

## Auto-start (launchd, macOS)

```bash
make loop-install     # installs ~/Library/LaunchAgents/com.suno.orchestrator.plist
make loop-uninstall
```

The plist sets `RunAtLoad=true`, `KeepAlive.Crashed=true`, `ThrottleInterval=60`. After install the loop runs at every login and auto-restarts on crash.

## Crash recovery

- State at `state/orchestrator.json` is written atomically (write to temp + rename) so an OOM mid-iteration cannot corrupt it.
- The next process invocation reads the state and continues from the next iteration number.
- Each train/eval subphase runs in its own subprocess, so a Python crash inside HuggingFace doesn't kill the orchestrator — just the current iteration's training step.

## Reading the loop's mind

- `PROGRESS.md` — per-iteration summaries, newest at bottom
- `state/orchestrator.json` — full current state (best WER, iteration count, last error)
- `NEXT_TASK.md` — what the loop thinks the next human/agent should do
- `logs/train_iter*.log` — per-iteration training logs
- `logs/eval_iter*.log` — per-iteration eval logs
- `logs/errors.log` — anything that threw
- `git log --oneline` — auto-commit trail (`loop iter N — WER X.XXXX`)

## Cost

Zero ongoing cost — local compute only. Apple Silicon thermal envelope is the real constraint; expect ~10-30 minutes per training subphase on M5 Pro for whisper-small at the default settings.

## Extending

Adding a new phase:

1. Write `src/suno/orchestrator/phases/<name>.py` with `run(state) -> dict`
2. Register in `src/suno/orchestrator/loop.py:PHASES`
3. Smoke-test: `SUNO_LOOP_MAX_ITERS=1 make smoke`
4. Update this file and `docs/architecture.md`

See [CLAUDE.md](../CLAUDE.md) for the full session protocol.
