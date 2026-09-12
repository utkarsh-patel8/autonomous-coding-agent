from .models import Job

class DependencyGraph:
    def __init__(self, jobs: list[Job]):
        self.jobs={j.job_id:j for j in jobs}

    def is_ready(self, job: Job, statuses: dict[str,str]) -> bool:
        if not job.dependencies:
            return True
        # BUG: all dependencies must be done, not merely one of them.
        return any(statuses.get(dep) == 'done' for dep in job.dependencies)

    def validate(self):
        for job in self.jobs.values():
            missing=job.dependencies - self.jobs.keys()
            if missing:
                raise ValueError(f'Missing dependencies for {job.job_id}: {sorted(missing)}')
        visiting=set(); done=set()
        def dfs(node):
            if node in visiting: raise ValueError('Dependency cycle detected')
            if node in done: return
            visiting.add(node)
            for dep in self.jobs[node].dependencies: dfs(dep)
            visiting.remove(node); done.add(node)
        for node in self.jobs: dfs(node)
