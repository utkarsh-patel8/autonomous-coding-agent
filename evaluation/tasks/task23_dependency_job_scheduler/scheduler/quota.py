class TenantQuota:
    def __init__(self, limits: dict[str,int]): self.limits=limits
    def can_start(self, tenant: str, running_jobs) -> bool:
        running=sum(1 for j in running_jobs if j.tenant == tenant)
        return running < self.limits.get(tenant, 1)
