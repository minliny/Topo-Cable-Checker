from src.domain.interfaces import IResultRepository
from src.domain.result_model import RunSummaryOverview, IssueAggregateSnapshot, RunStatisticsSnapshot

class ResultQueryService:
    def __init__(self, result_repo: IResultRepository):
        self.result_repo = result_repo
        
    def get_summary(self, run_id: str) -> RunSummaryOverview:
        return self.result_repo.get_summary(run_id)
        
    def get_issues(self, run_id: str) -> IssueAggregateSnapshot:
        return self.result_repo.get_issue_aggregate(run_id)

    def get_statistics(self, run_id: str) -> RunStatisticsSnapshot:
        return self.result_repo.get_statistics(run_id)
