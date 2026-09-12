from .model import PackageRelease, Requirement
from .repository import PackageRepository


class ResolutionError(RuntimeError):
    pass


def resolve(
    repository: PackageRepository,
    requirements: list[Requirement],
) -> dict[str, PackageRelease]:
    selected: dict[str, PackageRelease] = {}

    def visit(requirement: Requirement) -> None:
        existing = selected.get(requirement.name)
        if existing is not None:
            if not requirement.matches(existing.version):
                raise ResolutionError(
                    f"selected {existing.name} {existing.version} does not satisfy a later constraint"
                )
            return

        candidates = repository.candidates(requirement)
        if not candidates:
            raise ResolutionError(f"no compatible release for {requirement.name}")

        release = candidates[0]
        selected[release.name] = release
        for dependency in release.dependencies:
            visit(dependency)

    for requirement in requirements:
        visit(requirement)

    return selected
