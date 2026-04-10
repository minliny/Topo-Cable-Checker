from typing import Dict, Any, Optional

class ParameterSchemaRegistry:
    _schemas = {
        "threshold": {
            "required": ["metric_type"],
            "optional": ["metric_field", "threshold_key", "operator", "expected_value", "expected", "min_value", "max_value"]
        },
        "single_fact": {
            "required": ["field", "type"],
            "optional": ["expected"]
        },
        "group_consistency": {
            "required": [],
            "optional": ["group_key", "comparison_field", "parameter_key"]
        },
        "topology": {
            "required": ["source_type", "target_type", "link_type", "expected_connection"],
            "optional": []
        }
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
