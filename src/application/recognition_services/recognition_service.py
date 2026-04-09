from src.infrastructure.repository import TaskRepository
from src.domain.task_model import TaskStatus
from src.crosscutting.errors.exceptions import TaskError

class RecognitionService:
    def __init__(self):
        self.task_repo = TaskRepository()
        
    def recognize_data(self, task_id: str):
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskError(f"Task {task_id} not found.")
        
        # Real mock of recognition logic
        if task.task_status != TaskStatus.data_attached:
            raise TaskError("Task must be in data_attached state.")
            
        # Transition state
        task.task_status = TaskStatus.recognized
        self.task_repo.save(task)
        return {"status": "recognized", "task_id": task_id}

    def confirm_recognition(self, task_id: str):
        task = self.task_repo.get_by_id(task_id)
        if task.task_status != TaskStatus.recognized:
            raise TaskError("Task must be in recognized state.")
            
        task.task_status = TaskStatus.pending_confirmation
        self.task_repo.save(task)
        
        # Normally wait for user, but we'll assume it's confirmed
        task.task_status = TaskStatus.ready_to_check
        self.task_repo.save(task)
        return {"status": "confirmed and ready_to_check", "task_id": task_id}
