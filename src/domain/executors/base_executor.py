from abc import ABC, abstractmethod
from typing import Dict, Any, List
from src.domain.result_model import IssueItem
from src.domain.rule_engine.execution_context import ExecutionContext
from src.domain.rule_engine.compiled_rule import CompiledRule

class RuleExecutor(ABC):
    @abstractmethod
    def execute(self, rule_id: str, compiled_rule: CompiledRule, filtered_dataset: Dict[str, List[Any]], 
                context: ExecutionContext) -> List[IssueItem]:
        """
        Executes a rule against a filtered dataset.
        filtered_dataset is a dict where keys are target_types (devices, ports, links)
        and values are the filtered list of Fact objects based on scope_selector.
        """
        pass
