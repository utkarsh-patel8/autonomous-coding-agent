class ResourcePool:
    def __init__(self, capacities: dict[str,int]): self.capacities=capacities
    def available(self, resource: str, running_jobs) -> bool:
        used=sum(1 for j in running_jobs if j.resource == resource)
        return used < self.capacities.get(resource, 0)
