from collections import defaultdict

class DependencyIndex:
    def __init__(self): self._dependents=defaultdict(set)
    def add_dependency(self, derived_key: str, source_key: str):
        self._dependents[source_key].add(derived_key)
    def dependents_of(self,key): return set(self._dependents.get(key,()))
