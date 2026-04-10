from typing import Dict, Any, List

from src.application.recognition_services.rule_definition_model import RuleDefinition
from src.application.recognition_services.rule_definition_registry import RuleDefinitionRegistry


class SingleFactRuleCompiler:
    @staticmethod
    def compile(definition: RuleDefinition) -> Dict[str, Any]:
        if definition.engine_scope != "rule_engine_single_fact":
            raise ValueError(f"Invalid engine_scope for single_fact: {definition.engine_scope}")

        if not definition.applies_to or len(definition.applies_to) != 1:
            raise ValueError("single_fact rules must have exactly one applies_to entry")

        applies_to = definition.applies_to[0]
        if applies_to == "DeviceFact":
            target_type = "devices"
        elif applies_to == "PortFact":
            target_type = "ports"
        elif applies_to == "LinkFact":
            target_type = "links"
        else:
            raise ValueError(f"Unsupported applies_to for single_fact: {applies_to}")

        rule_type = definition.rule_type
        if rule_type not in {"field_equals", "field_not_equals", "missing_value"}:
            raise ValueError(f"Unsupported rule_type for single_fact: {rule_type}")

        field = definition.parameters.get("target_field")
        expected = definition.parameters.get("expected_value")
        if not field:
            raise ValueError("Missing parameters.target_field for single_fact rule")

        compiled_rule = {
            "executor": "single_fact",
            "scope_selector": {"target_type": target_type},
            "severity": definition.severity,
            "field": field,
            "expected": expected,
            "type": rule_type,
        }
        
        if definition.message_template:
            compiled_rule["message_template"] = definition.message_template
        elif definition.error_message:
            compiled_rule["message_template"] = definition.error_message
            
        return compiled_rule

    @staticmethod
    def compile_registry(registry: RuleDefinitionRegistry, enabled_only: bool = True) -> Dict[str, Dict[str, Any]]:
        compiled: Dict[str, Dict[str, Any]] = {}
        definitions: List[RuleDefinition] = registry.get_by_scope("rule_engine_single_fact", enabled_only=enabled_only)
        for d in definitions:
            compiled[d.rule_id] = SingleFactRuleCompiler.compile(d)
        return compiled

