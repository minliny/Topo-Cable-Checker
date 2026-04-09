from typing import Dict, Any, List
from src.domain.executors.base_executor import RuleExecutor
from src.domain.result_model import IssueItem
from src.crosscutting.ids.generator import generate_id
import dataclasses

class GroupConsistencyExecutor(RuleExecutor):
    def execute(self, rule_id: str, rule_def: Dict[str, Any], filtered_dataset: Dict[str, List[Any]], 
                parameter_profile: Dict[str, Any], threshold_profile: Dict[str, Any]) -> List[IssueItem]:
        issues = []
        
        target_type = rule_def.get("scope_selector", {}).get("target_type")
        
        # Resolve parameters either from rule_def or parameter_profile
        param_key = rule_def.get("parameter_key")
        if param_key and param_key in parameter_profile:
            group_key_field = parameter_profile[param_key].get("group_key")
            comparison_field = parameter_profile[param_key].get("comparison_field")
        else:
            group_key_field = rule_def.get("group_key")
            comparison_field = rule_def.get("comparison_field")
            
        severity = rule_def.get("severity", "medium")
        
        target_list = filtered_dataset.get(target_type, [])
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
                    issues.append(IssueItem(
                        issue_id=generate_id(),
                        message=f"Rule {rule_id} (group_consistency) failed: Group '{g_key}' has inconsistent '{comparison_field}'. Expected '{dominant_val}', got '{actual_val}'.",
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
