from typing import Dict, Any, List
import re
from src.domain.compiled_rule_schema import CompiledRule, RuleTarget, RuleMessage

class RuleCompileError(Exception):
    """
    Structured error model for rule compilation failures.
    """
    def __init__(self, rule_id: str, error_type: str, message: str):
        self.rule_id = rule_id
        self.error_type = error_type
        self.message = message
        super().__init__(f"[{error_type}] {rule_id}: {message}")

    def to_dict(self):
        return {
            "rule_id": self.rule_id,
            "error_type": self.error_type,
            "message": self.message
        }

class TemplateRegistry:
    """
    Registry for supported rule templates.
    """
    _templates = {
        "group_consistency": {
            "target_executor": "group_consistency",
            "supported_params": ["group_key", "comparison_field", "parameter_key"],
            "validation_rules": [
                lambda p: None if ("parameter_key" in p or ("group_key" in p and "comparison_field" in p)) else "missing_required_param: either parameter_key or (group_key + comparison_field) is required"
            ]
        },
        "threshold": {
            "target_executor": "threshold",
            "supported_params": ["metric_type", "metric_field", "threshold_key", "operator", "expected_value", "expected", "min_value", "max_value"],
            "validation_rules": [
                lambda p: None if "metric_type" in p else "missing_required_param: metric_type is required",
                lambda p: "unknown_rule_capability: unsupported metric_type" if p.get("metric_type") not in ["count", "distinct_count", "sum", "average"] else None
            ]
        },
        "threshold_check": {
            "target_executor": "threshold",
            "supported_params": ["metric_type", "metric_field", "threshold_key"],
            "validation_rules": [
                lambda p: None if "metric_type" in p else "missing_required_param: metric_type is required",
                lambda p: "unknown_rule_capability: unsupported metric_type" if p.get("metric_type") not in ["count", "distinct_count", "sum", "average"] else None
            ]
        },
        "single_fact": {
            "target_executor": "single_fact",
            "supported_params": ["field", "type", "expected"],
            "validation_rules": []
        },
        "topology": {
            "target_executor": "topology",
            "supported_params": ["source_type", "target_type", "link_type", "expected_connection"],
            "validation_rules": []
        },
        "topology_assertion": {
            "target_executor": "topology",
            "supported_params": ["source_type", "target_type", "link_type", "expected_connection"],
            "validation_rules": [
                lambda p: None if "source_type" in p and "target_type" in p else "missing_required_param: source_type and target_type are required"
            ]
        }
    }

    @classmethod
    def get_template(cls, name: str):
        return cls._templates.get(name)

    @classmethod
    def validate(cls, name: str, params: Dict[str, Any]):
        template = cls.get_template(name)
        if not template:
            return "unknown_template"
        
        for rule in template["validation_rules"]:
            err = rule(params)
            if err:
                return err
        return None

class RuleCompiler:
    """
    Compiles Rule Definitions (DSL or Templates) into executable Rule Engine configuration objects.
    """

    SUPPORTED_VERSIONS = ["v1", "v1.0"]

    @classmethod
    def compile(cls, rule_id: str, rule_def: Dict[str, Any]) -> CompiledRule:
        language_version = rule_def.get("language_version", "v1.0")
        if language_version not in cls.SUPPORTED_VERSIONS:
            raise RuleCompileError(
                rule_id, 
                "unsupported_language_version", 
                f"Language version '{language_version}' is not supported. Supported versions: {cls.SUPPORTED_VERSIONS}"
            )

        rule_type = rule_def.get("rule_type")
        if not rule_type:
            raise RuleCompileError(rule_id, "unknown_rule_type", "Missing rule_type")
            
        target_type = rule_def.get("target_type", "devices")
        if target_type not in ["devices", "ports", "links"]:
            raise RuleCompileError(rule_id, "unsupported_target_type", f"Target type '{target_type}' is not supported")
            
        if rule_type == "dsl":
            return cls._compile_dsl(rule_id, rule_def)
        elif rule_type == "template":
            return cls._compile_template(rule_id, rule_def)
        else:
            raise RuleCompileError(rule_id, "unknown_rule_type", f"Unsupported rule_type: '{rule_type}'")
            
    @classmethod
    def _compile_dsl(cls, rule_id: str, rule_def: Dict[str, Any]) -> CompiledRule:
        expression = rule_def.get("expression", {})
        when_expr = expression.get("when")
        assert_expr = expression.get("assert")
        
        scope_selector = {"target_type": rule_def.get("target_type", "devices")}
        
        if when_expr:
            if isinstance(when_expr, str):
                match = re.match(r'^\s*(\w+)\s*==\s*"([^"]+)"\s*$', when_expr)
                if match:
                    scope_selector[match.group(1)] = match.group(2)
                else:
                    raise RuleCompileError(rule_id, "invalid_dsl_expression", f"Unsupported 'when' string expression: {when_expr}")
            elif isinstance(when_expr, dict) and "all" in when_expr:
                for cond in when_expr["all"]:
                    # Match standard equality: key == "value"
                    match_eq = re.match(r'^\s*(\w+)\s*==\s*"([^"]+)"\s*$', cond)
                    if match_eq:
                        scope_selector[match_eq.group(1)] = match_eq.group(2)
                        continue
                    
                    # Match exists shorthand in when clause: key exists
                    match_exists = re.match(r'^\s*(\w+)\s+exists\s*$', cond)
                    if match_exists:
                        if "_exists" not in scope_selector:
                            scope_selector["_exists"] = []
                        scope_selector["_exists"].append(match_exists.group(1))
                        continue
                        
                    raise RuleCompileError(rule_id, "invalid_dsl_expression", f"Unsupported 'when.all' condition: {cond}")
            else:
                raise RuleCompileError(rule_id, "invalid_dsl_expression", "Invalid 'when' clause format")
                
        if not assert_expr:
            raise RuleCompileError(rule_id, "invalid_dsl_expression", "DSL expression must contain an 'assert' clause")
            
        target_type = scope_selector.pop("target_type", "devices")
        target = RuleTarget(type=target_type, filter=scope_selector)
        
        params = {}
        rule_type = ""
        
        if isinstance(assert_expr, str):
            match = re.match(r'^\s*(\w+)\s*==\s*"([^"]+)"\s*$', assert_expr)
            if match:
                params["field"] = match.group(1)
                params["expected"] = match.group(2)
                rule_type = "field_equals"
            else:
                raise RuleCompileError(rule_id, "invalid_dsl_expression", f"Unsupported 'assert' string: {assert_expr}")
        elif isinstance(assert_expr, dict):
            if "regex" in assert_expr:
                params["field"] = assert_expr["regex"].get("field")
                params["expected"] = assert_expr["regex"].get("pattern")
                rule_type = "regex_match"
                if not params["field"] or not params["expected"]:
                    raise RuleCompileError(rule_id, "missing_required_param", "regex assert requires 'field' and 'pattern'")
            elif "exists" in assert_expr:
                params["field"] = assert_expr["exists"]
                rule_type = "missing_value" 
                params["expected"] = None
            else:
                raise RuleCompileError(rule_id, "invalid_dsl_expression", "Unsupported 'assert' dict keys")
        else:
            raise RuleCompileError(rule_id, "invalid_dsl_expression", "Invalid 'assert' clause format")
            
        msg_template = rule_def.get("message_template") or rule_def.get("error_message") or ""
        
        return CompiledRule(
            rule_id=rule_id,
            rule_type=rule_type,
            target=target,
            executor="single_fact",
            params=params,
            message=RuleMessage(template=msg_template, severity=rule_def.get("severity", "medium"))
        )
        
    @classmethod
    def _compile_template(cls, rule_id: str, rule_def: Dict[str, Any]) -> CompiledRule:
        template_name = rule_def.get("template")
        if not template_name:
            raise RuleCompileError(rule_id, "unknown_template", "Missing template name")
            
        params = rule_def.get("params", {})
        
        validation_error = TemplateRegistry.validate(template_name, params)
        if validation_error:
            if validation_error == "unknown_template":
                raise RuleCompileError(rule_id, "unknown_template", f"Template '{template_name}' not found in registry")
            elif validation_error.startswith("missing_required_param"):
                raise RuleCompileError(rule_id, "missing_required_param", validation_error)
            else:
                raise RuleCompileError(rule_id, "invalid_dsl_expression", validation_error)
                
        template_info = TemplateRegistry.get_template(template_name)
        
        from src.domain.rule_engine.rule_meta_registry import RuleMetaRegistry
        if not RuleMetaRegistry.get_meta(template_info["target_executor"]):
            raise RuleCompileError(rule_id, "unknown_rule_meta", f"Unknown executor meta for '{template_info['target_executor']}'")

        scope_selector = rule_def.get("scope_selector", {"target_type": rule_def.get("target_type", "devices")})
        target_type = scope_selector.pop("target_type", "devices")
        target = RuleTarget(type=target_type, filter=scope_selector)
        
        compiled_params = {}
        for p in template_info["supported_params"]:
            if p in params:
                compiled_params[p] = params[p]
                
        msg_template = rule_def.get("message_template") or rule_def.get("error_message") or ""
                
        return CompiledRule(
            rule_id=rule_id,
            rule_type=template_name,
            target=target,
            executor=template_info["target_executor"],
            params=compiled_params,
            message=RuleMessage(template=msg_template, severity=rule_def.get("severity", "medium"))
        )
