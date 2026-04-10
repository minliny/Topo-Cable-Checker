from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from src.domain.rule_engine.rule_meta_registry import RuleMetaRegistry, RuleMeta
from src.domain.rule_engine.parameter_schema_registry import ParameterSchemaRegistry
from src.domain.rule_engine.rule_capability_registry import RuleCapabilityRegistry, RuleCapability

class RuleCatalogError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

@dataclass
class RuleDescriptor:
    rule_type: str
    display_name: str
    description: str
    rule_meta: RuleMeta
    parameter_schema: Dict[str, List[str]]  # e.g., {"required": [...], "optional": [...]}
    capabilities: List[RuleCapability]
    supported_targets: List[str]
    default_examples: List[Dict[str, Any]]

class RuleCatalogService:
    _descriptors: Dict[str, RuleDescriptor] = {}
    _initialized: bool = False

    @classmethod
    def _build_catalog(cls):
        if cls._initialized:
            return

        all_metas = RuleMetaRegistry.get_all()
        for rule_type, meta in all_metas.items():
            schema = ParameterSchemaRegistry._schemas.get(rule_type)
            if not schema:
                raise RuleCatalogError(f"Consistency Check Failed: Rule type '{rule_type}' has no parameter schema.")
                
            capabilities = RuleCapabilityRegistry._registry.get(rule_type, [])
            if not capabilities:
                raise RuleCatalogError(f"Consistency Check Failed: Rule type '{rule_type}' has no registered capabilities.")

            # Create default human-readable display names and descriptions based on rule_type
            display_name = rule_type.replace("_", " ").title()
            description = f"Rules of type {display_name} ({meta.category})"
            
            # Simple default examples based on type
            default_examples = []
            if rule_type == "single_fact":
                default_examples = [{"field": "status", "type": "field_equals", "expected": "active"}]
            elif rule_type == "threshold":
                default_examples = [{"metric_type": "count", "operator": "lt", "expected_value": 100}]

            descriptor = RuleDescriptor(
                rule_type=rule_type,
                display_name=display_name,
                description=description,
                rule_meta=meta,
                parameter_schema=schema,
                capabilities=capabilities,
                supported_targets=meta.supported_targets,
                default_examples=default_examples
            )
            cls._descriptors[rule_type] = descriptor

        cls._initialized = True

    @classmethod
    def list_rule_descriptors(cls) -> List[RuleDescriptor]:
        cls._build_catalog()
        return list(cls._descriptors.values())

    @classmethod
    def get_rule_descriptor(cls, rule_type: str) -> Optional[RuleDescriptor]:
        cls._build_catalog()
        return cls._descriptors.get(rule_type)

    @classmethod
    def list_capabilities(cls, rule_type: str) -> List[RuleCapability]:
        cls._build_catalog()
        descriptor = cls._descriptors.get(rule_type)
        return descriptor.capabilities if descriptor else []

    @classmethod
    def list_supported_rule_types(cls) -> List[str]:
        cls._build_catalog()
        return list(cls._descriptors.keys())

    @classmethod
    def force_rebuild(cls):
        """Used for testing to force rebuilding the catalog."""
        cls._initialized = False
        cls._descriptors = {}
        cls._build_catalog()
