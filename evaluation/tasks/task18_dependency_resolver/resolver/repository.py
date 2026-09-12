from collections import defaultdict
from .model import PackageRelease, Requirement


class PackageRepository:
    def __init__(self):
        self._releases: dict[str, list[PackageRelease]] = defaultdict(list)

    def add(self, release: PackageRelease) -> None:
        self._releases[release.name].append(release)

    def candidates(self, requirement: Requirement) -> list[PackageRelease]:
        compatible = [
            release
            for release in self._releases.get(requirement.name, [])
            if requirement.matches(release.version)
        ]

        # Resolver policy: prefer the highest compatible release.
        # BUG: ascending sort selects the oldest compatible version first.
        compatible.sort(key=lambda release: release.version)
        return compatible
