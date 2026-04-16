from fastapi import Depends
from src.infrastructure.repository import BaselineRepository, TaskRepository, ResultRepository, FileStorage
from src.infrastructure.excel_reader import ExcelReader
from src.application.baseline_services.baseline_service import BaselineService
from src.application.rule_editor_services.rule_baseline_history_service import RuleBaselineHistoryService
from src.application.rule_editor_services.rule_draft_save_service import RuleDraftSaveService
from src.application.task_services.task_service import TaskService
from src.application.recognition_services.recognition_service import RecognitionService
from src.application.check_run_services.check_run_service import CheckRunService
from src.application.review_services.review_service import ReviewService
from src.application.export_services.export_service import ExportService
from src.application.result_query_services.result_query_service import ResultQueryService

# Global repository instances
_baseline_repo = BaselineRepository()
_task_repo = TaskRepository()
_result_repo = ResultRepository()
_excel_reader = ExcelReader()
_file_storage = FileStorage()

def get_baseline_repository() -> BaselineRepository:
    return _baseline_repo

def get_task_repository() -> TaskRepository:
    return _task_repo

def get_result_repository() -> ResultRepository:
    return _result_repo

def get_excel_reader() -> ExcelReader:
    return _excel_reader

def get_file_storage() -> FileStorage:
    return _file_storage

def get_baseline_service(repo: BaselineRepository = Depends(get_baseline_repository)) -> BaselineService:
    return BaselineService(repo=repo)

def get_history_service(repo: BaselineRepository = Depends(get_baseline_repository)) -> RuleBaselineHistoryService:
    return RuleBaselineHistoryService(repo=repo)

def get_draft_save_service(repo: BaselineRepository = Depends(get_baseline_repository)) -> RuleDraftSaveService:
    return RuleDraftSaveService(repo=repo)

def get_task_service(task_repo: TaskRepository = Depends(get_task_repository), baseline_repo: BaselineRepository = Depends(get_baseline_repository)) -> TaskService:
    return TaskService(task_repo=task_repo, baseline_repo=baseline_repo)

def get_recognition_service(task_repo: TaskRepository = Depends(get_task_repository), result_repo: ResultRepository = Depends(get_result_repository), excel_reader: ExcelReader = Depends(get_excel_reader)) -> RecognitionService:
    return RecognitionService(task_repo=task_repo, result_repo=result_repo, excel_reader=excel_reader)

def get_check_run_service(task_repo: TaskRepository = Depends(get_task_repository), baseline_repo: BaselineRepository = Depends(get_baseline_repository), result_repo: ResultRepository = Depends(get_result_repository)) -> CheckRunService:
    return CheckRunService(task_repo=task_repo, baseline_repo=baseline_repo, result_repo=result_repo)

def get_review_service(result_repo: ResultRepository = Depends(get_result_repository), task_repo: TaskRepository = Depends(get_task_repository)) -> ReviewService:
    return ReviewService(result_repo=result_repo, task_repo=task_repo)

def get_export_service(result_repo: ResultRepository = Depends(get_result_repository), file_storage: FileStorage = Depends(get_file_storage)) -> ExportService:
    return ExportService(result_repo=result_repo, file_storage=file_storage)

def get_result_query_service(result_repo: ResultRepository = Depends(get_result_repository)) -> ResultQueryService:
    return ResultQueryService(result_repo=result_repo)
