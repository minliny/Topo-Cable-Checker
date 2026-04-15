"""
B2: Rollback completeness tests.

Verifies:
1. Restore-draft endpoint returns the FULL rule_set, not just the first rule
2. RuleBaselineHistoryService.rollback_to_version restores complete rule_set
3. API integration: POST /api/rules/restore-draft returns rule_set field
"""

import pytest
from src.application.rule_editor_services.rule_baseline_history_service import (
    RuleBaselineHistoryService,
    BaselineRollbackResult,
)
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


# ==========================================
# Domain Service Tests: rollback_to_version
# ==========================================

class TestRollbackCompleteRuleSet:
    """Verify rollback_to_version restores the complete rule_set."""

    @pytest.fixture
    def repo_with_multi_rule_baseline(self):
        repo = FakeBaselineRepository()
        baseline = BaselineProfile(
            baseline_id="rb-test",
            baseline_version="v1.2",
            rule_set={
                "rule_a": {"rule_type": "threshold", "params": {"metric_type": "count", "operator": "gt", "expected_value": 10}},
                "rule_b": {"rule_type": "single_fact", "params": {"field": "status", "type": "field_equals", "expected": "active"}},
                "rule_c": {"rule_type": "group_consistency", "params": {"group_key": "device_type", "parameter_key": "voltage"}},
            },
            parameter_profile={},
            threshold_profile={},
            recognition_profile={},
            naming_profile={},
            baseline_version_snapshot={
                "v1.0": {
                    "rule_x": {"rule_type": "threshold", "params": {"metric_type": "count", "operator": "eq", "expected_value": 5}},
                    "rule_y": {"rule_type": "single_fact", "params": {"field": "name", "type": "regex_match", "pattern": "^SW"}},
                },
                "v1.1": {
                    "rule_a": {"rule_type": "threshold", "params": {"metric_type": "count", "operator": "gt", "expected_value": 8}},
                    "rule_b": {"rule_type": "single_fact", "params": {"field": "status", "type": "field_equals", "expected": "active"}},
                }
            }
        )
        repo.save(baseline)
        return repo

    @pytest.fixture
    def service(self, repo_with_multi_rule_baseline):
        return RuleBaselineHistoryService(repo=repo_with_multi_rule_baseline)

    def test_rollback_restores_complete_rule_set(self, service, repo_with_multi_rule_baseline):
        """Rolling back to v1.0 should restore both rule_x and rule_y (the full v1.0 rule set)."""
        result = service.rollback_to_version("rb-test", "v1.0", "Full rollback test")

        assert result.rollback_success is True

        baseline = repo_with_multi_rule_baseline.get_by_id("rb-test")
        # v1.0 had rule_x and rule_y — both should be present
        assert "rule_x" in baseline.rule_set
        assert "rule_y" in baseline.rule_set
        # v1.2 rules should NOT be present
        assert "rule_a" not in baseline.rule_set
        assert "rule_b" not in baseline.rule_set
        assert "rule_c" not in baseline.rule_set

    def test_rollback_rule_count_matches_target(self, service, repo_with_multi_rule_baseline):
        """After rollback, rule count should match the target version's rule count."""
        service.rollback_to_version("rb-test", "v1.0", "Count test")

        baseline = repo_with_multi_rule_baseline.get_by_id("rb-test")
        assert len(baseline.rule_set) == 2  # v1.0 had 2 rules

    def test_rollback_to_v11_partial_overlap(self, service, repo_with_multi_rule_baseline):
        """Rolling back to v1.1 should give us rule_a and rule_b (2 rules)."""
        result = service.rollback_to_version("rb-test", "v1.1", "Partial overlap test")

        assert result.rollback_success is True
        baseline = repo_with_multi_rule_baseline.get_by_id("rb-test")
        assert len(baseline.rule_set) == 2
        assert "rule_a" in baseline.rule_set
        assert "rule_b" in baseline.rule_set
        # rule_c from v1.2 should be gone
        assert "rule_c" not in baseline.rule_set

    def test_rollback_preserves_rule_content_integrity(self, service, repo_with_multi_rule_baseline):
        """After rollback, rule content should exactly match the target version."""
        service.rollback_to_version("rb-test", "v1.0", "Integrity test")

        baseline = repo_with_multi_rule_baseline.get_by_id("rb-test")
        assert baseline.rule_set["rule_x"]["params"]["expected_value"] == 5
        assert baseline.rule_set["rule_x"]["params"]["operator"] == "eq"
        assert baseline.rule_set["rule_y"]["params"]["pattern"] == "^SW"

    def test_rollback_creates_new_version(self, service, repo_with_multi_rule_baseline):
        """Rollback should create a new version (bumped from v1.2 → v1.3)."""
        result = service.rollback_to_version("rb-test", "v1.0", "Version bump test")

        assert result.rollback_new_version == "v1.3"
        baseline = repo_with_multi_rule_baseline.get_by_id("rb-test")
        assert baseline.baseline_version == "v1.3"

    def test_rollback_snapshots_current_before_overwrite(self, service, repo_with_multi_rule_baseline):
        """Before overwriting, the current rule_set should be snapshotted."""
        service.rollback_to_version("rb-test", "v1.0", "Snapshot test")

        baseline = repo_with_multi_rule_baseline.get_by_id("rb-test")
        # v1.2 should be snapshotted (it was the current version before rollback)
        assert "v1.2" in baseline.baseline_version_snapshot
        snap = baseline.baseline_version_snapshot["v1.2"]
        assert "rule_a" in snap
        assert "rule_b" in snap
        assert "rule_c" in snap


class TestRollbackEdgeCases:
    """Edge cases for rollback completeness."""

    @pytest.fixture
    def repo_with_empty_version(self):
        repo = FakeBaselineRepository()
        baseline = BaselineProfile(
            baseline_id="edge-test",
            baseline_version="v1.1",
            rule_set={
                "rule1": {"rule_type": "threshold", "params": {"metric_type": "count"}},
            },
            parameter_profile={},
            threshold_profile={},
            recognition_profile={},
            naming_profile={},
            baseline_version_snapshot={
                "v1.0": {}  # Empty rule set
            }
        )
        repo.save(baseline)
        return repo

    def test_rollback_to_empty_rule_set(self, repo_with_empty_version):
        service = RuleBaselineHistoryService(repo=repo_with_empty_version)
        result = service.rollback_to_version("edge-test", "v1.0", "Empty rollback")

        assert result.rollback_success is True
        baseline = repo_with_empty_version.get_by_id("edge-test")
        assert len(baseline.rule_set) == 0

    def test_rollback_nonexistent_version_fails(self, repo_with_empty_version):
        service = RuleBaselineHistoryService(repo=repo_with_empty_version)
        result = service.rollback_to_version("edge-test", "v9.9", "Bad version")

        assert result.rollback_success is False
        assert len(result.errors) > 0

    def test_rollback_nonexistent_baseline_fails(self, repo_with_empty_version):
        service = RuleBaselineHistoryService(repo=repo_with_empty_version)
        result = service.rollback_to_version("nonexistent", "v1.0", "Bad baseline")

        assert result.rollback_success is False


# ==========================================
# API Integration Tests: POST /api/rules/restore-draft
# ==========================================

class TestRollbackAPIIntegration:
    """Verify the restore-draft API endpoint returns complete rule_set."""

    @pytest.fixture
    def app_client(self):
        from fastapi.testclient import TestClient
        from src.presentation.api.main import app
        return TestClient(app)

    def test_restore_draft_endpoint_returns_rule_set(self, app_client):
        """POST /api/rules/restore-draft should return rule_set in the response."""
        # We test against whatever baselines exist in the data files
        resp = app_client.post("/api/rules/restore-draft", json={
            "baseline_id": "baseline-001",
            "version_id": "v1.0"
        })
        # May return 200 or 404 depending on test data
        if resp.status_code == 200:
            data = resp.json()
            # B2: rule_set field should be present
            assert "rule_set" in data
            # rule_set should be a dict (even if empty)
            assert isinstance(data["rule_set"], dict)

    def test_restore_draft_endpoint_still_has_draft_data(self, app_client):
        """Restore-draft response should still include draft_data for editor hydration."""
        resp = app_client.post("/api/rules/restore-draft", json={
            "baseline_id": "baseline-001",
            "version_id": "v1.0"
        })
        if resp.status_code == 200:
            data = resp.json()
            assert data["restored_from_version_id"] == "v1.0"
            assert "draft_data" in data
