from resolver.model import PackageRelease, Requirement
from resolver.planner import installation_order
from resolver.repository import PackageRepository
from resolver.solver import resolve
from resolver.version import Version


V = Version.parse


def release(name, version, *dependencies):
    return PackageRelease(name, V(version), tuple(dependencies))


def req(name, minimum, maximum=None):
    return Requirement(name, V(minimum), V(maximum) if maximum else None)


def test_repository_prefers_highest_compatible_release():
    repo = PackageRepository()
    repo.add(release("util", "1.2.0"))
    repo.add(release("util", "1.8.0"))
    repo.add(release("util", "2.0.0"))

    candidates = repo.candidates(req("util", "1.0.0", "2.0.0"))
    assert [str(item.version) for item in candidates] == ["1.8.0", "1.2.0"]


def test_resolver_chooses_highest_release_and_transitive_dependencies():
    repo = PackageRepository()
    repo.add(release("core", "1.0.0"))
    repo.add(release("core", "1.4.0"))
    repo.add(release("api", "2.0.0", req("core", "1.0.0", "2.0.0")))

    selected = resolve(repo, [req("api", "2.0.0")])

    assert str(selected["api"].version) == "2.0.0"
    assert str(selected["core"].version) == "1.4.0"


def test_installation_order_places_transitive_dependencies_first():
    selected = {
        "app": release("app", "1.0.0", req("api", "1.0.0"), req("log", "1.0.0")),
        "api": release("api", "1.0.0", req("core", "1.0.0")),
        "core": release("core", "1.0.0"),
        "log": release("log", "1.0.0"),
    }

    order = installation_order(selected)

    assert order.index("core") < order.index("api") < order.index("app")
    assert order.index("log") < order.index("app")


def test_installation_order_is_deterministic_for_independent_packages():
    selected = {
        "zeta": release("zeta", "1.0.0"),
        "alpha": release("alpha", "1.0.0"),
        "middle": release("middle", "1.0.0"),
    }
    assert installation_order(selected) == ["alpha", "middle", "zeta"]


def test_constraints_exclude_upper_bound():
    repo = PackageRepository()
    repo.add(release("db", "2.9.0"))
    repo.add(release("db", "3.0.0"))
    selected = resolve(repo, [req("db", "2.0.0", "3.0.0")])
    assert str(selected["db"].version) == "2.9.0"
