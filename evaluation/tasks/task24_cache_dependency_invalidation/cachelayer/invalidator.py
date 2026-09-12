class CacheInvalidator:
    def __init__(self,store,index): self.store=store; self.index=index
    def invalidate(self,key: str):
        # BUG: only direct dependents are removed; transitive dependents survive.
        for dep in self.index.dependents_of(key):
            self.store.delete(dep)
        self.store.delete(key)
    def invalidate_tag(self,tag: str):
        for key in self.store.keys_with_tag(tag):
            self.invalidate(key)
