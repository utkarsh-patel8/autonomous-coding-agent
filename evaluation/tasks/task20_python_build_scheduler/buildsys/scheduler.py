import heapq

from buildsys.graph import BuildGraph


def _collect_closure(
    graph: BuildGraph,
    target: str,
    closure: set[str],
    visiting: set[str],
) -> None:
    if target in closure:
        return

    if target in visiting:
        raise RuntimeError("dependency cycle detected")

    visiting.add(target)

    for dependency in graph.dependencies_of(target):
        _collect_closure(graph, dependency, closure, visiting)

    visiting.remove(target)
    closure.add(target)


def build_order(
    graph: BuildGraph,
    requested_targets: list[str],
) -> list[str]:
    closure: set[str] = set()
    visiting: set[str] = set()

    for target in requested_targets:
        _collect_closure(graph, target, closure, visiting)

    indegree = {name: 0 for name in closure}
    adjacency: dict[str, list[str]] = {
        name: [] for name in closure
    }

    for name in closure:
        for dependency in graph.dependencies_of(name):
            if dependency not in closure:
                continue

            # BUG: scheduling edges are reversed. Dependencies must be ready
            # before the targets that consume them.
            adjacency[name].append(dependency)
            indegree[dependency] += 1

    ready = [
        name
        for name, degree in indegree.items()
        if degree == 0
    ]
    heapq.heapify(ready)

    order: list[str] = []

    while ready:
        current = heapq.heappop(ready)
        order.append(current)

        for next_target in sorted(adjacency[current]):
            indegree[next_target] -= 1

            if indegree[next_target] == 0:
                heapq.heappush(ready, next_target)

    if len(order) != len(closure):
        raise RuntimeError("dependency cycle detected")

    return order
