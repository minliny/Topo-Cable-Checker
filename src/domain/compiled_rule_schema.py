from dataclasses import dataclass, field
from typing import Dict, Any, Optional

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
