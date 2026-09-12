from intervals.merge import merge_intervals


def test_overlapping_intervals():
    assert merge_intervals([(1, 4), (3, 6)]) == [(1, 6)]


def test_touching_intervals():
    assert merge_intervals([(1, 3), (3, 5)]) == [(1, 5)]


def test_disjoint_intervals():
    assert merge_intervals([(1, 2), (4, 5)]) == [(1, 2), (4, 5)]
