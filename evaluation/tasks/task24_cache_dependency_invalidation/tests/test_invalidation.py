from cachelayer.dependencies import DependencyIndex
from cachelayer.invalidator import CacheInvalidator
from cachelayer.store import CacheStore
from cachelayer.service import CachedQueryService

def setup(namespace='api'):
    store=CacheStore(); index=DependencyIndex(); inv=CacheInvalidator(store,index)
    return store,index,inv,CachedQueryService(namespace,store,index,inv)

def test_transitive_dependents_are_invalidated():
    store,index,inv,s=setup()
    s.put('/user/1',{'id':1},0,100)
    s.put('/team/7',[1],0,100,depends_on=['/user/1'])
    s.put('/dashboard','x',0,100,depends_on=['/team/7'])
    s.invalidate('/user/1')
    assert store.keys()==set()

def test_unrelated_entries_survive_invalidation():
    store,index,inv,s=setup(); s.put('/a',1,0,100); s.put('/b',2,0,100); s.invalidate('/a')
    assert s.get('/b',1)==2

def test_tag_invalidation_also_removes_derived_entries():
    store,index,inv,s=setup()
    s.put('/product/1',1,0,100,tags={'catalog'})
    s.put('/search',[1],0,100,depends_on=['/product/1'])
    inv.invalidate_tag('catalog')
    assert store.keys()==set()

def test_namespaces_do_not_collide_between_services():
    store=CacheStore(); index=DependencyIndex(); inv=CacheInvalidator(store,index)
    a=CachedQueryService('a',store,index,inv); b=CachedQueryService('b',store,index,inv)
    a.put('/same','A',0,100); b.put('/same','B',0,100)
    assert a.get('/same',1)=='A' and b.get('/same',1)=='B'

def test_query_variants_are_distinct():
    store,index,inv,s=setup(); s.put('/search','one',0,100,query='page=1'); s.put('/search','two',0,100,query='page=2')
    assert s.get('/search',1,'page=1')=='one' and s.get('/search',1,'page=2')=='two'
