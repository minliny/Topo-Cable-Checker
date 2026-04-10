from src.domain.interfaces import ITaskRepository, IResultRepository, IExcelReader
from src.domain.task_model import TaskStatus
from src.domain.result_model import RecognitionResultSnapshot
from src.crosscutting.errors.exceptions import TaskError
from typing import Dict, Any

class RecognitionService:
    def __init__(self, task_repo: ITaskRepository = None, result_repo: IResultRepository = None, excel_reader: IExcelReader = None):
        if task_repo is None or result_repo is None or excel_reader is None:
            from src.infrastructure.repository import TaskRepository, ResultRepository
            from src.infrastructure.excel_reader import ExcelReader
            self.task_repo = task_repo or TaskRepository()
            self.result_repo = result_repo or ResultRepository()
            self.excel_reader = excel_reader or ExcelReader()
        else:
            self.task_repo = task_repo
            self.result_repo = result_repo
            self.excel_reader = excel_reader
        
    def recognize_data(self, task_id: str) -> Dict[str, Any]:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskError(f"Task {task_id} not found.")
        
        if task.task_status != TaskStatus.data_attached:
            raise TaskError("Task must be in data_attached state.")
            
        # 1. Read real Excel file
        file_path = task.source_file_ref
        try:
            excel_data = self.excel_reader.read(file_path)
        except Exception as e:
            raise TaskError(f"Failed to read excel file {file_path}: {e}")

        # 2. Build snapshot
        snapshot = RecognitionResultSnapshot(
            task_id=task_id,
            recognized_data={
                "recognized_sheets": excel_data["sheets"],
                "header_mapping": excel_data["header_mapping"],
                "row_data": excel_data["row_data"],
                "warnings": []
            }
        )
        self.result_repo.save_recognition(snapshot)
        
        # 3. Transition state
        task.task_status = TaskStatus.recognized
        self.task_repo.save(task)
        
        return {
            "status": "recognized", 
            "task_id": task_id, 
            "sheets_found": len(excel_data["sheets"])
        }

    def confirm_recognition(self, task_id: str) -> Dict[str, Any]:
        task = self.task_repo.get_by_id(task_id)
        if task.task_status != TaskStatus.recognized:
            raise TaskError("Task must be in recognized state.")
            
        task.task_status = TaskStatus.pending_confirmation
        self.task_repo.save(task)
        
        # Normally wait for user, but we'll assume it's confirmed
        task.task_status = TaskStatus.ready_to_check
        self.task_repo.save(task)
        return {"status": "confirmed and ready_to_check", "task_id": task_id}
