from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.application.rule_catalog_services.rule_catalog_presentation_service import RuleCatalogPresentationService


@dataclass(frozen=True)
class RuleFieldSchema:
    name: str
    field_type: str
    required: bool
    enum_values: Optional[List[str]]
    description: Optional[str]
    default: Any


@dataclass(frozen=True)
class RuleTypeSchema:
    rule_type: str
    summary: Optional[str]
    supported_targets: List[str]
    fields: List[RuleFieldSchema]


@dataclass(frozen=True)
class RuleDraftSchema:
    rule_types: List[RuleTypeSchema]
    output_contract: Dict[str, Any]


class RuleDraftSchemaBuilder:
    @classmethod
    def build(cls) -> RuleDraftSchema:
        previews = RuleCatalogPresentationService.list_rule_previews()
        rule_types: List[RuleTypeSchema] = []

        for p in previews:
            form_def = RuleCatalogPresentationService.get_rule_form_definition(p.rule_type)
            if not form_def:
                continue

            fields: List[RuleFieldSchema] = []
            for f in form_def.parameter_fields:
                fields.append(
                    RuleFieldSchema(
                        name=f.field_name,
                        field_type=f.field_type,
                        required=f.required,
                        enum_values=f.enum_options,
                        description=f.help_text or None,
                        default=f.default_value,
                    )
                )

            rule_types.append(
                RuleTypeSchema(
                    rule_type=p.rule_type,
                    summary=p.description or None,
                    supported_targets=list(form_def.supported_targets),
                    fields=fields,
                )
            )

        output_contract = cls._build_output_contract(rule_types)
        return RuleDraftSchema(rule_types=rule_types, output_contract=output_contract)

    @classmethod
    def to_gateway_schema(cls, schema: RuleDraftSchema) -> Dict[str, Any]:
        return dict(schema.output_contract)

    @classmethod
    def _build_output_contract(cls, rule_types: List[RuleTypeSchema]) -> Dict[str, Any]:
        return {
            "type": "object",
            "additionalProperties": False,
            "required": ["rule_type", "target_type", "severity", "rule_definition"],
            "properties": {
                "rule_type": {"type": "string", "enum": [rt.rule_type for rt in rule_types]},
                "target_type": {"type": "string"},
                "severity": {"type": "string"},
                "rule_definition": {"type": "object"},
            },
        }

