import pytest
from src.domain.baseline_model import BaselineProfile
from src.application.rule_editor_services.rule_draft_save_service import RuleDraftSaveService
from src.application.rule_editor_services.rule_publish_workflow_service import RulePublishWorkflowService
from tests.fakes.in_memory_baseline_repository import InMemoryBaselineRepository

def test_rule_draft_save_service_with_in_memory_repo():
    """
    Test that the application service works perfectly with an InMemoryRepository,
    proving that it is completely decoupled from the file system / concrete infrastructure.
    """
    # Arrange
    initial_baseline = BaselineProfile(
        baseline_id="B_TEST",
        baseline_version="v1.0",
        recognition_profile={},
        naming_profile={},
        rule_set={},
        revision=1
    )
    repo = InMemoryBaselineRepository(initial_data=[initial_baseline])
    svc = RuleDraftSaveService(repo=repo)
    
    # Act: Save a draft
    result = svc.save_draft(
        baseline_id="B_TEST",
        rule_id="new_rule",
        rule_type="threshold",
        target_type="devices",
        severity="error",
        params={"metric_type": "count", "threshold_key": "T1"},
        expected_revision=1
    )
    
    # Assert: Result is success
    assert result.success is True
    
    # Assert: The draft was saved in the in-memory repository, not touching the disk
    updated_profile = repo.get_by_id("B_TEST")
    assert updated_profile.working_draft is not None
    assert updated_profile.working_draft["rule_id"] == "new_rule"
    assert updated_profile.working_draft["rule_type"] == "threshold"
    
    # Act: Clear draft
    new_rev = svc.clear_draft(baseline_id="B_TEST", expected_revision=updated_profile.revision)
    
    # Assert: The draft is cleared
    cleared_profile = repo.get_by_id("B_TEST")
    assert cleared_profile.working_draft is None
    assert cleared_profile.revision == new_rev

from src.application.rule_editor_services.rule_editor_mvp_service import RuleDraftView

def test_rule_publish_workflow_service_with_in_memory_repo():
    """
    Test that RulePublishWorkflowService can be injected with an InMemoryRepository.
    """
    # Arrange
    draft_data = {
        "rule_id": "new_rule",
        "rule_type": "threshold",
        "target_type": "devices",
        "severity": "error",
        "params": {"metric_type": "count", "threshold_key": "T1"},
    }
    
    initial_baseline = BaselineProfile(
        baseline_id="B_TEST_2",
        baseline_version="v1.0",
        recognition_profile={},
        naming_profile={},
        rule_set={},
        revision=1,
        working_draft=draft_data
    )
    repo = InMemoryBaselineRepository(initial_data=[initial_baseline])
    svc = RulePublishWorkflowService(repo=repo)
    
    draft_view = RuleDraftView(**draft_data)
    
    # Act: Publish the draft
    # Note: Publish requires compiling, but we don't mock the bridge service here. 
    # The real bridge service will compile the valid threshold rule.
    result = svc.publish_draft(baseline_id="B_TEST_2", draft=draft_view, expected_revision=1)
    
    # Assert
    assert result.publish_success is True
    
    # Check that it's published in the repo
    updated_profile = repo.get_by_id("B_TEST_2")
    assert updated_profile.working_draft is None
    assert "new_rule" in updated_profile.rule_set
    assert updated_profile.revision == 2
