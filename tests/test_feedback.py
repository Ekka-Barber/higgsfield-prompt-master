"""US-031: opt-in outcome logging."""
import pytest

import feedback


@pytest.fixture(autouse=True)
def isolated_log(tmp_path):
    """Point logging at a throwaway DB and restore global state after."""
    was_enabled = feedback.is_enabled()
    original = feedback._path
    feedback.disable()
    feedback._path = tmp_path / "log.db"
    yield
    feedback._enabled = was_enabled
    feedback._path = original


def _result(model="gpt_image_2", photography=True, marketing=False):
    return {
        "prompt": "a test prompt",
        "model_recommendation": {"id": model},
        "intelligence": {"photography": photography, "marketing": marketing,
                         "mood": ""},
        "source_prompt_ids": [1, 2],
        "quality_score": {"total": 80},
    }


def test_disabled_by_default_writes_nothing():
    assert feedback.log_generation("goal", "cat", _result()) is None
    assert not feedback._path.exists(), "logging must not create a file when off"


def test_enable_creates_db_and_logs():
    feedback.enable()
    rid = feedback.log_generation("goal", "cat", _result())
    assert isinstance(rid, int)
    assert feedback.acceptance_rates()["logged"] == 1


def test_outcome_and_acceptance_rates():
    feedback.enable()
    good = feedback.log_generation("g1", "cat", _result(photography=True))
    bad = feedback.log_generation("g2", "cat", _result(photography=True))
    feedback.record_outcome(good, "accepted")
    feedback.record_outcome(bad, "regenerated")

    rates = feedback.acceptance_rates()
    assert rates["logged"] == 2 and rates["with_outcome"] == 2
    assert rates["by_layer"]["photography"]["acceptance"] == 0.5
    assert rates["by_model"]["gpt_image_2"]["total"] == 2


def test_unjudged_rows_report_none_not_zero():
    """An unjudged layer must be distinguishable from a rejected one."""
    feedback.enable()
    feedback.log_generation("g", "cat", _result())
    assert feedback.acceptance_rates()["by_layer"]["photography"]["acceptance"] is None


def test_bad_outcome_rejected():
    feedback.enable()
    rid = feedback.log_generation("g", "cat", _result())
    with pytest.raises(ValueError):
        feedback.record_outcome(rid, "loved-it")


def test_logging_failure_never_breaks_generation(monkeypatch):
    feedback.enable()
    monkeypatch.setattr(feedback, "_connect",
                        lambda: (_ for _ in ()).throw(OSError("disk full")))
    assert feedback.log_generation("g", "cat", _result()) is None
