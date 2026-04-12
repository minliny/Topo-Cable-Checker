from src.domain.interfaces import ITaskRepository, IBaselineRepository, IResultRepository
from src.application.normalization_services.normalization_service import NormalizationService
from src.domain.task_model import TaskStatus
from src.domain.rule_engine.engine import rule_engine
from src.application.rule_engine_services.rule_engine_external_rule_assembler import RuleEngineExternalRuleAssembler
from src.domain.result_model import (
    RunExecutionSnapshot, RunSummaryOverview, IssueAggregateSnapshot, RunStatisticsSnapshot
)
from src.crosscutting.ids.generator import generate_id
from src.crosscutting.errors.exceptions import TaskError

class CheckRunService:
    def __init__(self, task_repo: ITaskRepository = None, baseline_repo: IBaselineRepository = None, result_repo: IResultRepository = None):
        if task_repo is None or baseline_repo is None or result_repo is None:
            from src.infrastructure.repository import TaskRepository, BaselineRepository, ResultRepository
            self.task_repo = task_repo or TaskRepository()
            self.baseline_repo = baseline_repo or BaselineRepository()
            self.result_repo = result_repo or ResultRepository()
        else:
            self.task_repo = task_repo
            self.baseline_repo = baseline_repo
            self.result_repo = result_repo
        self.normalization_service = NormalizationService()
        
    def run_checks(self, task_id: str, external_rule_file_path: str = None) -> str:
        task = self.task_repo.get_by_id(task_id)
        if not task or task.task_status != TaskStatus.ready_to_check:
            raise TaskError(f"Task {task_id} is not ready to check.")
            
        # 0. Assemble External Rules (Fail-fast if file path provided but invalid)
        external_compiled_rules = None
        if external_rule_file_path:
            try:
                external_compiled_rules = RuleEngineExternalRuleAssembler.assemble(external_rule_file_path)
            except Exception as e:
                # We fail the entire run intentionally if external rules cannot be loaded
                raise TaskError(f"Failed to assemble external rules from '{external_rule_file_path}': {e}")
                
        task.task_status = TaskStatus.checking
        self.task_repo.save(task)
        
        run_id = generate_id()
        task.latest_run_id = run_id
        
        # 1. Execution Snapshot
        execution_snapshot = RunExecutionSnapshot(run_id=run_id, task_id=task_id, status="running")
        self.result_repo.save_run_execution(execution_snapshot)
        
        # 2. Retrieve Recognized Data
        rec_snapshot = self.result_repo.get_recognition(task_id)
        if not rec_snapshot:
            raise TaskError("Recognition data not found for task.")
        raw_data = rec_snapshot.recognized_data["row_data"]
        
        # Load recognition issues
        from src.domain.result_model import IssueItem
        rec_issues_dicts = rec_snapshot.recognized_data.get("issues", [])
        rec_issues = [IssueItem(**d) for d in rec_issues_dicts]
        
        # 3. Normalize Data Pipeline
        normalized_dataset, norm_issues = self.normalization_service.normalize(raw_data)
        
        # 4. Statistics Layer
        device_types = {}
        for dev in normalized_dataset.devices:
            dt = dev.device_type or "Unknown"
            device_types[dt] = device_types.get(dt, 0) + 1

        stats_snapshot = RunStatisticsSnapshot(
            run_id=run_id,
            total_devices=len(normalized_dataset.devices),
            total_ports=len(normalized_dataset.ports),
            total_links=len(normalized_dataset.links),
            device_type_distribution=device_types
        )
        self.result_repo.save_statistics(stats_snapshot)

        # 5. Rule Engine Execution
        baseline = self.baseline_repo.get_by_id(task.baseline_id)
        engine_issues = rule_engine.execute(
            normalized_dataset, 
            baseline,
            external_compiled_rules=external_compiled_rules
        )
        
        # Combine all issues
        all_issues = rec_issues + norm_issues + engine_issues
        
        # 6. Aggregate Layer
        by_device = {}
        by_rule = {}
        by_severity = {}
        
        for issue in all_issues:
            item_data = issue.evidence.get("item_data", {})
            dev_name = item_data.get("device_name", "Unknown")
            rule_id = issue.evidence.get("rule_id", "Unknown")
            severity = issue.severity
            
            by_device[dev_name] = by_device.get(dev_name, 0) + 1
            by_rule[rule_id] = by_rule.get(rule_id, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
        aggregate = IssueAggregateSnapshot(
            run_id=run_id, 
            issues=all_issues,
            by_device=by_device,
            by_rule=by_rule,
            by_severity=by_severity
        )
        self.result_repo.save_issue_aggregate(aggregate)

        # 7. Summary
        summary = RunSummaryOverview(
            run_id=run_id, 
            summary=f"Analysis complete. {stats_snapshot.total_devices} devices, {stats_snapshot.total_ports} ports. Found {len(all_issues)} issues."
        )
        self.result_repo.save_summary(summary)
        
        # Finish
        task.task_status = TaskStatus.check_completed
        self.task_repo.save(task)
        
        execution_snapshot.status = "completed"
        self.result_repo.save_run_execution(execution_snapshot)
        
        return run_id
