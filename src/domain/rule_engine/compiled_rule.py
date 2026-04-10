from typing import Dict, Any, Optional
from src.domain.rule_engine.rule_meta_registry import RuleMeta
from src.domain.rule_engine.rule_capability_registry import RuleCapability

class RuleValidationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class CompiledRule:
    def __init__(
        self,
        rule_id: str,
        rule_type: str,
        executor: Dict[str, Any],
        target: Dict[str, Any],
        message: Dict[str, Any],
        severity: str = "medium",
        params: Optional[Dict[str, Any]] = None,
        rule_meta: Optional[RuleMeta] = None,
        capability: Optional[RuleCapability] = None,
        **kwargs
    ):
        self.rule_id = rule_id
        self.rule_type = rule_type
        self.executor = executor
        self.target = target
        self.message = message
        self.severity = severity
        self.params = params or {}
        self.rule_meta = rule_meta
        self.capability = capability
        
        # Store other arbitrary properties that might be needed
        self._extra = kwargs

    def validate(self):
        if not self.rule_id:
            raise RuleValidationError("rule_id is required")
        if not self.rule_type:
            raise RuleValidationError("rule_type is required")
        
        executor_type = self.executor.get("type")
        if not executor_type or executor_type not in ["single_fact", "group_consistency", "topology", "threshold"]:
            raise RuleValidationError(f"Invalid executor.type: {executor_type}")
            
        target_type = self.target.get("type")
        if not target_type or target_type not in ["devices", "ports", "links"]:
            raise RuleValidationError(f"Invalid target.type: {target_type}")
            
        target_filter = self.target.get("filter")
        if target_filter is not None:
            if callable(target_filter) or type(target_filter).__name__ == 'function':
                raise RuleValidationError("target.filter cannot be a function, must be a structured expression")
            if not isinstance(target_filter, dict):
                raise RuleValidationError("target.filter must be a dict (structured expression)")
                
        if not self.message or not self.message.get("template"):
            raise RuleValidationError("message.template is required")

    def get(self, key: str, default: Any = None) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        return self._extra.get(key, default)
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_type": self.rule_type,
            "executor": self.executor,
            "target": self.target,
            "message": self.message,
            "severity": self.severity,
            "params": self.params,
            **self._extra
        }
