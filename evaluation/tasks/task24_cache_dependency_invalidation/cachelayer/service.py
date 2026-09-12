from .keys import normalize_key

class CachedQueryService:
    def __init__(self,namespace,store,index,invalidator):
        self.namespace=namespace; self.store=store; self.index=index; self.invalidator=invalidator
    def key(self,path,query=''): return normalize_key(self.namespace,path,query)
    def put(self,path,value,now,ttl,query='',tags=(),depends_on=()):
        key=self.key(path,query)
        self.store.set(key,value,now+ttl if ttl is not None else None,tags)
        for source_path in depends_on:
            self.index.add_dependency(key,self.key(source_path))
        return key
    def get(self,path,now,query=''): return self.store.get(self.key(path,query),now)
    def invalidate(self,path,query=''): self.invalidator.invalidate(self.key(path,query))
