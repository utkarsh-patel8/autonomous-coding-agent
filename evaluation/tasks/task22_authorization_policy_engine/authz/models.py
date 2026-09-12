from dataclasses import dataclass, field

@dataclass(frozen=True)
class User:
    user_id: str
    groups: frozenset[str] = field(default_factory=frozenset)

@dataclass(frozen=True)
class Resource:
    path: str
    owner_id: str | None = None

@dataclass(frozen=True)
class Rule:
    action: str
    pattern: str
    effect: str  # allow | deny

@dataclass(frozen=True)
class Role:
    name: str
    rules: tuple[Rule, ...]
