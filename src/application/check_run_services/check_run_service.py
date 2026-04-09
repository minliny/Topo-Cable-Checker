from src.infrastructure.repository import TaskRepository, BaselineRepository, ResultRepository
from src.domain.task_model import TaskStatus
from src.domain.rule_engine import rule_engine
from src.domain.result_model import (
    RunExecutionSnapshot, RunSummaryOverview, IssueAggregateSnapshot
)
from src.crosscutting.ids.generator import generate_id
from src.crosscutting.errors.exceptions import TaskError
import json

class CheckRunService:
    def __init__(self):
        self.task_repo = TaskRepository()
        self.baseline_repo = BaselineRepository()
        self.result_repo = ResultRepository()
        
    def run_checks(self, task_id: str) -> str:
        task = self.task_repo.get_by_id(task_id)
        if not task or task.task_status != TaskStatus.ready_to_check:
            raise TaskError(f"Task {task_id} is not ready to check.")
            
        task.task_status = TaskStatus.checking
        self.task_repo.save(task)
        
        run_id = generate_id()
        task.latest_run_id = run_id
        
        # 1. Execution Snapshot
        execution_snapshot = RunExecutionSnapshot(run_id=run_id, task_id=task_id, status="running")
        self.result_repo.save_run_execution(execution_snapshot)
        
        # 2. Normalize (mocked dataset)
        normalized_dataset = [
            {"id": 1, "status": "active"},
            {"id": 2, "status": "inactive"},
            {"id": 3, "status": "pending"}
        ]
        
        # 3. Rule Engine Execution
        baseline = self.baseline_repo.get_by_id(task.baseline_id)
        issues = rule_engine.execute(normalized_dataset, baseline.rule_set)
        
        # 4. Result Pipeline: Aggregate & Summary
        aggregate = IssueAggregateSnapshot(run_id=run_id, issues=issues)
        self.result_repo.save_issue_aggregate(aggregate)
        
        summary = RunSummaryOverview(
            run_id=run_id, 
            summary=f"Checked {len(normalized_dataset)} rows, found {len(issues)} issues."
        )
        self.result_repo.save_summary(summary)
        
        # Finish
        task.task_status = TaskStatus.check_completed
        self.task_repo.save(task)
        
        execution_snapshot.status = "completed"
        self.result_repo.save_run_execution(execution_snapshot)
        
        return run_id
