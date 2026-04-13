from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from src.domain.rule_engine.compiled_rule import RuleValidationError

@dataclass
class RuleTarget:
    type: str
    filter: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RuleMessage:
    template: str
    severity: str

@dataclass
class CompiledRule:
    rule_id: str
    rule_type: str
    target: RuleTarget
    executor: str
    params: Dict[str, Any] = field(default_factory=dict)
    message: RuleMessage = field(default_factory=lambda: RuleMessage(template="", severity="medium"))

    def validate(self) -> None:
        if not self.rule_id:
            raise RuleValidationError("rule_id is required")
        if not self.rule_type:
            raise RuleValidationError("rule_type is required")
        if not self.executor or self.executor not in ["single_fact", "group_consistency", "topology", "threshold"]:
            raise RuleValidationError(f"Invalid executor.type: {self.executor}")
        if not self.target or not self.target.type or self.target.type not in ["devices", "ports", "links"]:
            raise RuleValidationError(f"Invalid target.type: {getattr(self.target, 'type', None)}")
        if self.target.filter is not None and not isinstance(self.target.filter, dict):
            raise RuleValidationError("target.filter must be a dict (structured expression)")
        if self.message is None:
            raise RuleValidationError("message is required")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_type": self.rule_type,
            "executor": {"type": self.executor},
            "target": {"type": self.target.type, "filter": self.target.filter},
            "message": {"template": self.message.template, "severity": self.message.severity},
            "severity": self.message.severity,
            "params": self.params,
        }
