import pytest

from buildsys.graph import BuildGraph
from buildsys.parser import parse_manifest
from buildsys.scheduler import build_order


def position(values: list[str], item: str) -> int:
    return values.index(item)


def test_transitive_dependencies_are_built_before_dependents():
    graph = parse_manifest([
        "app: api ui",
        "api: core",
        "ui: core assets",
        "core:",
        "assets:",
    ])

    order = build_order(graph, ["app"])

    assert position(order, "core") < position(order, "api")
    assert position(order, "core") < position(order, "ui")
    assert position(order, "assets") < position(order, "ui")
    assert position(order, "api") < position(order, "app")
    assert position(order, "ui") < position(order, "app")


def test_only_requested_target_closure_is_scheduled():
    graph = parse_manifest([
        "app: core",
        "tool: util",
        "core:",
        "util:",
    ])

    order = build_order(graph, ["app"])

    assert len(order) == 2
    assert position(order, "core") < position(order, "app")
    assert "tool" not in order
    assert "util" not in order


def test_duplicate_dependencies_are_deduplicated():
    graph = BuildGraph()
    graph.add_dependency("app", "core")
    graph.add_dependency("app", "core")

    assert len(graph.dependencies_of("app")) == 1


def test_multiple_requested_targets_share_dependencies_once():
    graph = parse_manifest([
        "app: core",
        "tests: core",
        "core:",
    ])

    order = build_order(graph, ["tests", "app"])

    assert len(order) == 3
    assert position(order, "core") < position(order, "app")
    assert position(order, "core") < position(order, "tests")


def test_cycle_is_reported():
    graph = parse_manifest([
        "a: b",
        "b: c",
        "c: a",
    ])

    with pytest.raises(RuntimeError):
        build_order(graph, ["a"])
