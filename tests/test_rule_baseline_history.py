import pytest
from src.application.rule_editor_services.rule_baseline_history_service import (
    RuleBaselineHistoryService,
    BaselineVersionListItemView,
    BaselineDiffView,
    BaselineDiffRuleChangeView,
    BaselineRollbackResult
)
from src.domain.interfaces import IBaselineRepository
from src.domain.baseline_model import BaselineProfile

class FakeBaselineRepository(IBaselineRepository):
    def __init__(self):
        self._store = {}

    def save(self, baseline):
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
    
    baseline = BaselineProfile(
        baseline_id="b1",
        baseline_version="v1.2",
        rule_set={
            "rule1": {"rule_type": "threshold", "params": {"metric_type": "count", "operator": "gt"}},
            "rule3": {"rule_type": "single_fact", "params": {"field": "status", "type": "field_equals"}}
        },
        parameter_profile={},
        threshold_profile={},
        recognition_profile={},
        naming_profile={},
        baseline_version_snapshot={
            "v1.0": {
                "rule1": {"rule_type": "threshold", "params": {"metric_type": "count", "operator": "eq"}},
                "rule2": {"rule_type": "topology", "params": {"source_type": "devices"}}
            },
            "v1.1": {
                "rule1": {"rule_type": "threshold", "params": {"metric_type": "count", "operator": "gt"}},
                "rule2": {"rule_type": "topology", "params": {"source_type": "devices"}},
                "rule3": {"rule_type": "single_fact", "params": {"field": "status", "type": "field_equals"}}
            }
        }
    )
    
    repo.save(baseline)
    return repo

@pytest.fixture
def history_service(fake_repo):
    return RuleBaselineHistoryService(repo=fake_repo)

def test_list_baseline_versions_returns_ordered_history(history_service):
    versions = history_service.list_baseline_versions("b1")
    
    assert len(versions) == 3
    # It should be ordered descending (v1.2, v1.1, v1.0) based on simple string sort for now
    assert versions[0].version == "v1.2"
    assert versions[0].is_current is True
    assert versions[0].rule_count == 2
    
    assert versions[1].version == "v1.1"
    assert versions[1].is_current is False
    assert versions[1].rule_count == 3
    
    assert versions[2].version == "v1.0"
    assert versions[2].is_current is False

def test_diff_versions_detects_added_removed_modified_rules(history_service):
    # Diff v1.0 to v1.2
    diff = history_service.diff_versions("b1", "v1.0", "v1.2")
    
    assert diff is not None
    assert diff.from_version == "v1.0"
    assert diff.to_version == "v1.2"
    
    assert len(diff.added_rules) == 1
    assert diff.added_rules[0].rule_id == "rule3"
    
    assert len(diff.removed_rules) == 1
    assert diff.removed_rules[0].rule_id == "rule2"
    
    assert len(diff.modified_rules) == 1
    assert diff.modified_rules[0].rule_id == "rule1"
    assert "params" in diff.modified_rules[0].changed_fields
    
    assert "1 added, 1 removed, 1 modified" in diff.summary_text

def test_rollback_to_version_creates_new_version(history_service, fake_repo):
    # Rollback to v1.0
    result = history_service.rollback_to_version("b1", "v1.0", "Rolling back to stable")
    
    assert result.rollback_success is True
    assert result.rollback_target_version == "v1.0"
    assert result.rollback_new_version == "v1.3" # Bumped from v1.2
    
    # Check baseline structure after rollback
    updated_baseline = fake_repo.get_by_id("b1")
    assert updated_baseline.baseline_version == "v1.3"
    
    # Rule set should now match v1.0
    assert "rule1" in updated_baseline.rule_set
    assert "rule2" in updated_baseline.rule_set
    assert "rule3" not in updated_baseline.rule_set
    
def test_rollback_preserves_history(history_service, fake_repo):
    history_service.rollback_to_version("b1", "v1.0", "Rolling back")
    
    updated_baseline = fake_repo.get_by_id("b1")
    snapshots = updated_baseline.baseline_version_snapshot
    
    # The history should now contain v1.0, v1.1, and the state that was active just before rollback (v1.2)
    assert "v1.0" in snapshots
    assert "v1.1" in snapshots
    assert "v1.2" in snapshots
    
    # Check v1.2 was correctly snapshotted
    assert "rule3" in snapshots["v1.2"]
    
def test_diff_view_contains_summary(history_service):
    diff = history_service.diff_versions("b1", "v1.1", "v1.2")
    
    assert diff is not None
    # from v1.1 to v1.2, rule2 was removed, nothing added, nothing modified
    assert len(diff.removed_rules) == 1
    assert len(diff.added_rules) == 0
    assert len(diff.modified_rules) == 0
    assert "0 added, 1 removed, 0 modified" in diff.summary_text
