from .models import Operation, TableSchema

WIDENING={('int','bigint'),('float','double')}

def operation_is_backward_compatible(schema: TableSchema, op: Operation) -> bool:
    if op.kind=='add':
        return op.column is not None and op.column.nullable
    if op.kind=='drop': return False
    if op.kind=='alter':
        old=schema.columns[op.name]; new=op.column
        if new is None: return False
        if old.nullable and not new.nullable: return False
        return old.type==new.type or (old.type,new.type) in WIDENING
    raise ValueError(op.kind)

def migration_is_backward_compatible(schema, migration) -> bool:
    # BUG: every operation must be compatible, not merely any operation.
    return any(operation_is_backward_compatible(schema,op) for op in migration.operations)
