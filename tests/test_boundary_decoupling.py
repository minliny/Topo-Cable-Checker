import pytest
from typing import List, Dict, Any, Optional
from src.domain.interfaces import IBaselineRepository
from src.domain.baseline_model import BaselineProfile
from src.application.rule_editor_services.rule_draft_save_service import RuleDraftSaveService
from src.application.rule_editor_services.rule_editor_mvp_service import RuleDraftView
from src.crosscutting.errors.exceptions import ConcurrencyError

class InMemoryBaselineRepository(IBaselineRepository):
    """A pure in-memory implementation of the baseline repository for testing decoupling."""
    def __init__(self):
        self.profiles: Dict[str, BaselineProfile] = {}
        
    def get_all(self) -> List[BaselineProfile]:
        return list(self.profiles.values())
        
    def get_by_id(self, baseline_id: str) -> BaselineProfile:
        # Mimic file-based repo logic where it creates a default if missing
        if baseline_id not in self.profiles:
            return BaselineProfile(
                baseline_id=baseline_id,
                baseline_version="v1.0",
                recognition_profile={},
                naming_profile={}
            )
        return self.profiles[baseline_id]
        
    def save(self, profile: BaselineProfile, expected_revision: int = None):
        current = self.profiles.get(profile.baseline_id)
        current_revision = current.revision if current else 0
        
        if expected_revision is not None and current_revision != expected_revision:
            raise ConcurrencyError(
                message=f"Conflict detected for baseline {profile.baseline_id}"
            )
            
        profile.revision = current_revision + 1
        self.profiles[profile.baseline_id] = profile

def test_service_can_run_with_in_memory_repo():
    """
    Tests that the application layer is fully decoupled from the concrete 
    infrastructure (JSON/file) and can work flawlessly with an in-memory test double.
    """
    # 1. Arrange
    repo = InMemoryBaselineRepository()
    service = RuleDraftSaveService(repo=repo)
    
    draft = RuleDraftView(
        rule_id="rule_1",
        rule_type="test_rule",
        target_type="devices",
        severity="error",
        params={"key": "val"}
    )
    
    # 2. Act
    result = service.save_draft(
        baseline_id="B001",
        rule_id="rule_1",
        rule_type="test_rule",
        target_type="devices",
        severity="error",
        params={"key": "val"},
        expected_revision=0
    )
    
    # 3. Assert
    assert result.success is True
    assert result.new_revision == 1
    
    # Verify the draft is stored in our in-memory repo
    saved_profile = repo.get_by_id("B001")
    assert saved_profile.working_draft is not None
    assert saved_profile.working_draft["rule_id"] == "rule_1"
    
def test_in_memory_repo_enforces_occ_semantics():
    repo = InMemoryBaselineRepository()
    service = RuleDraftSaveService(repo=repo)
    
    draft = RuleDraftView(
        rule_id="rule_1", rule_type="test_rule", target_type="devices",
        severity="error", params={}
    )
    
    # Save once to get revision 1
    service.save_draft(
        baseline_id="B001", rule_id="rule_1", rule_type="test_rule", 
        target_type="devices", severity="error", params={}, expected_revision=0
    )
    
    # Try to save again with stale expected_revision=0
    with pytest.raises(ConcurrencyError):
        service.save_draft(
            baseline_id="B001", rule_id="rule_1", rule_type="test_rule", 
            target_type="devices", severity="error", params={}, expected_revision=0
        )