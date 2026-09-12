from dataclasses import dataclass, field

@dataclass(frozen=True)
class Job:
    job_id: str
    tenant: str
    priority: int
    dependencies: frozenset[str] = field(default_factory=frozenset)
    resource: str = 'cpu'
    submitted_at: int = 0
