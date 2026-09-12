from migrations.executor import SchemaExecutor
from migrations.models import Column, Migration, Operation, TableSchema
from migrations.planner import MigrationPlanner

M=lambda mid,deps=(),ops=(): Migration(mid,frozenset(deps),tuple(ops))

def test_planner_skips_applied_and_keeps_pending_dependency_order():
    ms=[M('001'),M('002',{'001'}),M('003',{'002'}),M('004',{'001'})]
    plan=MigrationPlanner().plan(ms,{'001'})
    ids=[m.migration_id for m in plan]
    assert ids.index('002') < ids.index('003')
    assert set(ids)=={'002','003','004'}

def test_executor_returns_new_schema_without_mutating_input():
    original=TableSchema({'id':Column('id','int',False)})
    migration=M('001',ops=[Operation('add','name',Column('name','text',True))])
    updated=SchemaExecutor().apply(original,migration)
    assert set(original.columns)=={'id'}
    assert set(updated.columns)=={'id','name'}

def test_multi_migration_plan_can_be_applied_end_to_end():
    ms=[
      M('001',ops=[Operation('add','name',Column('name','text',True))]),
      M('002',{'001'},[Operation('add','age',Column('age','int',True))]),
      M('003',{'002'},[Operation('alter','age',Column('age','bigint',True))]),
    ]
    schema=TableSchema({'id':Column('id','int',False)})
    ex=SchemaExecutor()
    for migration in MigrationPlanner().plan(ms,set()): schema=ex.apply(schema,migration)
    assert schema.columns['age'].type=='bigint' and 'name' in schema.columns
