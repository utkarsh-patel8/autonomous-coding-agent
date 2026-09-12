from dataclasses import dataclass, field

@dataclass
class CacheEntry:
    value: object
    expires_at: float | None = None
    tags: set[str] = field(default_factory=set)
