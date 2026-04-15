import pytest
from src.application.rule_editor_services.rule_editor_mvp_service import RuleDraftView, RuleDraftValidationResult
from src.application.rule_editor_services.rule_editor_governance_bridge_service import RuleEditorGovernanceBridgeService

@pytest.fixture
def bridge_service():
    return RuleEditorGovernanceBridgeService()

def test_rule_draft_compile_preview_success(bridge_service):
    draft = RuleDraftView(
        rule_id="r1",
        rule_type="threshold",
        target_type="devices",
        severity="medium",
        params={"metric_type": "count", "operator": "gt", "expected_value": 5},
        validation_result=RuleDraftValidationResult(is_valid=True, errors={})
    )
    
    result = bridge_service.compile_draft_preview(draft)
    
    assert result.compile_success is True
    assert len(result.validation_errors) == 0
    assert result.compiled_preview is not None
    assert result.compiled_preview["executor"] == "threshold"
    # Ensure internal domain objects are stripped
    assert "rule_meta" not in result.compiled_preview
    assert "capability" not in result.compiled_preview

def test_rule_draft_compile_preview_failure(bridge_service):
    # Pass a valid draft at the UI level, but structurally invalid for compiler
    # e.g., metric_type is not provided
    draft = RuleDraftView(
        rule_id="r2",
        rule_type="threshold",
        target_type="devices",
        severity="medium",
        params={},  # missing metric_type
        validation_result=RuleDraftValidationResult(is_valid=True, errors={})
    )
    
    result = bridge_service.compile_draft_preview(draft)
    
    assert result.compile_success is False
    assert result.compiled_preview is None
    assert len(result.validation_errors) == 1
    
    error = result.validation_errors[0]
    assert error.error_type == "invalid_parameter_schema"

def test_governance_error_mapping(bridge_service):
    # Test that "missing metric_type" maps back to the metric_type field
    draft = RuleDraftView(
        rule_id="r3",
        rule_type="threshold",
        target_type="devices",
        severity="medium",
        params={"operator": "eq"}, # missing metric_type
        validation_result=RuleDraftValidationResult(is_valid=True, errors={})
    )
    
    result = bridge_service.compile_draft_preview(draft)
    assert result.compile_success is False
    
    error = result.validation_errors[0]
    # Check if the heuristic successfully extracted the field name
    assert error.field_name == "metric_type"

def test_publish_candidate_summary_build(bridge_service):
    draft = RuleDraftView(
        rule_id="r_publish",
        rule_type="single_fact",
        target_type="devices",
        severity="high",
        params={"field": "status", "type": "field_equals", "expected": "active"},
        validation_result=RuleDraftValidationResult(is_valid=True, errors={})
    )
    
    candidate = bridge_service.build_publish_candidate(draft)
    
    assert candidate.rule_id == "r_publish"
    assert candidate.is_ready_for_publish is True
    assert "New rule" in candidate.diff_summary
    assert candidate.compile_result.compile_success is True
