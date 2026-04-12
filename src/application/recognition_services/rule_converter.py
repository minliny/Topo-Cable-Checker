from typing import Callable, Dict, Any
from src.application.recognition_services.rule_definition_model import RuleDefinition
from src.application.recognition_services.input_contract import RowConstraint

class RuleDefinitionConverter:
    """
    Converts serializable RuleDefinition objects into runtime RowConstraint objects with executable lambdas.
    """
    @staticmethod
    def to_runtime(definition: RuleDefinition) -> RowConstraint:
        condition_fn = RuleDefinitionConverter._build_condition(definition.rule_type, definition.parameters)
        
        return RowConstraint(
            id=definition.rule_id,
            name=definition.name,
            description=definition.description,
            condition=condition_fn,
            error_message=definition.error_message,
            severity=definition.severity,
            enabled=definition.enabled,
            group=definition.group
        )

    @staticmethod
    def _build_condition(rule_type: str, parameters: Dict[str, Any]) -> Callable[[Dict[str, Any]], bool]:
        if rule_type == "field_equals":
            target_field = parameters.get("target_field")
            expected_value = parameters.get("expected_value")
            if not target_field:
                raise ValueError(f"Missing target_field in parameters for rule type {rule_type}")
            return lambda row: row.get(target_field) == expected_value

        elif rule_type == "field_not_equals":
            target_field = parameters.get("target_field")
            expected_value = parameters.get("expected_value")
            if not target_field:
                raise ValueError(f"Missing target_field in parameters for rule type {rule_type}")
            return lambda row: row.get(target_field) != expected_value

        elif rule_type == "if_field_equals_then_required":
            target_field = parameters.get("target_field")
            expected_value = parameters.get("expected_value")
            dependent_field = parameters.get("dependent_field")
            if not target_field or not dependent_field:
                raise ValueError(f"Missing target_field or dependent_field in parameters for rule type {rule_type}")
                
            def _condition(row: Dict[str, Any]) -> bool:
                # If target field doesn't match the condition, rule is trivially satisfied
                if row.get(target_field) != expected_value:
                    return True
                # If it does match, the dependent field MUST be present and not empty
                dep_val = row.get(dependent_field)
                return dep_val is not None and str(dep_val).strip() != ""
                
            return _condition
            
        else:
            raise ValueError(f"Unsupported rule_type: {rule_type}")
