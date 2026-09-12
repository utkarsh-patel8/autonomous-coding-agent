class BuildGraph:
    def __init__(self) -> None:
        self._dependencies: dict[str, list[str]] = {}

    def add_target(self, target: str) -> None:
        self._dependencies.setdefault(target, [])

    def add_dependency(self, target: str, dependency: str) -> None:
        self.add_target(target)
        self.add_target(dependency)

        # BUG: repeated declarations should not create duplicate graph edges.
        self._dependencies[target].append(dependency)

    def dependencies_of(self, target: str) -> list[str]:
        if target not in self._dependencies:
            raise KeyError(f"unknown target: {target}")

        return list(self._dependencies[target])

    def targets(self) -> list[str]:
        return sorted(self._dependencies)
