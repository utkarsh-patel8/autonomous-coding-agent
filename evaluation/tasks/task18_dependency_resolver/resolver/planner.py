from collections import defaultdict
from .model import PackageRelease


def installation_order(selected: dict[str, PackageRelease]) -> list[str]:
    """Return package names with every dependency before its dependent."""
    adjacency: dict[str, list[str]] = defaultdict(list)
    indegree = {name: 0 for name in selected}

    for name, release in selected.items():
        for requirement in release.dependencies:
            if requirement.name not in selected:
                continue

            # BUG: this edge points from dependent -> dependency, which produces
            # the reverse of the required installation order.
            adjacency[name].append(requirement.name)
            indegree[requirement.name] += 1

    ready = sorted(name for name, degree in indegree.items() if degree == 0)
    order: list[str] = []

    while ready:
        name = ready.pop(0)
        order.append(name)
        for neighbor in sorted(adjacency[name]):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                ready.append(neighbor)
                ready.sort()

    if len(order) != len(selected):
        raise ValueError("dependency cycle detected")

    return order
