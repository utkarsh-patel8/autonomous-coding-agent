from graph.path import shortest_path


def test_returns_shortest_path():
    graph = {
        "A": ["B", "C"],
        "B": ["G"],
        "C": ["D"],
        "D": ["E"],
        "E": ["G"],
        "G": [],
    }

    assert shortest_path(graph, "A", "G") == ["A", "B", "G"]


def test_no_path():
    graph = {
        "A": ["B"],
        "B": [],
        "C": [],
    }

    assert shortest_path(graph, "A", "C") is None
