from typing import Dict, Any, List
from abc import ABC, abstractmethod
from src.domain.result_model import IssueItem

class RuleExecutor(ABC):
    @abstractmethod
    def execute(self, rule_id: str, rule_def: Dict[str, Any], filtered_dataset: Dict[str, List[Any]], 
                parameter_profile: Dict[str, Any], threshold_profile: Dict[str, Any]) -> List[IssueItem]:
        """
        Executes a rule against a filtered dataset.
        filtered_dataset is a dict where keys are target_types (devices, ports, links)
        and values are the filtered list of Fact objects based on scope_selector.
        """
        pass
