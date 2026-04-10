from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from src.domain.rule_engine.rule_catalog import RuleCatalogService, RuleDescriptor

@dataclass
class ParameterFieldDTO:
    field_name: str
    field_type: str
    required: bool
    enum_options: Optional[List[str]] = None
    default_value: Any = None
    placeholder: str = ""
    help_text: str = ""

@dataclass
class RuleCapabilityDTO:
    capability_id: str
    intent_category: str
    description: str

@dataclass
class RulePreviewDTO:
    rule_type: str
    display_name: str
    description: str
    category: str
    supported_targets: List[str]
    capabilities: List[RuleCapabilityDTO]

@dataclass
class RuleFormDefinitionDTO:
    rule_type: str
    display_name: str
    description: str
    category: str
    supported_targets: List[str]
    capabilities: List[RuleCapabilityDTO]
    parameter_fields: List[ParameterFieldDTO]
    default_example: Dict[str, Any]
    validation_hints: List[str]

class RuleCatalogPresentationService:
    """
    Adapter layer that converts domain RuleCatalog concepts into UI-friendly DTOs.
    """
    
    # Hardcoded metadata for form fields to enrich the basic schema
    _FIELD_METADATA = {
        "metric_type": {
            "type": "select",
            "enum_options": ["count", "distinct_count", "sum", "average"],
            "default": "count",
            "placeholder": "Select metric type",
            "help_text": "The type of metric to calculate."
        },
        "operator": {
            "type": "select",
            "enum_options": ["eq", "gt", "gte", "lt", "lte", "neq"],
            "default": "eq",
            "placeholder": "Operator",
            "help_text": "Comparison operator."
        },
        "type": {
            "type": "select",
            "enum_options": ["field_equals", "regex_match", "missing_value"],
            "default": "field_equals",
            "placeholder": "Condition type",
            "help_text": "Type of single fact check."
        },
        "expected": {
            "type": "string",
            "placeholder": "Expected value",
            "help_text": "The expected value to match."
        },
        "field": {
            "type": "string",
            "placeholder": "Field name",
            "help_text": "The name of the attribute to check."
        }
    }

    @classmethod
    def _map_capability(cls, cap) -> RuleCapabilityDTO:
        return RuleCapabilityDTO(
            capability_id=cap.capability_id,
            intent_category=cap.intent_category,
            description=cap.description
        )

    @classmethod
    def _build_parameter_fields(cls, descriptor: RuleDescriptor) -> List[ParameterFieldDTO]:
        fields = []
        schema = descriptor.parameter_schema
        
        all_field_names = schema.get("required", []) + schema.get("optional", [])
        required_set = set(schema.get("required", []))
        
        for fname in all_field_names:
            meta = cls._FIELD_METADATA.get(fname, {})
            fields.append(ParameterFieldDTO(
                field_name=fname,
                field_type=meta.get("type", "string"),
                required=(fname in required_set),
                enum_options=meta.get("enum_options"),
                default_value=meta.get("default"),
                placeholder=meta.get("placeholder", f"Enter {fname}"),
                help_text=meta.get("help_text", f"Parameter: {fname}")
            ))
            
        return fields

    @classmethod
    def list_rule_previews(cls) -> List[RulePreviewDTO]:
        descriptors = RuleCatalogService.list_rule_descriptors()
        return [
            RulePreviewDTO(
                rule_type=d.rule_type,
                display_name=d.display_name,
                description=d.description,
                category=d.rule_meta.category,
                supported_targets=d.supported_targets,
                capabilities=[cls._map_capability(c) for c in d.capabilities]
            )
            for d in descriptors
        ]

    @classmethod
    def get_rule_preview(cls, rule_type: str) -> Optional[RulePreviewDTO]:
        d = RuleCatalogService.get_rule_descriptor(rule_type)
        if not d:
            return None
            
        return RulePreviewDTO(
            rule_type=d.rule_type,
            display_name=d.display_name,
            description=d.description,
            category=d.rule_meta.category,
            supported_targets=d.supported_targets,
            capabilities=[cls._map_capability(c) for c in d.capabilities]
        )

    @classmethod
    def get_rule_form_definition(cls, rule_type: str) -> Optional[RuleFormDefinitionDTO]:
        d = RuleCatalogService.get_rule_descriptor(rule_type)
        if not d:
            return None
            
        parameter_fields = cls._build_parameter_fields(d)
        default_example = d.default_examples[0] if d.default_examples else {}
        
        # Basic validation hints based on schema
        validation_hints = [f"'{req}' is a required field." for req in d.parameter_schema.get("required", [])]
        
        return RuleFormDefinitionDTO(
            rule_type=d.rule_type,
            display_name=d.display_name,
            description=d.description,
            category=d.rule_meta.category,
            supported_targets=d.supported_targets,
            capabilities=[cls._map_capability(c) for c in d.capabilities],
            parameter_fields=parameter_fields,
            default_example=default_example,
            validation_hints=validation_hints
        )

    @classmethod
    def get_rule_default_example(cls, rule_type: str) -> Optional[Dict[str, Any]]:
        d = RuleCatalogService.get_rule_descriptor(rule_type)
        if not d or not d.default_examples:
            return None
        return d.default_examples[0]
