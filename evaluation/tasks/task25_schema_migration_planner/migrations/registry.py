from .models import Migration

class MigrationRegistry:
    def __init__(self,migrations: list[Migration]): self.migrations={m.migration_id:m for m in migrations}
    def pending(self,applied: set[str]) -> list[Migration]:
        # BUG: already-applied migrations are returned instead of excluded.
        return [m for mid,m in sorted(self.migrations.items()) if mid in applied]
