from buildsys.graph import BuildGraph


def parse_manifest(lines: list[str]) -> BuildGraph:
    graph = BuildGraph()

    for line in lines:
        if ":" not in line:
            raise ValueError("manifest line missing ':'")

        target, dependency_text = line.split(":", 1)

        if not target:
            raise ValueError("empty target")

        graph.add_target(target)

        for dependency in dependency_text.split():
            graph.add_dependency(target, dependency)

    return graph
