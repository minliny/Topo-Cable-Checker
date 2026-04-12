from src.infrastructure.repository import BaselineRepository
from src.application.baseline_services.baseline_service import BaselineService
from src.application.rule_editor_services.rule_baseline_history_service import RuleBaselineHistoryService
from src.application.rule_editor_services.rule_draft_save_service import RuleDraftSaveService

# Dependency Injection Container for the API Shell
# For this minimum viable integration, we reuse the existing file-based repository.

baseline_repo = BaselineRepository()
baseline_service = BaselineService(repo=baseline_repo)
rule_baseline_history_service = RuleBaselineHistoryService(repo=baseline_repo)
rule_draft_save_service = RuleDraftSaveService(repo=baseline_repo)

def get_baseline_service() -> BaselineService:
    return baseline_service

def get_history_service() -> RuleBaselineHistoryService:
    return rule_baseline_history_service

def get_baseline_repo() -> BaselineRepository:
    return baseline_repo

def get_draft_save_service() -> RuleDraftSaveService:
    return rule_draft_save_service
