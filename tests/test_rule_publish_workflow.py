import pytest
from src.application.rule_editor_services.rule_editor_mvp_service import RuleDraftView, RuleDraftValidationResult
from src.application.rule_editor_services.rule_publish_workflow_service import RulePublishWorkflowService, RulePublishResult, RulePublishFailure
from src.domain.interfaces import IBaselineRepository
from src.domain.baseline_model import BaselineProfile

class FakeBaselineRepository(IBaselineRepository):
    def __init__(self):
        self._store = {}

    def save(self, baseline, expected_revision: int = None):
        if isinstance(baseline, dict):
            self._store[baseline["baseline_id"]] = baseline
        else:
            self._store[baseline.baseline_id] = baseline

    def get_by_id(self, baseline_id: str):
        return self._store.get(baseline_id)

    def list_all(self):
        return list(self._store.values())

    def delete(self, baseline_id: str):
        if baseline_id in self._store:
            del self._store[baseline_id]

@pytest.fixture
def fake_repo():
    repo = FakeBaselineRepository()
    # Initialize with a basic baseline
    baseline = BaselineProfile(
        baseline_id="b1",
        baseline_version="v1.0",
        rule_set={
            "existing_rule": {
                "rule_type": "template",
                "template": "single_fact",
                "target_type": "devices",
                "severity": "medium",
                "params": {"field": "status", "type": "field_equals", "expected": "active"}
            }
        },
        parameter_profile={},
        threshold_profile={},
        recognition_profile={},
        naming_profile={},
        baseline_version_snapshot={}
    )
    # The actual baseline model might have a 'name' attribute added dynamically or not at all,
    # so we avoid passing it in __init__ if it throws.
    setattr(baseline, "name", "Test Baseline")
    repo.save(baseline)
    return repo

@pytest.fixture
def publish_service(fake_repo):
    return RulePublishWorkflowService(repo=fake_repo)

def test_publish_draft_success(publish_service, fake_repo):
    draft = RuleDraftView(
        rule_id="new_rule",
        rule_type="threshold",
        target_type="devices",
        severity="high",
        params={"metric_type": "count", "operator": "gt", "expected_value": 5},
        validation_result=RuleDraftValidationResult(is_valid=True, errors={})
    )
    
    result = publish_service.publish_draft("b1", draft, expected_revision=1, change_note="Added new threshold rule")
    
    assert result.publish_success is True
    assert len(result.errors) == 0
    assert result.summary is not None
    assert result.summary.baseline_id == "b1"
    assert result.summary.baseline_version == "v1.1" # v1.0 bumped
    assert result.summary.published_rule_count == 2
    assert result.summary.changed_rule_count == 1
    assert result.summary.added_rules == 1
    assert result.summary.modified_rules == 0
    assert "Added rule 'new_rule' (threshold)" in result.summary.summary_text
    
    # Verify persistence
    updated_baseline = fake_repo.get_by_id("b1")
    assert updated_baseline.baseline_version == "v1.1"
    assert "new_rule" in updated_baseline.rule_set
    assert "existing_rule" in updated_baseline.rule_set
    assert "v1.0" in updated_baseline.baseline_version_snapshot
    assert "existing_rule" in updated_baseline.baseline_version_snapshot["v1.0"]

def test_publish_draft_rejects_form_validation_error(publish_service):
    # Form layer invalidated this draft
    draft = RuleDraftView(
        rule_id="bad_rule",
        rule_type="threshold",
        target_type="devices",
        severity="medium",
        params={},
        validation_result=RuleDraftValidationResult(is_valid=False, errors={"metric_type": "Required"})
    )
    
    result = publish_service.publish_draft("b1", draft, expected_revision=1)
    
    assert result.publish_success is False
    assert result.summary is None
    assert len(result.errors) == 1
    assert result.errors[0].error_type == "form_validation_error"
    assert result.errors[0].field_name == "metric_type"

def test_publish_draft_rejects_compile_error(publish_service):
    # Form validation passed, but structure missing metric_type
    draft = RuleDraftView(
        rule_id="bad_rule_compile",
        rule_type="threshold",
        target_type="devices",
        severity="medium",
        params={},
        validation_result=RuleDraftValidationResult(is_valid=True, errors={})
    )
    
    result = publish_service.publish_draft("b1", draft, expected_revision=1)
    
    assert result.publish_success is False
    assert result.summary is None
    assert len(result.errors) > 0
    
    error = result.errors[0]
    assert error.error_type == "invalid_parameter_schema"
    assert error.field_name == "metric_type"

def test_publish_modifies_existing_rule(publish_service, fake_repo):
    draft = RuleDraftView(
        rule_id="existing_rule",
        rule_type="single_fact",
        target_type="devices",
        severity="high",
        params={"field": "status", "type": "field_equals", "expected": "inactive"},
        validation_result=RuleDraftValidationResult(is_valid=True, errors={})
    )
    
    result = publish_service.publish_draft("b1", draft, expected_revision=1, change_note="Modified status to inactive")
    
    assert result.publish_success is True
    assert result.summary.added_rules == 0
    assert result.summary.modified_rules == 1
    assert result.summary.published_rule_count == 1
    assert "Modified rule 'existing_rule'" in result.summary.summary_text
