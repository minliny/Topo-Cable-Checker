from enum import Enum
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

class TaskStatus(Enum):
    draft = "draft"
    data_attached = "data_attached"
    recognized = "recognized"
    pending_confirmation = "pending_confirmation"
    ready_to_check = "ready_to_check"
    checking = "checking"
    check_completed = "check_completed"
    reviewing = "reviewing"
    rechecking = "rechecking"
    archived = "archived"

@dataclass
class CheckTask:
    task_id: str
    task_name: str
    source_file_ref: str
    source_file_version: str
    baseline_id: str
    baseline_version: str
    task_status: TaskStatus
    created_at: datetime
    latest_run_id: Optional[str] = None
    parent_task_id: Optional[str] = None

