from src.domain.interfaces import IResultRepository, ITaskRepository
from src.application.normalization_services.normalization_service import NormalizationService
from src.domain.result_model import DeviceReviewContext
from src.crosscutting.errors.exceptions import TaskError
import dataclasses

class ReviewService:
    def __init__(self, result_repo: IResultRepository = None, task_repo: ITaskRepository = None):
        if result_repo is None or task_repo is None:
            from src.infrastructure.repository import ResultRepository, TaskRepository
            self.result_repo = result_repo or ResultRepository()
            self.task_repo = task_repo or TaskRepository()
        else:
            self.result_repo = result_repo
            self.task_repo = task_repo
        self.normalization_service = NormalizationService()
        
    def review_issues(self, run_id: str, device_name: str) -> DeviceReviewContext:
        # 1. Fetch Execution and Task to get Normalized Dataset
        execution = self.result_repo.get_run_execution(run_id)
        if not execution:
            raise TaskError(f"Run {run_id} not found.")
            
        task_id = execution.task_id
        rec_snapshot = self.result_repo.get_recognition(task_id)
        raw_data = rec_snapshot.recognized_data["row_data"]
        dataset, _ = self.normalization_service.normalize(raw_data)

        # 2. Filter Ports and Links related to device
        related_ports = [dataclasses.asdict(p) for p in dataset.ports if p.device_name == device_name]
        related_links = []
        connected_devices = set()
        
        for link in dataset.links:
            if link.src_device == device_name:
                related_links.append(dataclasses.asdict(link))
                connected_devices.add(link.dst_device)
            elif link.dst_device == device_name:
                related_links.append(dataclasses.asdict(link))
                connected_devices.add(link.src_device)
                
        # 3. Filter Issues related to device
        aggregate = self.result_repo.get_issue_aggregate(run_id)
        related_issues = []
        if aggregate:
            for issue in aggregate.issues:
                item_data = issue.evidence.get("item_data", {})
                if item_data.get("device_name") == device_name or item_data.get("src_device") == device_name or item_data.get("dst_device") == device_name:
                    related_issues.append(issue)
                    
        # 4. Build DeviceReviewContext
        ctx = DeviceReviewContext(
            run_id=run_id,
            device_name=device_name,
            related_ports=related_ports,
            connected_devices=list(connected_devices),
            related_links=related_links,
            related_issues=related_issues
        )
        self.result_repo.save_review(ctx)
        
        return ctx
