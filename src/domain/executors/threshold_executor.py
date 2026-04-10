from typing import Dict, Any, List
from src.domain.executors.base_executor import RuleExecutor
from src.domain.result_model import IssueItem
from src.crosscutting.ids.generator import generate_id
from src.domain.rule_engine.execution_context import ExecutionContext
from src.domain.rule_engine.compiled_rule import CompiledRule
import dataclasses

class ThresholdExecutor(RuleExecutor):
    def execute(self, rule_id: str, compiled_rule: CompiledRule, filtered_dataset: Dict[str, List[Any]], 
                context: ExecutionContext) -> List[IssueItem]:
        issues = []

        target_type = compiled_rule.target.get("type")
        metric_type = compiled_rule.get("metric_type", "count") # count, distinct_count
        metric_field = compiled_rule.get("metric_field")
        
        # Read threshold definitions
        thresh_key = compiled_rule.get("threshold_key")
        if thresh_key and thresh_key in context.threshold_profile:
            t_def = context.threshold_profile[thresh_key]
            compare_operator = t_def.get("operator", "eq")
            expected_val = t_def.get("expected_value", t_def.get("value"))
            min_val = t_def.get("min_value")
            max_val = t_def.get("max_value")
        else:
            compare_operator = compiled_rule.get("operator", "eq")
            expected_val = compiled_rule.get("expected_value", compiled_rule.get("expected"))
            min_val = compiled_rule.get("min_value")
            max_val = compiled_rule.get("max_value")
            
        severity = compiled_rule.severity
        target_list = filtered_dataset.get(target_type, [])
        
        # 1. Calculate metric
        actual_value = 0
        if metric_type == "count":
            actual_value = len(target_list)
        elif metric_type == "distinct_count" and metric_field:
            distinct_vals = set()
            for item in target_list:
                val = getattr(item, metric_field, None)
                if val is not None:
                    distinct_vals.add(val)
            actual_value = len(distinct_vals)
            
        # 2. Evaluate
        is_failed = False
        message = ""
        expected_repr = str(expected_val)
        
        if compare_operator == "gt":
            if not (actual_value > expected_val): is_failed = True
            message = f"Must be > {expected_val}"
        elif compare_operator == "gte":
            if not (actual_value >= expected_val): is_failed = True
            message = f"Must be >= {expected_val}"
        elif compare_operator == "lt":
            if not (actual_value < expected_val): is_failed = True
            message = f"Must be < {expected_val}"
        elif compare_operator == "lte":
            if not (actual_value <= expected_val): is_failed = True
            message = f"Must be <= {expected_val}"
        elif compare_operator == "between":
            if not (min_val <= actual_value <= max_val): is_failed = True
            expected_repr = f"[{min_val}, {max_val}]"
            message = f"Must be between {min_val} and {max_val}"
        elif compare_operator == "outside":
            if min_val <= actual_value <= max_val: is_failed = True
            expected_repr = f"Outside [{min_val}, {max_val}]"
            message = f"Must be outside {min_val} and {max_val}"
        else: # eq
            if actual_value != expected_val: is_failed = True
            message = f"Must equal {expected_val}"
            
        # 3. Report
        if is_failed:
            evidence = {
                "rule_id": rule_id,
                "metric_key": f"{target_type}.{metric_type}",
                "metric_field": metric_field,
                "actual_value": actual_value,
                "compare_operator": compare_operator,
                "scope": rule_def.get("scope_selector", {}),
                "threshold_source": "threshold_profile" if thresh_key else "inline"
            }
            if compare_operator in ("between", "outside"):
                evidence["expected_range"] = expected_repr
            else:
                evidence["expected_value"] = expected_repr

            issues.append(IssueItem(
                issue_id=generate_id(),
                message=f"Rule {rule_id} (threshold) failed: Metric '{metric_type}' on '{target_type}' is {actual_value}. {message}.",
                evidence=evidence,
                expected=expected_repr,
                actual=actual_value,
                details={"target_type": target_type},
                source_row=0,
                severity=severity,
                category="threshold_check"
            ))

        return issues
