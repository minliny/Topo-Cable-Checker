from typing import Dict, Any, List
from src.domain.executors.base_executor import RuleExecutor
from src.domain.result_model import IssueItem
from src.domain.compiled_rule_schema import CompiledRule
from src.crosscutting.ids.generator import generate_id
import dataclasses
import re

class SingleFactExecutor(RuleExecutor):
    def execute(self, compiled_rule: CompiledRule, dataset: Dict[str, List[Any]], context: Dict[str, Any]) -> List[IssueItem]:
        issues = []
        
        rule_id = compiled_rule.rule_id
        target_type = compiled_rule.target.type
        target_field = compiled_rule.params.get("field")
        rule_subtype = compiled_rule.rule_type
        expected_val = compiled_rule.params.get("expected")
        severity = compiled_rule.message.severity
        
        target_list = dataset.get(target_type, [])
            
        for i, item in enumerate(target_list):
            actual_val = getattr(item, target_field, None)
            is_failed = False
            message = ""
            
            if rule_subtype == "field_equals":
                if actual_val != expected_val:
                    is_failed = True
                    message = compiled_rule.message.template or f"Rule {rule_id} ({rule_subtype}) failed on {target_field}: Expected '{expected_val}', got '{actual_val}'"
            elif rule_subtype == "field_not_equals":
                if actual_val == expected_val:
                    is_failed = True
                    message = compiled_rule.message.template or f"Rule {rule_id} ({rule_subtype}) failed on {target_field}: Expected anything but '{expected_val}', got '{actual_val}'"
            elif rule_subtype == "regex_match":
                if not actual_val or not re.match(str(expected_val), str(actual_val)):
                    is_failed = True
                    message = compiled_rule.message.template or f"Rule {rule_id} ({rule_subtype}) failed on {target_field}: '{actual_val}' does not match regex '{expected_val}'"
            elif rule_subtype == "missing_value":
                if actual_val is None or str(actual_val).strip() == "":
                    is_failed = True
                    message = compiled_rule.message.template or f"Rule {rule_id} ({rule_subtype}) failed: Required field '{target_field}' is missing or empty"
            
            if is_failed:
                issues.append(IssueItem(
                    issue_id=generate_id(),
                    message=message,
                    evidence={"rule_id": rule_id, "item_data": dataclasses.asdict(item)},
                    expected=expected_val,
                    actual=actual_val,
                    details={"target_field": target_field, "rule_type": rule_subtype, "target_type": target_type},
                    source_row=i + 1,
                    severity=severity,
                    category="single_fact"
                ))
        return issues
