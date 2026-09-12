from .models import CacheEntry

class CacheStore:
    def __init__(self): self._entries={}
    def set(self,key,value,expires_at=None,tags=()): self._entries[key]=CacheEntry(value,expires_at,set(tags))
    def get(self,key,now):
        entry=self._entries.get(key)
        if entry is None: return None
        # BUG: an entry expires exactly at expires_at as well.
        if entry.expires_at is not None and now > entry.expires_at:
            self._entries.pop(key,None); return None
        return entry.value
    def delete(self,key): self._entries.pop(key,None)
    def keys(self): return set(self._entries)
    def keys_with_tag(self,tag): return {k for k,v in self._entries.items() if tag in v.tags}
