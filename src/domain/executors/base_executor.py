from abc import ABC, abstractmethod
from typing import Dict, Any, List
from src.domain.result_model import IssueItem
from src.domain.compiled_rule_schema import CompiledRule

class RuleExecutor(ABC):
    @abstractmethod
    def execute(self, compiled_rule: CompiledRule, dataset: Dict[str, List[Any]], context: Dict[str, Any]) -> List[IssueItem]:
        """
        Executes a compiled rule against a filtered dataset.
        `dataset` is a dict where keys are target_types (devices, ports, links)
        and values are the filtered list of Fact objects based on target.filter.
        `context` contains 'parameter_profile' and 'threshold_profile'.
        """
        pass
