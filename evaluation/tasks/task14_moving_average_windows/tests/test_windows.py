import pytest

from stats.windows import moving_average


def test_multiple_windows():
    assert moving_average([1, 2, 3, 4], 2) == [1.5, 2.5, 3.5]


def test_exact_window_size():
    assert moving_average([2, 4], 2) == [3.0]


def test_window_too_large():
    assert moving_average([1, 2], 3) == []


def test_invalid_window():
    with pytest.raises(ValueError):
        moving_average([1, 2], 0)
