from dataclasses import dataclass, field
from .version import Version


@dataclass(frozen=True)
class Requirement:
    name: str
    min_version: Version
    max_exclusive: Version | None = None

    def matches(self, version: Version) -> bool:
        if version < self.min_version:
            return False
        if self.max_exclusive is not None and version >= self.max_exclusive:
            return False
        return True


@dataclass(frozen=True)
class PackageRelease:
    name: str
    version: Version
    dependencies: tuple[Requirement, ...] = field(default_factory=tuple)
