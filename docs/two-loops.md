# Two loops, two purposes

Suno runs **two independent autonomous loops** that work on different layers of the system.

```
┌────────────────────────────────────────────────────────────────────┐
│  Loop 1: Python ML training loop                                  │
│  Owner: scripts/start_loop.sh → python -m suno.orchestrator.loop  │
│                                                                    │
│  Cycle: acquire → curate → train → eval → promote → cleanup       │
│         → journal → plan_next                                      │
│  Cadence: every 10 min (SUNO_LOOP_SLEEP)                          │
│  Cost: $0 — local compute only                                    │
│  Output: better model weights, PROGRESS.md, NEXT_TASK.md          │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│  Loop 2: Claude code-improvement loop                             │
│  Owner: scripts/claude_loop.sh → claude -p                        │
│                                                                    │
│  Cycle: read PROGRESS + NEXT_TASK + TASKS → pick next task →      │
│         execute → lint + test → commit                            │
│  Cadence: every 10 min (SUNO_CLAUDE_SLEEP)                        │
│  Cost: subscription tokens (Max plan) OR API metered              │
│  Output: better code, tests, docs                                 │
└────────────────────────────────────────────────────────────────────┘
```

## Why two

The Python loop is **deterministic** ML pipeline work — pull data, train, evaluate, promote. No creativity needed. Running an LLM here would be wasteful (cost, latency, OAuth expiry) for work that's a fixed program.

The Claude loop is **open-ended** code-improvement work — add a new phase, write a test, fix a bug, document a decision. A deterministic script can't do this; an LLM can.

Original ADR-005 ruled out Claude-in-a-loop for the *ML pipeline*. That stands. ADR-006 added Claude-in-a-loop as a *separate layer* for code work — different scope, different cost profile.

## How they interact

```
state/orchestrator.json   ← written by Loop 1, read by Loop 2
PROGRESS.md              ← written by Loop 1, read by Loop 2
NEXT_TASK.md             ← written by Loop 1, read by Loop 2
TASKS.md                 ← written by humans + Loop 2, read by Loop 2
src/suno/                ← read by Loop 1, edited by Loop 2 + humans
models/current_best/     ← written by Loop 1, never touched by Loop 2
```

Loop 2 never writes to Loop 1's runtime files (`state/`, `models/`, `data/`, `logs/`). Loop 1 never invokes Claude. The interface between them is the markdown/JSON files.

## Failure modes

| What could go wrong | Mitigation |
|---|---|
| Loop 2 breaks Loop 1's code | Loop 2 must run `make test` + `make lint` before committing |
| Loop 2 burns Max tokens | `SUNO_CLAUDE_SLEEP` defaults to 600s = ~6 iters/hr. Max plan: 50–200 prompts/5h |
| OAuth expires mid-loop | `claude -p` is a fresh session per iter — token refresh happens between calls. If expired, loop exits non-zero and bash retries. Long-term: use `claude setup-token` for ~1-year token |
| Loop 2 runs a dangerous command | `.claude/guard.sh` PreToolUse hook blocks `rm -rf /`, `git push`, `git reset --hard`, `sudo`, fork bombs, `curl \| sh` |
| Loop 2 fills TASKS.md with junk | Humans curate TASKS.md. The loop only marks `[ ]` → `[x]` and moves entries to `## Done` |

## Starting and stopping

### Loop 1 (ML)

```bash
make loop           # foreground, with caffeinate
make stop           # graceful stop
make loop-install   # launchd auto-start at login (recommended)
```

### Loop 2 (Claude)

```bash
make claude-loop        # foreground (recommended — watch the first few iters)
make claude-loop-stop   # graceful stop
make claude-loop-dry    # print prompt without invoking claude (debugging)
```

### Running both

You can run both concurrently. Loop 1 takes the heavy compute (training); Loop 2 makes small file edits in the gaps. They communicate only through committed files.

```bash
# Terminal 1
make loop           # ML training loop
# Terminal 2
make claude-loop    # Claude code loop
```

Or even better: install Loop 1 via launchd (background, auto-restart) and run Loop 2 manually when you have a TASKS.md queue you want chewed through.

## Cost reality

Loop 1: $0 ongoing.

Loop 2 on Max plan: subscription includes ~50–200 prompts per 5h. At 600s sleep that's 6 prompts/hr = 30/5h, comfortably under the lower bound. If you set `SUNO_CLAUDE_SLEEP=300` (5 min), you'd be at 60/5h, still safe on Max 5x. Watch usage at https://platform.claude.com/usage.

Loop 2 on API key: ~$0.10–0.50 per iteration depending on context size + task complexity. 10 iters/hr × 8 hrs = $8–40 overnight. Set hard caps via the Anthropic console.

**Do not** run Loop 2 with `--dangerously-skip-permissions` on host. The guard hook is the primary protection; permission mode `acceptEdits` is the secondary. Both should be on.

## What goes in TASKS.md

Scoped, low-risk, verifiable. Each task should be doable in a single Claude session (no multi-day epics), have a clear acceptance criterion, and pass `make test` after.

Good task: "Add `test_gitignore.py` that fails if `src/suno/data/__init__.py` is ignored."
Bad task: "Improve the model" (no acceptance), "Refactor the entire orchestrator" (too broad).

See `TASKS.md` for the current queue.
