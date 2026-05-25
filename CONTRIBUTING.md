# Contributing

Thanks for considering a contribution to Suno.

## Quick rules

1. Read [`CLAUDE.md`](CLAUDE.md) (if you are an AI agent) or [`AGENTS.md`](AGENTS.md) (any agent) first.
2. Architectural decisions are in [`docs/decisions/`](docs/decisions/). Don't violate them without filing a new ADR.
3. Every PR runs CI: `ruff` + `pytest`. Make sure both pass locally.
4. If your change touches `src/suno/orchestrator/`, smoke-test with `make smoke`.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install     # optional
```

## Common commands

```bash
make test       # pytest tests/
make lint       # ruff check
make fmt        # ruff format
make smoke      # one-iteration loop smoke test
```

## Commit style

- Imperative mood, ≤72 char subject
- Body is optional; if present, separate from subject with a blank line
- Examples:
  - `feat: add pseudo-labeling phase`
  - `fix: handle empty manifest in trainer`
  - `docs: clarify hardware constraints`

## Branch names

`<type>/<short-slug>` — examples:
- `feat/codeswitch-eval-set`
- `fix/mps-oom-on-batch-2`
- `docs/training-guide`

## What to work on

Default to the recommendation in `NEXT_TASK.md` — it's regenerated every loop iteration based on observed trends. If you have a different idea, file an issue using the [feature template](.github/ISSUE_TEMPLATE/feature.md) first to check it doesn't conflict with locked decisions.

## Data contributions

If you have rights to Pakistani-Urdu audio (or other Pakistani languages), please open an issue rather than committing it directly — we'll work out licensing and where to host. Audio files do NOT belong in the git repo (see `.gitignore`).

## Code reviews

Reviewers focus on:
- Does it respect the [locked decisions](docs/decisions/)?
- Does it have tests for new logic?
- Does it update documentation?
- Does it keep the loop runnable on a 16 GB Mac?

## Reporting bugs

Use the [bug template](.github/ISSUE_TEMPLATE/bug.md). Attach `logs/errors.log` and any relevant `logs/train_iter*.log` or `logs/eval_iter*.log`.
