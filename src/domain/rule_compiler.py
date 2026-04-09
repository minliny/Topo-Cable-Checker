import re
from typing import Dict, Any

class RuleCompiler:
    """
    Compiles Rule Definitions (DSL or Templates) into executable Rule Engine configuration objects.
    """
    
    @classmethod
    def compile(cls, rule_id: str, rule_def: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compiles a high-level rule definition into a low-level executable rule structure.
        """
        rule_type = rule_def.get("rule_type", "unknown")
        
        if rule_type == "dsl":
            return cls._compile_dsl(rule_id, rule_def)
        elif rule_type == "template":
            return cls._compile_template(rule_id, rule_def)
        else:
            # If it's already a raw executor config, return it as is or raise an error depending on strictness
            return rule_def
            
    @classmethod
    def _compile_dsl(cls, rule_id: str, rule_def: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compiles DSL expressions into single_fact executable config.
        Example DSL:
            when: device_type == "Switch"
            assert: status == "active"
        """
        expression = rule_def.get("expression", {})
        when_expr = expression.get("when", "")
        assert_expr = expression.get("assert", "")
        
        # Parse "when" clause to scope_selector
        scope_selector = {"target_type": rule_def.get("target_type", "devices")}
        if when_expr:
            # Basic parsing of key == "value"
            match = re.match(r'^\s*(\w+)\s*==\s*"([^"]+)"\s*$', when_expr)
            if match:
                scope_selector[match.group(1)] = match.group(2)
            else:
                raise ValueError(f"Unsupported 'when' DSL expression: {when_expr}")
                
        # Parse "assert" clause to target_field and expected value
        if assert_expr:
            match = re.match(r'^\s*(\w+)\s*==\s*"([^"]+)"\s*$', assert_expr)
            if match:
                target_field = match.group(1)
                expected_value = match.group(2)
            else:
                raise ValueError(f"Unsupported 'assert' DSL expression: {assert_expr}")
        else:
            raise ValueError("DSL expression must contain an 'assert' clause")
            
        compiled_rule = {
            "executor": "single_fact",
            "scope_selector": scope_selector,
            "field": target_field,
            "type": "field_equals",
            "expected": expected_value,
            "severity": rule_def.get("severity", "medium")
        }
        return compiled_rule
        
    @classmethod
    def _compile_template(cls, rule_id: str, rule_def: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compiles Template definitions into specific executor configs.
        Example Template:
            template: group_consistency
            params:
              group_key: device_type
              comparison_field: status
        """
        template_name = rule_def.get("template")
        params = rule_def.get("params", {})
        
        compiled_rule = {
            "executor": template_name,
            "scope_selector": rule_def.get("scope_selector", {"target_type": rule_def.get("target_type", "devices")}),
            "severity": rule_def.get("severity", "medium")
        }
        
        if template_name == "group_consistency":
            compiled_rule["group_key"] = params.get("group_key")
            compiled_rule["comparison_field"] = params.get("comparison_field")
            if "parameter_key" in params:
                 compiled_rule["parameter_key"] = params["parameter_key"]
        elif template_name == "threshold":
            compiled_rule["metric_type"] = params.get("metric_type", "count")
            if "metric_field" in params:
                compiled_rule["metric_field"] = params["metric_field"]
            if "threshold_key" in params:
                compiled_rule["threshold_key"] = params["threshold_key"]
        elif template_name == "topology":
            compiled_rule["source_type"] = params.get("source_type")
            compiled_rule["target_type"] = params.get("target_type")
            compiled_rule["link_type"] = params.get("link_type")
            compiled_rule["expected_connection"] = params.get("expected_connection")
        else:
            compiled_rule.update(params)
            
        return compiled_rule
