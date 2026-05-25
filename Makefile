.PHONY: install dev test lint fmt smoke loop loop-install loop-uninstall stop clean

install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -e ".[dev]"

dev: install
	. .venv/bin/activate && pre-commit install || true

test:
	. .venv/bin/activate && pytest tests/ -v

lint:
	. .venv/bin/activate && ruff check src/ tests/

fmt:
	. .venv/bin/activate && ruff format src/ tests/

smoke:
	. .venv/bin/activate && SUNO_LOOP_MAX_ITERS=1 SUNO_TRAIN_STEPS=5 SUNO_EVAL_SAMPLES=2 python -m suno.orchestrator.loop

status:
	. .venv/bin/activate && python scripts/show_progress.py

plan:
	. .venv/bin/activate && suno-plan

loop:
	./scripts/start_loop.sh

stop:
	./scripts/stop_loop.sh

loop-install:
	./scripts/install_launchd.sh

loop-uninstall:
	./scripts/uninstall_launchd.sh

clean:
	rm -rf build/ dist/ *.egg-info src/*.egg-info __pycache__ .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
