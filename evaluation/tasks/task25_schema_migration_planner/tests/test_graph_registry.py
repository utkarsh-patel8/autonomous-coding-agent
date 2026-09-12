import pytest
from migrations.graph import MigrationGraph
from migrations.models import Migration
from migrations.registry import MigrationRegistry

M=lambda mid,deps=(): Migration(mid,frozenset(deps),())

def test_topological_order_places_dependencies_first():
    ordered=MigrationGraph([M('003',{'002'}),M('001'),M('002',{'001'})]).ordered()
    assert [m.migration_id for m in ordered]==['001','002','003']

def test_cycle_is_rejected():
    with pytest.raises(ValueError,match='cycle'):
        MigrationGraph([M('a',{'b'}),M('b',{'a'})]).ordered()

def test_registry_returns_only_pending_migrations():
    r=MigrationRegistry([M('001'),M('002'),M('003')])
    assert [m.migration_id for m in r.pending({'001'})]==['002','003']
