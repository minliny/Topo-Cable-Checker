from typing import Dict, Any, Optional
from src.domain.rule_engine.rule_meta_registry import RuleMetaRegistry

class ParameterSchemaRegistry:
    _schemas = {}

    @classmethod
    def register(cls, rule_type: str, required: list, optional: list):
        if not RuleMetaRegistry.get_meta(rule_type):
            raise ValueError(f"Cannot register schema for unknown rule_type: {rule_type}")
            
        cls._schemas[rule_type] = {
            "required": required,
            "optional": optional
        }

    @classmethod
    def validate(cls, executor_type: str, params: Dict[str, Any]) -> Optional[str]:
        schema = cls._schemas.get(executor_type)
        if not schema:
            return f"Unknown executor type: {executor_type}"
            
        for req in schema["required"]:
            if req not in params:
                return f"Missing required parameter: {req}"
                
        # Optional: we can also check for unsupported parameters
        # allowed = set(schema["required"] + schema["optional"])
        # for k in params:
        #     if k not in allowed:
        #         return f"Unsupported parameter: {k}"
                
        return None

# Register out-of-the-box schemas
ParameterSchemaRegistry.register(
    "threshold",
    required=["metric_type"],
    optional=["metric_field", "threshold_key", "operator", "expected_value", "expected", "min_value", "max_value"]
)

ParameterSchemaRegistry.register(
    "single_fact",
    required=["field", "type"],
    optional=["expected"]
)

ParameterSchemaRegistry.register(
    "group_consistency",
    required=[],
    optional=["group_key", "comparison_field", "parameter_key"]
)

ParameterSchemaRegistry.register(
    "topology",
    required=["source_type", "target_type", "link_type", "expected_connection"],
    optional=[]
)
