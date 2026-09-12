from cachelayer.keys import normalize_key
from cachelayer.store import CacheStore

def test_key_normalization_is_query_order_independent_and_namespaced():
    assert normalize_key('users','//v1/items/','b=2&a=1') == 'users:/v1/items?a=1&b=2'
    assert normalize_key('orders','/v1/items','a=1') != normalize_key('users','/v1/items','a=1')

def test_ttl_expires_at_boundary():
    s=CacheStore(); s.set('k','v',expires_at=10)
    assert s.get('k',9.999)=='v'
    assert s.get('k',10) is None
