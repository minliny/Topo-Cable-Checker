import pytest
from src.application.rule_editor_services.rule_baseline_history_service import RuleBaselineHistoryService
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


@pytest.fixture
def repo_with_draft():
    repo = FakeBaselineRepository()
    baseline = BaselineProfile(
        baseline_id="b_draft",
        baseline_version="v1.1",
        rule_set={
            "r1": {"rule_type": "template", "template": "threshold", "target_type": "devices", "severity": "warning", "params": {"metric_type": "count", "threshold_key": "T1"}},
        },
        parameter_profile={},
        threshold_profile={},
        recognition_profile={},
        naming_profile={},
        baseline_version_snapshot={
            "v1.0": {
                "r1": {"rule_type": "template", "template": "threshold", "target_type": "devices", "severity": "warning", "params": {"metric_type": "count", "threshold_key": "T0"}},
            }
        },
        working_draft={
            "rule_id": "r1",
            "rule_type": "threshold",
            "target_type": "devices",
            "severity": "warning",
            "params": {"metric_type": "count", "threshold_key": "T2"},
        },
    )
    repo.save(baseline)
    return repo


def test_diff_versions_supports_draft_source(repo_with_draft):
    svc = RuleBaselineHistoryService(repo=repo_with_draft)
    diff = svc.diff_versions("b_draft", "draft", "v1.1")
    assert diff is not None
    assert len(diff.added_rules) == 0
    assert len(diff.removed_rules) == 0
    assert len(diff.modified_rules) == 1
    assert diff.modified_rules[0].rule_id == "r1"


def test_diff_versions_rejects_unknown_version(repo_with_draft):
    svc = RuleBaselineHistoryService(repo=repo_with_draft)
    diff = svc.diff_versions("b_draft", "v9.9", "v1.1")
    assert diff is None

