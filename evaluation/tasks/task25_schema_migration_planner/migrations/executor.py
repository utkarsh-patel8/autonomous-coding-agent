from copy import deepcopy
from .models import TableSchema

class SchemaExecutor:
    def apply(self,schema: TableSchema,migration):
        updated=deepcopy(schema)
        for op in migration.operations:
            if op.kind=='add':
                if op.name in updated.columns: raise ValueError(f'Column exists: {op.name}')
                updated.columns[op.name]=op.column
            elif op.kind=='drop':
                if op.name not in updated.columns: raise ValueError(f'Unknown column: {op.name}')
                del updated.columns[op.name]
            elif op.kind=='alter':
                if op.name not in updated.columns: raise ValueError(f'Unknown column: {op.name}')
                updated.columns[op.name]=op.column
            else: raise ValueError(op.kind)
        return updated
