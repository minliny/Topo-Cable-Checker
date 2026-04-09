from typing import Dict, Any, List
from abc import ABC, abstractmethod
from src.domain.result_model import IssueItem
from src.domain.fact_model import NormalizedDataset

class RuleExecutor(ABC):
    @abstractmethod
    def execute(self, rule_id: str, rule_def: Dict[str, Any], dataset: NormalizedDataset) -> List[IssueItem]:
        pass
