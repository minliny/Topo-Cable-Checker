from typing import Dict, Any, List
from src.domain.result_model import IssueItem
from src.crosscutting.ids.generator import generate_id

class RuleEngine:
    def execute(self, normalized_dataset: List[Dict[str, Any]], rule_set: Dict[str, Any]) -> List[IssueItem]:
        """
        The only rule engine. Takes normalized dataset, applies rule_set, and produces IssueItems.
        """
        issues = []
        for i, row in enumerate(normalized_dataset):
            for rule_id, rule_def in rule_set.items():
                target_field = rule_def.get("field")
                expected_val = rule_def.get("expected")
                
                if target_field in row and row[target_field] != expected_val:
                    issues.append(IssueItem(
                        issue_id=generate_id(),
                        message=f"Rule {rule_id} failed: Expected {expected_val}, got {row[target_field]}",
                        evidence={"rule_id": rule_id, "row_data": row},
                        expected=expected_val,
                        actual=row[target_field],
                        details={"target_field": target_field},
                        source_row=i + 1
                    ))
        return issues

rule_engine = RuleEngine()
