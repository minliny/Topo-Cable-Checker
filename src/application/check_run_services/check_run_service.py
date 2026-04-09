from src.infrastructure.repository import TaskRepository, BaselineRepository, ResultRepository
from src.application.normalization_services.normalization_service import NormalizationService
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
        self.normalization_service = NormalizationService()
        
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
        
        # 2. Retrieve Recognized Data (Raw Excel)
        rec_snapshot = self.result_repo.get_recognition(task_id)
        if not rec_snapshot:
            raise TaskError("Recognition data not found for task.")
        raw_data = rec_snapshot.recognized_data["row_data"]
        
        # 3. Normalize Data Pipeline
        normalized_dataset = self.normalization_service.normalize(raw_data)
        
        # 4. Rule Engine Execution
        baseline = self.baseline_repo.get_by_id(task.baseline_id)
        issues = rule_engine.execute(normalized_dataset, baseline.rule_set)
        
        # 5. Result Pipeline: Aggregate & Summary
        aggregate = IssueAggregateSnapshot(run_id=run_id, issues=issues)
        self.result_repo.save_issue_aggregate(aggregate)
        
        summary = RunSummaryOverview(
            run_id=run_id, 
            summary=f"Normalized dataset contains {len(normalized_dataset['devices'])} devices, {len(normalized_dataset['ports'])} ports, {len(normalized_dataset['links'])} links. Found {len(issues)} issues."
        )
        self.result_repo.save_summary(summary)
        
        # Finish
        task.task_status = TaskStatus.check_completed
        self.task_repo.save(task)
        
        execution_snapshot.status = "completed"
        self.result_repo.save_run_execution(execution_snapshot)
        
        return run_id
