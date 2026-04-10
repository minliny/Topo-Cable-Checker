from src.application.rule_editor_services.rule_draft_validator import RuleDraftValidator
from src.application.rule_editor_services.rule_schema_builder import RuleDraftSchemaBuilder

def test_ai_output_validator_rejects_invalid_top_level_shape():
    schema = RuleDraftSchemaBuilder.build()
    result = RuleDraftValidator.validate(["not-a-dict"], schema)
    assert result.is_valid is False
    assert any(e.code == "invalid_top_level_shape" for e in result.schema_errors)

def test_ai_output_validator_rejects_unknown_top_level_fields():
    schema = RuleDraftSchemaBuilder.build()
    result = RuleDraftValidator.validate(
        {"rule_type": "threshold", "target_type": "devices", "severity": "high", "rule_definition": {}, "x": 1},
        schema,
    )
    assert result.is_valid is False
    assert any(e.code == "unknown_top_level_field" for e in result.schema_errors)

def test_ai_output_validator_rejects_unknown_rule_definition_fields():
    schema = RuleDraftSchemaBuilder.build()
    result = RuleDraftValidator.validate(
        {"rule_type": "threshold", "target_type": "devices", "severity": "high", "rule_definition": {"nope": 1}},
        schema,
    )
    assert result.is_valid is False
    assert any(e.code == "unknown_field" for e in result.schema_errors)

def test_ai_output_validator_rejects_invalid_enum_value():
    schema = RuleDraftSchemaBuilder.build()
    result = RuleDraftValidator.validate(
        {
            "rule_type": "threshold",
            "target_type": "devices",
            "severity": "high",
            "rule_definition": {"metric_type": "count", "operator": "INVALID", "expected_value": 1},
        },
        schema,
    )
    assert result.is_valid is False
    assert any(e.code == "invalid_enum_value" for e in result.schema_errors)

