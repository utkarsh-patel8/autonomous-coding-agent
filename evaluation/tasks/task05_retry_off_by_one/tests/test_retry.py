import pytest

from retrying.retry import run_with_retries


def test_zero_retries_still_runs_once():
    assert run_with_retries(lambda: 42, retries=0) == 42


def test_two_retries_means_three_total_attempts():
    attempts = {"count": 0}

    def flaky():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RuntimeError("temporary")
        return "ok"

    assert run_with_retries(flaky, retries=2) == "ok"
    assert attempts["count"] == 3


def test_final_exception_is_raised():
    attempts = {"count": 0}

    def always_fails():
        attempts["count"] += 1
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        run_with_retries(always_fails, retries=2)

    assert attempts["count"] == 3
