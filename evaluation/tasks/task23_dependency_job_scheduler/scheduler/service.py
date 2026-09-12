from .state import JobState
from .planner import DispatchPlanner

class SchedulerService:
    def __init__(self, jobs, planner: DispatchPlanner):
        self.jobs=list(jobs); self.planner=planner; self.state=JobState()
        for j in self.jobs: self.state.add(j.job_id)

    def dispatch(self, max_new=1):
        chosen=self.planner.choose(self.jobs,self.state,max_new)
        for job in chosen: self.state.mark_running(job.job_id)
        return [j.job_id for j in chosen]

    def finish(self, job_id, success=True):
        if success: self.state.mark_done(job_id)
        else: self.state.mark_failed(job_id)
