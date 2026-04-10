from typing import Dict, Any, List

from src.application.recognition_services.rule_definition_model import RuleDefinition
from src.application.recognition_services.rule_definition_registry import RuleDefinitionRegistry


class ThresholdRuleCompiler:
    @staticmethod
    def compile(definition: RuleDefinition) -> Dict[str, Any]:
        if definition.engine_scope != "rule_engine_threshold":
            raise ValueError(f"Invalid engine_scope for threshold: {definition.engine_scope}")

        if not definition.applies_to or len(definition.applies_to) != 1:
            raise ValueError("threshold rules must have exactly one applies_to entry")

        applies_to = definition.applies_to[0]
        if applies_to == "DeviceFact":
            target_type = "devices"
        elif applies_to == "PortFact":
            target_type = "ports"
        elif applies_to == "LinkFact":
            target_type = "links"
        else:
            raise ValueError(f"Unsupported applies_to for threshold: {applies_to}")

        rule_type = definition.rule_type
        if rule_type not in {"threshold", "threshold_check"}:
            raise ValueError(f"Unsupported rule_type for threshold: {rule_type}")

        compiled_rule = {
            "executor": "threshold",
            "scope_selector": {"target_type": target_type},
            "severity": definition.severity,
            "metric_type": definition.parameters.get("metric_type", "count"),
        }

        # Handle optional threshold parameters
        if "metric_field" in definition.parameters:
            compiled_rule["metric_field"] = definition.parameters["metric_field"]
        if "threshold_key" in definition.parameters:
            compiled_rule["threshold_key"] = definition.parameters["threshold_key"]
        if "operator" in definition.parameters:
            compiled_rule["operator"] = definition.parameters["operator"]
        if "expected_value" in definition.parameters:
            compiled_rule["expected_value"] = definition.parameters["expected_value"]
        elif "value" in definition.parameters:
            compiled_rule["expected_value"] = definition.parameters["value"]
        if "min_value" in definition.parameters:
            compiled_rule["min_value"] = definition.parameters["min_value"]
        if "max_value" in definition.parameters:
            compiled_rule["max_value"] = definition.parameters["max_value"]

        if definition.message_template:
            compiled_rule["message_template"] = definition.message_template
        elif definition.error_message:
            compiled_rule["message_template"] = definition.error_message

        return compiled_rule

    @staticmethod
    def compile_registry(registry: RuleDefinitionRegistry, enabled_only: bool = True) -> Dict[str, Dict[str, Any]]:
        compiled: Dict[str, Dict[str, Any]] = {}
        definitions: List[RuleDefinition] = registry.get_by_scope("rule_engine_threshold", enabled_only=enabled_only)
        for d in definitions:
            compiled[d.rule_id] = ThresholdRuleCompiler.compile(d)
        return compiled
