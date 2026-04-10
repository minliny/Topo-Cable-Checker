from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class RuleMeta:
    rule_type: str
    category: str  # quantitative, logical, topology
    supported_targets: List[str]
    supports_grouping: bool
    supports_topology: bool

class RuleMetaRegistry:
    _registry: Dict[str, RuleMeta] = {}

    @classmethod
    def register(cls, meta: RuleMeta):
        cls._registry[meta.rule_type] = meta

    @classmethod
    def get_meta(cls, rule_type: str) -> Optional[RuleMeta]:
        return cls._registry.get(rule_type)

    @classmethod
    def get_all(cls) -> Dict[str, RuleMeta]:
        return cls._registry.copy()

# Register out-of-the-box rule types
RuleMetaRegistry.register(RuleMeta(
    rule_type="single_fact",
    category="logical",
    supported_targets=["devices", "ports", "links"],
    supports_grouping=False,
    supports_topology=False
))

RuleMetaRegistry.register(RuleMeta(
    rule_type="threshold",
    category="quantitative",
    supported_targets=["devices", "ports", "links"],
    supports_grouping=True,
    supports_topology=False
))

RuleMetaRegistry.register(RuleMeta(
    rule_type="group_consistency",
    category="logical",
    supported_targets=["devices", "ports", "links"],
    supports_grouping=True,
    supports_topology=False
))

RuleMetaRegistry.register(RuleMeta(
    rule_type="topology",
    category="topology",
    supported_targets=["links"],
    supports_grouping=False,
    supports_topology=True
))
