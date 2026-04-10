from src.infrastructure.repository import TaskRepository
from src.domain.task_model import TaskStatus
repo = TaskRepository()
task = repo.get_by_id("5365aa3e-84fe-4eb1-b2fb-fa195e2af4fd")
task.task_status = TaskStatus.ready_to_check
repo.save(task)

from src.application.check_run_services.check_run_service import CheckRunService
svc = CheckRunService()
try:
    svc.run_checks("5365aa3e-84fe-4eb1-b2fb-fa195e2af4fd")
except Exception as e:
    import traceback
    traceback.print_exc()
