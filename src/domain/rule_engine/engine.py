from typing import Dict, Any, List
from src.domain.result_model import IssueItem
from src.domain.fact_model import NormalizedDataset
from src.domain.executors.single_fact_executor import SingleFactExecutor
from src.domain.executors.group_consistency_executor import GroupConsistencyExecutor
from src.domain.executors.topology_executor import TopologyExecutor
from src.domain.executors.threshold_executor import ThresholdExecutor
from src.crosscutting.logging.logger import get_logger
from src.domain.baseline_model import BaselineProfile
from src.domain.rule_compiler import RuleCompiler
from src.domain.rule_engine.execution_context import ExecutionContext
from src.domain.rule_engine.compiled_rule import RuleValidationError

logger = get_logger(__name__)

class RuleEngine:
    def __init__(self):
        self.executors = {
            "single_fact": SingleFactExecutor(),
            "group_consistency": GroupConsistencyExecutor(),
            "topology": TopologyExecutor(),
            "threshold": ThresholdExecutor()
        }

    def _apply_scope(self, dataset: NormalizedDataset, scope_def: Dict[str, Any]) -> Dict[str, List[Any]]:
        """
        Filters the dataset based on the scope_selector.
        scope_def examples:
        {"target_type": "devices"} -> all devices
        {"target_type": "devices", "device_type": "Switch"} -> only switch devices
        {"target_type": "links", "source_sheet": "Links_v2"} -> specific links
        """
        filtered_dataset = {}
        
        for t_type in ["devices", "ports", "links"]:
            target_list = getattr(dataset, t_type, [])
            # 1. Filter by target_type
            if scope_def and "target_type" in scope_def:
                if t_type != scope_def["target_type"]:
                    continue
                    
            # 2. Filter individual facts by attribute matching
            filtered_facts = []
            for item in target_list:
                match = True
                for s_key, s_val in scope_def.items():
                    if s_key == "target_type":
                        continue
                    
                    if s_key == "_exists":
                        # s_val is a list of fields that must exist
                        for exist_field in s_val:
                            val = getattr(item, exist_field, None)
                            if val is None or str(val).strip() == "":
                                match = False
                                break
                        if not match:
                            break
                        continue

                    actual_val = getattr(item, s_key, None)
                    if actual_val != s_val:
                        match = False
                        break
                if match:
                    filtered_facts.append(item)
                    
            if filtered_facts:
                filtered_dataset[t_type] = filtered_facts
                
        return filtered_dataset

    def execute(self, normalized_dataset: NormalizedDataset, baseline: BaselineProfile) -> List[IssueItem]:
        all_issues = []
        rule_set = getattr(baseline, "rule_set", baseline.get("rule_set", {})) if isinstance(baseline, dict) else baseline.rule_set
        parameter_profile = getattr(baseline, "parameter_profile", baseline.get("parameter_profile", {})) if isinstance(baseline, dict) else baseline.parameter_profile
        threshold_profile = getattr(baseline, "threshold_profile", baseline.get("threshold_profile", {})) if isinstance(baseline, dict) else baseline.threshold_profile
        
        context = ExecutionContext(
            parameter_profile=parameter_profile,
            threshold_profile=threshold_profile,
            runtime_flags={}
        )
        
        for rule_id, rule_def in rule_set.items():
            # 1. Compile Rule
            try:
                compiled_rule = RuleCompiler.compile(rule_id, rule_def)
            except Exception as e:
                logger.error(f"Error compiling rule {rule_id}: {e}")
                continue

            # 1.5 Validate Compiled Rule
            try:
                compiled_rule.validate()
            except RuleValidationError as e:
                logger.error(f"Rule validation failed for rule {rule_id}: {e}")
                continue

            rule_executor_type = compiled_rule.executor.get("type", "single_fact")
            executor = self.executors.get(rule_executor_type)

            if executor:
                try:
                    scope_def = compiled_rule.target.get("filter", {}) or {}
                    # Add target_type to scope_def for backward compatibility with _apply_scope
                    if "target_type" not in scope_def:
                        scope_def["target_type"] = compiled_rule.target.get("type")
                        
                    # 2. Apply Scope
                    filtered_dataset = self._apply_scope(normalized_dataset, scope_def)

                    # 3. Dispatch
                    issues = executor.execute(rule_id, compiled_rule, filtered_dataset, context)
                    all_issues.extend(issues)
                except Exception as e:
                    logger.error(f"Error executing rule {rule_id}: {e}")
            else:
                logger.warning(f"No executor found for rule type: {rule_executor_type}")
                
        return all_issues

rule_engine = RuleEngine()
