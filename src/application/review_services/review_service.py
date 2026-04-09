from src.infrastructure.repository import ResultRepository, TaskRepository
from src.domain.result_model import ReviewContext
from src.domain.task_model import TaskStatus

class ReviewService:
    def __init__(self):
        self.result_repo = ResultRepository()
        self.task_repo = TaskRepository()
        
    def review_issues(self, run_id: str, device_name: str) -> ReviewContext:
        issues = self.result_repo.get_issue_aggregate(run_id)
        
        ctx = ReviewContext(
            run_id=run_id,
            device_name=device_name,
            context_data={"device": device_name, "issues_count": len(issues.issues) if issues else 0}
        )
        self.result_repo.save_review(ctx)
        
        # Update task status if we can find it... (simplified)
        return ctx
