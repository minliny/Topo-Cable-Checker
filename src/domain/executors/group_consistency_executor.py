from typing import Dict, Any, List
from src.domain.executors.base_executor import RuleExecutor
from src.domain.result_model import IssueItem
from src.domain.compiled_rule_schema import CompiledRule
from src.crosscutting.ids.generator import generate_id
import dataclasses

class GroupConsistencyExecutor(RuleExecutor):
    def execute(self, compiled_rule: CompiledRule, dataset: Dict[str, List[Any]], context: Dict[str, Any]) -> List[IssueItem]:
        issues = []
        
        rule_id = compiled_rule.rule_id
        target_type = compiled_rule.target.type

        # Resolve parameters either from rule_def or parameter_profile
        param_key = compiled_rule.params.get("parameter_key")
        parameter_profile = context.get("parameter_profile", {})
        
        if param_key and param_key in parameter_profile:
            group_key_field = parameter_profile[param_key].get("group_key")
            comparison_field = parameter_profile[param_key].get("comparison_field")
        else:
            group_key_field = compiled_rule.params.get("group_key")
            comparison_field = compiled_rule.params.get("comparison_field")
            
        severity = compiled_rule.message.severity

        if not group_key_field or not comparison_field:
            msg = f"Rule {rule_id} (group_consistency) execution_error: missing required config (group_key/comparison_field)."
            issues.append(IssueItem(
                issue_id=generate_id(),
                message=msg,
                evidence={
                    "rule_id": rule_id,
                    "parameter_key": param_key,
                    "resolved_group_key": group_key_field,
                    "resolved_comparison_field": comparison_field,
                    "parameter_source": "parameter_profile" if param_key else "inline"
                },
                expected="valid group_consistency config",
                actual={
                    "group_key": group_key_field,
                    "comparison_field": comparison_field
                },
                details={"target_type": target_type},
                source_row=0,
                severity="critical",
                category="execution_error"
            ))
            return issues
        
        target_list = dataset.get(target_type, [])
        if not target_list:
            return issues
            
        groups = {}
        for i, item in enumerate(target_list):
            g_key = getattr(item, group_key_field, None)
            if g_key is None:
                continue
            if g_key not in groups:
                groups[g_key] = []
            groups[g_key].append((i, item))
            
        for g_key, items in groups.items():
            if len(items) <= 1:
                continue
                
            val_counts = {}
            for _, item in items:
                val = getattr(item, comparison_field, None)
                val_counts[val] = val_counts.get(val, 0) + 1
                
            if len(val_counts) <= 1:
                continue
                
            dominant_val = max(val_counts, key=val_counts.get)
            
            for i, item in items:
                actual_val = getattr(item, comparison_field, None)
                if actual_val != dominant_val:
                    msg = compiled_rule.message.template or f"Rule {rule_id} (group_consistency) failed: Group '{g_key}' has inconsistent '{comparison_field}'. Expected '{dominant_val}', got '{actual_val}'."
                    issues.append(IssueItem(
                        issue_id=generate_id(),
                        message=msg,
                        evidence={
                            "rule_id": rule_id, 
                            "group_key": g_key,
                            "comparison_field": comparison_field,
                            "item_data": dataclasses.asdict(item),
                            "parameter_source": "parameter_profile" if param_key else "inline"
                        },
                        expected=dominant_val,
                        actual=actual_val,
                        details={"target_type": target_type, "affected_items": [dataclasses.asdict(x[1]) for x in items]},
                        source_row=i + 1,
                        severity=severity,
                        category="group_consistency"
                    ))
        return issues
