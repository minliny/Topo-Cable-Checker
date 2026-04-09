from src.infrastructure.repository import TaskRepository, BaselineRepository
from src.domain.task_model import CheckTask, TaskStatus
from src.crosscutting.ids.generator import generate_id
from src.crosscutting.time.clock import now
from src.crosscutting.errors.exceptions import TaskError

class TaskService:
    def __init__(self):
        self.task_repo = TaskRepository()
        self.baseline_repo = BaselineRepository()

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
