from src.domain.interfaces import ITaskRepository, IBaselineRepository
from src.domain.task_model import CheckTask, TaskStatus
from src.crosscutting.ids.generator import generate_id
from src.crosscutting.time.clock import now
from src.crosscutting.errors.exceptions import TaskError

class TaskService:
    def __init__(self, task_repo: ITaskRepository = None, baseline_repo: IBaselineRepository = None):
        if task_repo is None or baseline_repo is None:
            from src.infrastructure.repository import TaskRepository, BaselineRepository
            self.task_repo = task_repo or TaskRepository()
            self.baseline_repo = baseline_repo or BaselineRepository()
        else:
            self.task_repo = task_repo
            self.baseline_repo = baseline_repo

    def create_task(self, baseline_id: str, file_path: str) -> str:
        baseline = self.baseline_repo.get_by_id(baseline_id)
        if not baseline:
            raise TaskError(f"Baseline {baseline_id} not found.")
            
        task = CheckTask(
            task_id=generate_id(),
            task_name=f"Task_{file_path}",
            source_file_ref=file_path,
            source_file_version="1.0",
            baseline_id=baseline.baseline_id,
            baseline_version=baseline.baseline_version,
            task_status=TaskStatus.data_attached, # draft -> data_attached in one go
            created_at=now()
        )
        self.task_repo.save(task)
        return task.task_id

    def get_task_status(self, task_id: str) -> str:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskError(f"Task {task_id} not found.")
        return task.task_status.value
