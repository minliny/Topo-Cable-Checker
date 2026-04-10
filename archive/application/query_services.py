from typing import List, Dict, Any, Optional
from src.domain.interfaces import ITaskRepository, IResultRepository
from src.application.dto_models import (
    TaskSummaryDTO, RecognitionSummaryDTO, RunOverviewDTO, 
    IssueListItemDTO, DeviceReviewDTO, RecheckDiffDTO, ExportArtifactDTO, IssueListResultDTO
)

class QueryService:
    def __init__(self, task_repo: ITaskRepository = None, result_repo: IResultRepository = None):
        if task_repo is None or result_repo is None:
            # Fallback for backward compatibility if not injected
            from src.infrastructure.repository import TaskRepository, ResultRepository
            self.task_repo = task_repo or TaskRepository()
            self.result_repo = result_repo or ResultRepository()
        else:
            self.task_repo = task_repo
            self.result_repo = result_repo

    def get_task_summary(self, task_id: str) -> Optional[TaskSummaryDTO]:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            return None
        return TaskSummaryDTO(
            task_id=task.task_id,
            task_name=task.task_name,
            task_status=task.task_status.value,
            baseline_version=f"{task.baseline_id}:{task.baseline_version}",
            latest_run_id=task.latest_run_id,
            created_at=task.created_at.isoformat()
        )

    def get_task_list(self) -> List[TaskSummaryDTO]:
        # For UI demo: retrieve all tasks from repository
        import json, os
        from src.crosscutting.config.settings import settings
        path = os.path.join(settings.BASE_DIR, "data", "tasks.json")
        tasks = []
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
            for t_id in data:
                tasks.append(self.get_task_summary(t_id))
        return tasks

    def get_recognition_summary(self, task_id: str) -> Optional[RecognitionSummaryDTO]:
        rec = self.result_repo.get_recognition(task_id)
        if not rec:
            return None
        
        task = self.task_repo.get_by_id(task_id)
        status = "pending"
        if task and task.task_status.value in ["recognized", "pending_confirmation", "ready_to_check", "checking", "check_completed"]:
            status = "confirmed" if task.task_status.value != "recognized" else "pending"

        return RecognitionSummaryDTO(
            recognition_id=task_id, # using task_id as 1:1 mapping
            recognized_sheets=rec.recognized_data.get("recognized_sheets", []),
            header_mapping_summary=rec.recognized_data.get("header_mapping", {}),
            warnings=rec.recognized_data.get("warnings", []),
            errors=[],
            confirmation_status=status
        )

    def get_run_overview(self, run_id: str) -> Optional[RunOverviewDTO]:
        agg = self.result_repo.get_issue_aggregate(run_id)
        summary = self.result_repo.get_summary(run_id)
        if not agg or not summary:
            return None

        total_issues = len(agg.issues)
        err_count = agg.by_severity.get("error", 0)
        warn_count = agg.by_severity.get("warning", 0)
        info_count = agg.by_severity.get("info", 0) + agg.by_severity.get("medium", 0) # medium mapped to info/medium
        
        overall_risk = "High" if err_count > 0 else ("Medium" if warn_count > 0 else "Low")
        if total_issues == 0:
            overall_risk = "None"

        return RunOverviewDTO(
            run_id=run_id,
            overall_passed=(total_issues == 0),
            overall_risk_level=overall_risk,
            total_issue_count=total_issues,
            error_count=err_count,
            warning_count=warn_count,
            info_count=info_count,
            affected_device_count=len(agg.by_device.keys()),
            summary_message=summary.summary
        )

    def list_issue_items(self, run_id: str, filters: Dict[str, Any] = None) -> IssueListResultDTO:
        agg = self.result_repo.get_issue_aggregate(run_id)
        if not agg:
            return IssueListResultDTO([], 0, 0)
        
        before_count = len(agg.issues)
        filters = filters or {}
        dtos = []
        
        for issue in agg.issues:
            item_data = issue.evidence.get("item_data", {})
            dev_name = item_data.get("device_name") or item_data.get("src_device") or ""
            rule_id = issue.evidence.get("rule_id", "")
            
            # Apply filters
            if "severity" in filters and filters["severity"] and issue.severity != filters["severity"]:
                continue
            if "rule_id" in filters and filters["rule_id"] and rule_id != filters["rule_id"]:
                continue
            if "device_name" in filters and filters["device_name"] and dev_name != filters["device_name"]:
                continue
                
            dtos.append(IssueListItemDTO(
                issue_id=issue.issue_id,
                severity=issue.severity,
                rule_id=rule_id,
                rule_name=rule_id, # placeholder for name
                device_name=dev_name,
                port_name=item_data.get("port_name") or item_data.get("src_port") or "",
                message=issue.message,
                issue_status="Open",
                category=issue.category
            ))
            
        return IssueListResultDTO(items=dtos, before_count=before_count, after_count=len(dtos))

    def get_device_review(self, run_id: str, device_name: str) -> Optional[DeviceReviewDTO]:
        review = self.result_repo.get_review(run_id, device_name)
        if not review:
            return None
        
        issue_dtos = []
        for issue in review.related_issues:
            item_data = issue.evidence.get("item_data", {})
            issue_dtos.append(IssueListItemDTO(
                issue_id=issue.issue_id,
                severity=issue.severity,
                rule_id=issue.evidence.get("rule_id", ""),
                rule_name=issue.evidence.get("rule_id", ""),
                device_name=item_data.get("device_name") or item_data.get("src_device") or "",
                port_name=item_data.get("port_name") or item_data.get("src_port") or "",
                message=issue.message,
                issue_status="Open",
                category=issue.category
            ))

        return DeviceReviewDTO(
            device_name=review.device_name,
            related_ports=review.related_ports,
            connected_devices=review.connected_devices,
            related_links=review.related_links,
            related_issues=issue_dtos
        )

    def get_recheck_diff(self, diff_id: str) -> Optional[RecheckDiffDTO]:
        # Assume diff_id is "prevRunId_currRunId"
        parts = diff_id.split("_")
        if len(parts) != 2:
            return None
        diff = self.result_repo.get_diff(parts[0], parts[1])
        if not diff:
            return None

        return RecheckDiffDTO(
            diff_id=diff_id,
            new_issue_count=diff.diff_data.get("new", 0),
            resolved_issue_count=diff.diff_data.get("resolved", 0),
            persistent_issue_count=diff.diff_data.get("persistent", 0),
            changed_issue_count=diff.diff_data.get("changed", 0),
            risk_trend_summary=diff.risk_trend
        )

    def list_export_artifacts(self, run_id: str) -> List[ExportArtifactDTO]:
        exports = self.result_repo.get_exports(run_id)
        dtos = []
        for e in exports:
            dtos.append(ExportArtifactDTO(
                run_id=e.run_id,
                format=e.format,
                filename=f"export_{e.run_id}.{e.format}",
                download_url=f"/download/{e.run_id}/{e.format}"
            ))
        return dtos

    def get_export_artifact(self, run_id: str, fmt: str) -> Optional[ExportArtifactDTO]:
        exports = self.list_export_artifacts(run_id)
        for e in exports:
            if e.format == fmt:
                return e
        return None
