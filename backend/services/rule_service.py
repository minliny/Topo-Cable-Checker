# backend/services/rule_service.py
from typing import Optional

from ..repositories.mock_repository import MockRepository
from ..models.baseline import RuleDefinition, RuleSet


class RuleService:
    def __init__(self):
        self.repo = MockRepository()

    def get_all_rules(self) -> list[RuleDefinition]:
        return self.repo.get_all_rules()

    def get_all_rulesets(self) -> list[RuleSet]:
        return self.repo.get_all_rulesets()

    def update_rule_override(self, rule_id: str, request: dict) -> bool:
        rule = self.repo.get_rule_by_id(rule_id)
        return rule is not None
