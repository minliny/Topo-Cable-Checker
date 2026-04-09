from src.infrastructure.repository import ResultRepository
from src.domain.result_model import RecheckDiffSnapshot

class RecheckService:
    def __init__(self):
        self.result_repo = ResultRepository()
        
    def generate_diff(self, task_id: str, prev_run_id: str, curr_run_id: str) -> RecheckDiffSnapshot:
        prev_issues = self.result_repo.get_issue_aggregate(prev_run_id)
        curr_issues = self.result_repo.get_issue_aggregate(curr_run_id)
        
        prev_cnt = len(prev_issues.issues) if prev_issues else 0
        curr_cnt = len(curr_issues.issues) if curr_issues else 0
        
        diff = RecheckDiffSnapshot(
            task_id=task_id,
            prev_run_id=prev_run_id,
            curr_run_id=curr_run_id,
            diff_data={"resolved": prev_cnt - curr_cnt, "new_issues": 0 if prev_cnt > curr_cnt else curr_cnt - prev_cnt}
        )
        self.result_repo.save_diff(diff)
        return diff
