from src.application.rule_editor_services.ai_rule_output_validator import AiRuleOutputValidator
from src.application.rule_editor_services.ai_rule_schema_builder import AiRuleSchemaBuilder


def test_ai_output_validator_rejects_invalid_top_level_shape():
    schema = AiRuleSchemaBuilder.build()
    result = AiRuleOutputValidator.validate(["not-a-dict"], schema)
    assert result.is_valid is False
    assert any(e.code == "invalid_top_level_shape" for e in result.schema_errors)


def test_ai_output_validator_rejects_unknown_top_level_fields():
    schema = AiRuleSchemaBuilder.build()
    result = AiRuleOutputValidator.validate(
        {
            "rule_type": "threshold",
            "target_type": "devices",
            "severity": "high",
            "rule_definition": {},
            "x": 1,
        },
        schema,
    )
    assert result.is_valid is False
    assert any(e.code == "unknown_top_level_field" and e.field == "x" for e in result.schema_errors)


def test_ai_output_validator_rejects_unknown_rule_definition_fields():
    schema = AiRuleSchemaBuilder.build()
    result = AiRuleOutputValidator.validate(
        {
            "rule_type": "threshold",
            "target_type": "devices",
            "severity": "high",
            "rule_definition": {"nope": 1},
        },
        schema,
    )
    assert result.is_valid is False
    assert any(e.code == "unknown_field" and e.field == "rule_definition.nope" for e in result.schema_errors)


def test_ai_output_validator_rejects_invalid_enum_value():
    schema = AiRuleSchemaBuilder.build()
    result = AiRuleOutputValidator.validate(
        {
            "rule_type": "threshold",
            "target_type": "devices",
            "severity": "high",
            "rule_definition": {"metric_type": "count", "operator": "INVALID", "expected_value": 1},
        },
        schema,
    )
    assert result.is_valid is False
    assert any(e.code == "invalid_enum_value" and e.field == "rule_definition.operator" for e in result.schema_errors)

