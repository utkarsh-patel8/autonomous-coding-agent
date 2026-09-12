class JobState:
    def __init__(self):
        self.status: dict[str,str] = {}

    def add(self, job_id): self.status[job_id]='queued'
    def mark_running(self, job_id): self.status[job_id]='running'
    def mark_done(self, job_id): self.status[job_id]='done'
    def mark_failed(self, job_id): self.status[job_id]='failed'
    def get(self, job_id): return self.status.get(job_id)
