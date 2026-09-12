from dataclasses import dataclass, field

@dataclass(frozen=True)
class Column:
    name: str
    type: str
    nullable: bool = True

@dataclass
class TableSchema:
    columns: dict[str, Column] = field(default_factory=dict)

@dataclass(frozen=True)
class Operation:
    kind: str
    name: str
    column: Column | None = None

@dataclass(frozen=True)
class Migration:
    migration_id: str
    depends_on: frozenset[str]
    operations: tuple[Operation, ...]
