class MigrationGraph:
    def __init__(self,migrations): self.migrations={m.migration_id:m for m in migrations}
    def ordered(self):
        for m in self.migrations.values():
            missing=m.depends_on-self.migrations.keys()
            if missing: raise ValueError(f'Missing dependency: {sorted(missing)}')
        visiting=set(); done=set(); result=[]
        def visit(mid):
            if mid in visiting: raise ValueError('Migration cycle detected')
            if mid in done: return
            visiting.add(mid)
            for dep in sorted(self.migrations[mid].depends_on): visit(dep)
            visiting.remove(mid); done.add(mid); result.append(self.migrations[mid])
        for mid in sorted(self.migrations): visit(mid)
        # BUG: dependencies are already before dependents; reversing breaks order.
        return list(reversed(result))
