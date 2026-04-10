import pytest
from src.application.rule_editor_services.rule_editor_mvp_service import RuleEditorMVPService

@pytest.fixture
def editor_service():
    return RuleEditorMVPService()

def test_rule_editor_lists_rule_types(editor_service):
    types = editor_service.list_available_rule_types()
    assert len(types) > 0
    
    threshold_item = next((t for t in types if t.rule_type == "threshold"), None)
    assert threshold_item is not None
    assert threshold_item.display_name == "Threshold"
    assert threshold_item.category == "quantitative"

def test_rule_editor_loads_form_definition(editor_service):
    form_view = editor_service.create_new_rule_form("single_fact")
    assert form_view is not None
    assert form_view.rule_type == "single_fact"
    
    form_def = form_view.form_definition
    assert len(form_def.parameter_fields) > 0
    assert form_def.parameter_fields[0].field_name in ["field", "type", "expected"]

def test_rule_editor_applies_default_example(editor_service):
    form_view = editor_service.create_new_rule_form("threshold")
    assert form_view is not None
    
    # Should prepopulate with default example
    initial_data = form_view.initial_data
    assert initial_data.get("metric_type") == "count"

def test_rule_editor_builds_rule_draft(editor_service):
    # Simulate user filling out the form validly
    form_data = {
        "metric_type": "count",
        "operator": "lt",
        "expected_value": 50
    }
    
    draft = editor_service.validate_and_build_draft(
        rule_id="new_rule_1",
        rule_type="threshold",
        target_type="devices",
        severity="high",
        form_data=form_data
    )
    
    assert draft.validation_result.is_valid is True
    assert len(draft.validation_result.errors) == 0
    
    rule_def = draft.to_rule_def()
    assert rule_def["rule_type"] == "template"
    assert rule_def["template"] == "threshold"
    assert rule_def["params"] == form_data

def test_rule_editor_validation_feedback(editor_service):
    # Simulate user leaving required fields blank and providing invalid enum
    form_data = {
        # missing metric_type (required)
        "operator": "invalid_op", # invalid enum
        "expected_value": 50
    }
    
    draft = editor_service.validate_and_build_draft(
        rule_id="new_rule_2",
        rule_type="threshold",
        target_type="unsupported_target", # Invalid target
        severity="medium",
        form_data=form_data
    )
    
    assert draft.validation_result.is_valid is False
    errors = draft.validation_result.errors
    
    assert "target_type" in errors
    assert "Unsupported target type" in errors["target_type"]
    
    assert "metric_type" in errors
    assert "is required" in errors["metric_type"]
    
    assert "operator" in errors
    assert "Invalid value" in errors["operator"]
