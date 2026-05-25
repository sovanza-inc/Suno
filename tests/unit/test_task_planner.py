from suno.orchestrator.task_planner import _recent_wer_trend, plan


def test_trend_insufficient():
    assert _recent_wer_trend([]) == "insufficient"
    assert _recent_wer_trend([{"wer": 0.5}]) == "insufficient"


def test_trend_improving():
    history = [{"wer": 0.5}, {"wer": 0.48}, {"wer": 0.45}, {"wer": 0.42}]
    assert _recent_wer_trend(history) == "improving"


def test_trend_regressing():
    history = [{"wer": 0.30}, {"wer": 0.32}, {"wer": 0.35}, {"wer": 0.40}]
    assert _recent_wer_trend(history) == "regressing"


def test_trend_plateau():
    history = [{"wer": 0.30}, {"wer": 0.30}, {"wer": 0.30}, {"wer": 0.30}]
    assert _recent_wer_trend(history) == "plateau"


def test_plan_returns_markdown():
    state = {
        "iteration": 5,
        "best_wer": 0.30,
        "best_wer_iteration": 4,
        "last_wer": 0.30,
        "data_samples_curated": 100,
        "eval_history": [{"wer": 0.30}, {"wer": 0.30}, {"wer": 0.30}, {"wer": 0.30}],
    }
    md = plan(state)
    assert md.startswith("# NEXT_TASK")
    assert "Current state" in md
    assert "Recommended next task" in md
