import pytest
from src.application.rule_catalog_services.rule_catalog_presentation_service import (
    RuleCatalogPresentationService, 
    RulePreviewDTO, 
    RuleFormDefinitionDTO
)

def test_rule_preview_build():
    previews = RuleCatalogPresentationService.list_rule_previews()
    assert len(previews) > 0
    
    # Check if a preview is properly formed
    threshold_preview = next((p for p in previews if p.rule_type == "threshold"), None)
    assert threshold_preview is not None
    assert threshold_preview.category == "quantitative"
    assert len(threshold_preview.capabilities) > 0
    assert hasattr(threshold_preview.capabilities[0], "intent_category")

    # test get single
    single = RuleCatalogPresentationService.get_rule_preview("single_fact")
    assert single is not None
    assert single.rule_type == "single_fact"

def test_rule_form_definition():
    form_def = RuleCatalogPresentationService.get_rule_form_definition("threshold")
    assert form_def is not None
    assert form_def.rule_type == "threshold"
    
    # Check parameter fields mapping
    fields = form_def.parameter_fields
    assert len(fields) > 0
    
    metric_type_field = next((f for f in fields if f.field_name == "metric_type"), None)
    assert metric_type_field is not None
    assert metric_type_field.required is True
    assert metric_type_field.field_type == "select"
    assert "count" in metric_type_field.enum_options
    assert metric_type_field.default_value == "count"
    
    operator_field = next((f for f in fields if f.field_name == "operator"), None)
    assert operator_field is not None
    assert operator_field.required is False # It's optional
    assert operator_field.field_type == "select"
    
    # Validation hints
    assert len(form_def.validation_hints) > 0
    assert any("metric_type" in hint for hint in form_def.validation_hints)

def test_rule_default_example():
    example = RuleCatalogPresentationService.get_rule_default_example("single_fact")
    assert example is not None
    assert example["type"] == "field_equals"
    assert example["field"] == "status"
    
    unknown = RuleCatalogPresentationService.get_rule_default_example("non_existent_rule")
    assert unknown is None

def test_consumer_layer_uses_catalog_only():
    # The application layer should not leak domain objects directly
    form_def = RuleCatalogPresentationService.get_rule_form_definition("threshold")
    
    # Check that DTOs are used
    assert isinstance(form_def, RuleFormDefinitionDTO)
    assert not hasattr(form_def, "rule_meta") # Internal domain object hidden
    assert not hasattr(form_def, "parameter_schema") # Internal domain object hidden
