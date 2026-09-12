from utils.unique import unique_preserving_order


def test_preserves_first_seen_order():
    assert unique_preserving_order(["b", "a", "b", "c", "a"]) == ["b", "a", "c"]


def test_already_unique():
    assert unique_preserving_order([3, 1, 2]) == [3, 1, 2]


def test_empty():
    assert unique_preserving_order([]) == []
