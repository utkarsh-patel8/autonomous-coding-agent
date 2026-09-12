import pytest
from scheduler.graph import DependencyGraph
from scheduler.models import Job

def test_cycle_is_rejected():
    with pytest.raises(ValueError,match='cycle'):
        DependencyGraph([Job('a','t',1,frozenset({'b'})),Job('b','t',1,frozenset({'a'}))]).validate()

def test_missing_dependency_is_rejected():
    with pytest.raises(ValueError,match='Missing'):
        DependencyGraph([Job('a','t',1,frozenset({'missing'}))]).validate()
