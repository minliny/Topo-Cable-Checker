from typing import Dict, Any, List
from src.domain.result_model import IssueItem
from src.domain.fact_model import NormalizedDataset
from src.crosscutting.ids.generator import generate_id
import re
import dataclasses

class RuleEngine:
    def execute(self, normalized_dataset: NormalizedDataset, rule_set: Dict[str, Any]) -> List[IssueItem]:
        """
        Takes normalized dataset containing Devices, Ports, Links objects,
        applies rule_set, and produces IssueItems.
        """
        issues = []
        
        # Iterate over rules
        for rule_id, rule_def in rule_set.items():
            target_type = rule_def.get("target_type") # "devices", "ports", "links"
            target_field = rule_def.get("field")
            rule_type = rule_def.get("type", "field_equals") # default
            expected_val = rule_def.get("expected")
            
            target_list = getattr(normalized_dataset, target_type, None)
            if target_list is None:
                continue
                
            for i, item in enumerate(target_list):
                actual_val = getattr(item, target_field, None)
                
                is_failed = False
                message = ""
                
                # 1. field_equals
                if rule_type == "field_equals":
                    if actual_val != expected_val:
                        is_failed = True
                        message = f"Rule {rule_id} ({rule_type}) failed on {target_field}: Expected '{expected_val}', got '{actual_val}'"
                
                # 2. regex_match
                elif rule_type == "regex_match":
                    if not actual_val or not re.match(str(expected_val), str(actual_val)):
                        is_failed = True
                        message = f"Rule {rule_id} ({rule_type}) failed on {target_field}: '{actual_val}' does not match regex '{expected_val}'"
                
                # 3. missing_value
                elif rule_type == "missing_value":
                    if actual_val is None or str(actual_val).strip() == "":
                        is_failed = True
                        message = f"Rule {rule_id} ({rule_type}) failed: Required field '{target_field}' is missing or empty"
                
                if is_failed:
                    issues.append(IssueItem(
                        issue_id=generate_id(),
                        message=message,
                        evidence={"rule_id": rule_id, "item_data": dataclasses.asdict(item)},
                        expected=expected_val,
                        actual=actual_val,
                        details={"target_field": target_field, "rule_type": rule_type, "target_type": target_type},
                        source_row=i + 1 # 1-based index within the normalized list
                    ))
                    
        return issues

rule_engine = RuleEngine()
