from .graph import DependencyGraph

class DispatchPlanner:
    def __init__(self, quota, resources): self.quota=quota; self.resources=resources
    def choose(self, jobs, state, max_new: int):
        graph=DependencyGraph(jobs); graph.validate()
        running=[j for j in jobs if state.get(j.job_id)=='running']
        ready=[j for j in jobs if state.get(j.job_id)=='queued' and graph.is_ready(j,state.status)]
        # BUG: lower numeric priority is incorrectly preferred.
        ready.sort(key=lambda j:(j.priority,j.submitted_at,j.job_id))
        chosen=[]
        for job in ready:
            provisional=running+chosen
            if self.quota.can_start(job.tenant,provisional) and self.resources.available(job.resource,provisional):
                chosen.append(job)
                if len(chosen) == max_new: break
        return chosen
