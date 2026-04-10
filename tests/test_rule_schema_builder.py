from src.application.rule_editor_services.rule_schema_builder import RuleDraftSchemaBuilder

def test_ai_rule_schema_builder_builds_canonical_schema():
    schema = RuleDraftSchemaBuilder.build()
    assert schema.rule_types

    threshold = next((t for t in schema.rule_types if t.rule_type == "threshold"), None)
    assert threshold is not None

    metric_type = next((f for f in threshold.fields if f.name == "metric_type"), None)
    assert metric_type is not None
    assert metric_type.required is True
    assert metric_type.enum_values is not None
    assert "count" in metric_type.enum_values

    assert schema.output_contract.get("additionalProperties") is False
    assert "rule_type" in schema.output_contract["properties"]
    assert "target_type" in schema.output_contract["properties"]
    assert "severity" in schema.output_contract["properties"]
    assert "rule_definition" in schema.output_contract["properties"]

