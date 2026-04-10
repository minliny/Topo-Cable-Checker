from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Callable

@dataclass
class RuleCapability:
    capability_id: str
    rule_type: str
    intent_category: str
    description: str
    supported_targets: List[str]
    required_params: List[str]
    optional_params: List[str]
    match_fn: Callable[[Dict[str, Any]], bool]

class RuleCapabilityRegistry:
    _registry: Dict[str, List[RuleCapability]] = {}

    @classmethod
    def register(cls, capability: RuleCapability):
        if capability.rule_type not in cls._registry:
            cls._registry[capability.rule_type] = []
        cls._registry[capability.rule_type].append(capability)

    @classmethod
    def infer_capability(cls, rule_type: str, params: Dict[str, Any]) -> Optional[RuleCapability]:
        candidates = cls._registry.get(rule_type, [])
        for cap in candidates:
            # Check required params
            has_all_required = all(p in params for p in cap.required_params)
            if not has_all_required:
                continue
                
            # Use match function for more complex logic
            if cap.match_fn(params):
                return cap
        return None

# threshold capabilities
RuleCapabilityRegistry.register(RuleCapability(
    capability_id="threshold.count_limit",
    rule_type="threshold",
    intent_category="quantitative_limit",
    description="Limits the count of items to a specific threshold",
    supported_targets=["devices", "ports", "links"],
    required_params=["metric_type"],
    optional_params=["operator", "expected_value", "expected", "min_value", "max_value", "threshold_key"],
    match_fn=lambda p: p.get("metric_type") == "count"
))

RuleCapabilityRegistry.register(RuleCapability(
    capability_id="threshold.range_check",
    rule_type="threshold",
    intent_category="quantitative_range",
    description="Checks if a metric falls within a specific range",
    supported_targets=["devices", "ports", "links"],
    required_params=["metric_type", "metric_field"],
    optional_params=["operator", "expected_value", "expected", "min_value", "max_value", "threshold_key"],
    match_fn=lambda p: p.get("metric_type") in ["distinct_count", "sum", "average"]
))

# single_fact capabilities
RuleCapabilityRegistry.register(RuleCapability(
    capability_id="single_fact.equality_check",
    rule_type="single_fact",
    intent_category="logical_match",
    description="Checks if a specific field matches an expected value or regex",
    supported_targets=["devices", "ports", "links"],
    required_params=["field", "type"],
    optional_params=["expected"],
    match_fn=lambda p: p.get("type") in ["field_equals", "regex_match"]
))

RuleCapabilityRegistry.register(RuleCapability(
    capability_id="single_fact.existence_check",
    rule_type="single_fact",
    intent_category="logical_existence",
    description="Checks if a specific field exists and is not empty",
    supported_targets=["devices", "ports", "links"],
    required_params=["field", "type"],
    optional_params=[],
    match_fn=lambda p: p.get("type") == "missing_value"
))

# group_consistency capability
RuleCapabilityRegistry.register(RuleCapability(
    capability_id="group_consistency.uniformity",
    rule_type="group_consistency",
    intent_category="logical_consistency",
    description="Ensures all items in a group have the same value for a specific field",
    supported_targets=["devices", "ports", "links"],
    required_params=[],
    optional_params=["group_key", "comparison_field", "parameter_key"],
    match_fn=lambda p: True
))

# topology capability
RuleCapabilityRegistry.register(RuleCapability(
    capability_id="topology.connection_check",
    rule_type="topology",
    intent_category="topology_validation",
    description="Validates topology connections based on specific rules",
    supported_targets=["links"],
    required_params=["source_type", "target_type", "link_type", "expected_connection"],
    optional_params=[],
    match_fn=lambda p: True
))
