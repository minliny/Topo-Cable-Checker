from typing import Dict, Any, List

from src.application.recognition_services.rule_definition_model import RuleDefinition
from src.application.recognition_services.rule_definition_registry import RuleDefinitionRegistry
from src.domain.compiled_rule_schema import CompiledRule, RuleTarget, RuleMessage


class ThresholdRuleCompiler:
    @staticmethod
    def compile(definition: RuleDefinition) -> CompiledRule:
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

        params = {
            "metric_type": definition.parameters.get("metric_type", "count")
        }

        # Handle optional threshold parameters
        if "metric_field" in definition.parameters:
            params["metric_field"] = definition.parameters["metric_field"]
        if "threshold_key" in definition.parameters:
            params["threshold_key"] = definition.parameters["threshold_key"]
        if "operator" in definition.parameters:
            params["operator"] = definition.parameters["operator"]
        if "expected_value" in definition.parameters:
            params["expected_value"] = definition.parameters["expected_value"]
        elif "value" in definition.parameters:
            params["expected_value"] = definition.parameters["value"]
        if "min_value" in definition.parameters:
            params["min_value"] = definition.parameters["min_value"]
        if "max_value" in definition.parameters:
            params["max_value"] = definition.parameters["max_value"]

        msg_template = definition.message_template or definition.error_message or ""

        return CompiledRule(
            rule_id=definition.rule_id,
            rule_type=rule_type,
            target=RuleTarget(type=target_type),
            executor="threshold",
            params=params,
            message=RuleMessage(template=msg_template, severity=definition.severity)
        )

    @staticmethod
    def compile_registry(registry: RuleDefinitionRegistry, enabled_only: bool = True) -> Dict[str, CompiledRule]:
        compiled: Dict[str, CompiledRule] = {}
        definitions: List[RuleDefinition] = registry.get_by_scope("rule_engine_threshold", enabled_only=enabled_only)
        for d in definitions:
            compiled[d.rule_id] = ThresholdRuleCompiler.compile(d)
        return compiled
