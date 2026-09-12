import pytest

from utils.chunks import chunk


def test_exact_chunks():
    assert chunk([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_remainder_is_preserved():
    assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]


def test_empty_input():
    assert chunk([], 3) == []


def test_invalid_size():
    with pytest.raises(ValueError):
        chunk([1, 2], 0)
