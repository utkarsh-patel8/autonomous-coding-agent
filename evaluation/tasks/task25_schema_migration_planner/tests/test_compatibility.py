from migrations.compatibility import migration_is_backward_compatible, operation_is_backward_compatible
from migrations.models import Column, Migration, Operation, TableSchema

schema=TableSchema({'id':Column('id','int',False),'nickname':Column('nickname','text',True)})

def test_nullable_add_is_compatible_but_required_add_is_not():
    assert operation_is_backward_compatible(schema,Operation('add','age',Column('age','int',True)))
    assert not operation_is_backward_compatible(schema,Operation('add','age',Column('age','int',False)))

def test_widening_type_change_is_compatible():
    assert operation_is_backward_compatible(schema,Operation('alter','id',Column('id','bigint',False)))

def test_migration_requires_every_operation_to_be_compatible():
    m=Migration('x',frozenset(),(Operation('add','age',Column('age','int',True)),Operation('drop','nickname')))
    assert not migration_is_backward_compatible(schema,m)
