from typing import Dict, Any, List
from src.domain.result_model import IssueItem
from src.domain.fact_model import NormalizedDataset
from src.domain.executors.single_fact_executor import SingleFactExecutor
from src.domain.executors.group_consistency_executor import GroupConsistencyExecutor
from src.domain.executors.topology_executor import TopologyExecutor
from src.domain.executors.threshold_executor import ThresholdExecutor
from src.crosscutting.logging.logger import get_logger

logger = get_logger(__name__)

class RuleEngine:
    def __init__(self):
        self.executors = {
            "single_fact": SingleFactExecutor(),
            "group_consistency": GroupConsistencyExecutor(),
            "topology": TopologyExecutor(),
            "threshold": ThresholdExecutor()
        }

    def execute(self, normalized_dataset: NormalizedDataset, rule_set: Dict[str, Any]) -> List[IssueItem]:
        """
        Dispatches rules to appropriate executors based on rule configuration.
        """
        all_issues = []
        
        for rule_id, rule_def in rule_set.items():
            rule_executor_type = rule_def.get("executor", "single_fact")
            executor = self.executors.get(rule_executor_type)
            
            if executor:
                try:
                    issues = executor.execute(rule_id, rule_def, normalized_dataset)
                    all_issues.extend(issues)
                except Exception as e:
                    logger.error(f"Error executing rule {rule_id}: {e}")
            else:
                logger.warning(f"No executor found for rule type: {rule_executor_type}")
                
        return all_issues

rule_engine = RuleEngine()
