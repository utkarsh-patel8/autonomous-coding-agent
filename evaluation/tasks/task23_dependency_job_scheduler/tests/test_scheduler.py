from scheduler.models import Job
from scheduler.planner import DispatchPlanner
from scheduler.quota import TenantQuota
from scheduler.resources import ResourcePool
from scheduler.service import SchedulerService

def make(jobs,limits={'a':2,'b':2},caps={'cpu':2,'gpu':1}):
    return SchedulerService(jobs,DispatchPlanner(TenantQuota(limits),ResourcePool(caps)))

def test_job_waits_for_all_dependencies():
    jobs=[Job('a','a',1),Job('b','a',1),Job('c','b',10,frozenset({'a','b'}))]
    s=make(jobs); s.state.mark_done('a')
    assert 'c' not in s.dispatch(max_new=2)

def test_high_priority_jobs_are_dispatched_first():
    jobs=[Job('low','a',1,submitted_at=0),Job('high','b',9,submitted_at=1)]
    assert make(jobs).dispatch()==['high']

def test_submission_time_breaks_equal_priority_ties():
    jobs=[Job('later','a',5,submitted_at=20),Job('earlier','b',5,submitted_at=10)]
    assert make(jobs).dispatch()==['earlier']

def test_tenant_quota_applies_to_provisional_batch():
    jobs=[Job('a1','a',9),Job('a2','a',8),Job('b1','b',7)]
    s=make(jobs,limits={'a':1,'b':1},caps={'cpu':3})
    assert s.dispatch(max_new=3)==['a1','b1']

def test_resource_capacity_applies_across_batch():
    jobs=[Job('g1','a',9,resource='gpu'),Job('g2','b',8,resource='gpu'),Job('c','b',7,resource='cpu')]
    s=make(jobs,caps={'gpu':1,'cpu':1})
    assert s.dispatch(max_new=3)==['g1','c']

def test_dependent_job_runs_after_all_dependencies_finish():
    jobs=[Job('a','a',9),Job('b','b',8),Job('c','a',10,frozenset({'a','b'}))]
    s=make(jobs,caps={'cpu':2}); first=s.dispatch(max_new=2)
    assert first==['a','b']
    s.finish('a'); s.finish('b')
    assert s.dispatch()==['c']
