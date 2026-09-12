from .graph import MigrationGraph

class MigrationPlanner:
    def plan(self,migrations,applied: set[str]):
        pending=[m for m in migrations if m.migration_id not in applied]
        # Dependencies that are already applied are valid and should not need to be in pending graph.
        pending_ids={m.migration_id for m in pending}
        adjusted=[]
        from .models import Migration
        for m in pending:
            deps=frozenset(d for d in m.depends_on if d in pending_ids)
            adjusted.append(Migration(m.migration_id,deps,m.operations))
        return MigrationGraph(adjusted).ordered()
