"""
A1-9: Draft Save API Integration Tests

Covers:
1. save_draft success
2. load_draft success
3. clear_draft success
4. reload baseline restores draft (auto-recovery)
5. publish success clears draft
6. invalid draft can save (no compile gate)
7. invalid draft cannot publish (publish validation gate still blocks)
8. schema migration v1.1 → v1.2

Uses FastAPI TestClient for real HTTP-level testing.
"""

import pytest
import json
import os
import copy
from fastapi.testclient import TestClient
from src.presentation.api.main import app
from src.infrastructure.repository import (
    BaselineRepository, _read_json, _write_json, DATA_DIR,
    BASELINES_SCHEMA_VERSION, BASELINES_MIGRATIONS,
    _apply_schema_migration,
)

client = TestClient(app)

# ==========================================
# Fixtures
# ==========================================

TEST_BASELINE_ID = "TEST_DRAFT_B001"


def _current_revision(baseline_id: str = TEST_BASELINE_ID) -> int:
    repo = BaselineRepository()
    b = repo.get_by_id(baseline_id)
    return getattr(b, "revision", 1) if b else 1


@pytest.fixture(autouse=True)
def ensure_test_baseline():
    """Ensure a test baseline exists for draft operations."""
    repo = BaselineRepository()
    from src.domain.baseline_model import BaselineProfile
    
    # Check if test baseline already exists
    existing = repo.get_by_id(TEST_BASELINE_ID)
    if existing:
        # Clear any existing working draft
        existing.working_draft = None
        repo.save(existing)
    else:
        # Create a minimal test baseline
        profile = BaselineProfile(
            baseline_id=TEST_BASELINE_ID,
            baseline_version="v1.0",
            recognition_profile={},
            naming_profile={},
            parameter_profile={"P1": {"group_key": "device_type", "comparison_field": "status"}},
            threshold_profile={"T1": {"operator": "gt", "expected_value": 0}},
            rule_set={"rule_threshold_1": {"rule_type": "template", "template": "threshold", "target_type": "devices", "severity": "warning", "params": {"metric_type": "count", "threshold_key": "T1"}}},
            working_draft=None,
        )
        repo.save(profile)
    
    yield
    
    # Cleanup: remove working_draft from test baseline after each test
    existing = repo.get_by_id(TEST_BASELINE_ID)
    if existing:
        existing.working_draft = None
        repo.save(existing)


# ==========================================
# Test Cases
# ==========================================

class TestSaveDraftSuccess:
    """A1-9.1: Save draft successfully."""

    def test_save_draft_returns_success(self):
        payload = {
            "baseline_id": TEST_BASELINE_ID,
            "expected_revision": _current_revision(),
            "rule_id": "draft_rule_1",
            "rule_type": "threshold",
            "target_type": "devices",
            "severity": "warning",
            "params": {"metric_type": "count", "threshold_key": "T1"},
        }
        response = client.post("/api/rules/draft/save", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["saved_at"] is not None
        assert data["message"] is not None

    def test_save_draft_persists_working_draft(self):
        payload = {
            "baseline_id": TEST_BASELINE_ID,
            "expected_revision": _current_revision(),
            "rule_id": "draft_rule_1",
            "rule_type": "threshold",
            "target_type": "devices",
            "severity": "warning",
            "params": {"metric_type": "count", "threshold_key": "T1"},
        }
        client.post("/api/rules/draft/save", json=payload)
        
        # Verify via repository directly
        repo = BaselineRepository()
        profile = repo.get_by_id(TEST_BASELINE_ID)
        assert profile is not None
        assert profile.working_draft is not None
        assert profile.working_draft["rule_id"] == "draft_rule_1"
        assert profile.working_draft["rule_type"] == "threshold"

    def test_save_draft_overwrites_previous(self):
        # Save first draft
        payload1 = {
            "baseline_id": TEST_BASELINE_ID,
            "expected_revision": _current_revision(),
            "rule_id": "draft_v1",
            "rule_type": "threshold",
            "params": {"metric_type": "count"},
        }
        resp1 = client.post("/api/rules/draft/save", json=payload1)
        assert resp1.status_code == 200
        new_rev = resp1.json().get("new_revision")
        
        # Save second draft (should overwrite)
        payload2 = {
            "baseline_id": TEST_BASELINE_ID,
            "expected_revision": payload1["expected_revision"],
            "rule_id": "draft_v2",
            "rule_type": "single_fact",
            "params": {"field": "status"},
        }
        response = client.post("/api/rules/draft/save", json=payload2)
        assert response.status_code == 409
        
        payload3 = dict(payload2)
        payload3["expected_revision"] = new_rev
        response2 = client.post("/api/rules/draft/save", json=payload3)
        assert response2.status_code == 200
        
        repo = BaselineRepository()
        profile = repo.get_by_id(TEST_BASELINE_ID)
        assert profile.working_draft["rule_id"] == "draft_v2"
        assert profile.working_draft["rule_type"] == "single_fact"


class TestLoadDraftSuccess:
    """A1-9.2: Load draft successfully."""

    def test_load_draft_when_none_exists(self):
        response = client.get(f"/api/rules/draft/{TEST_BASELINE_ID}")
        assert response.status_code == 200
        data = response.json()
        assert data["has_draft"] is False
        assert data["draft_data"] is None
        assert data["base_revision"] is not None

    def test_load_draft_after_save(self):
        # Save a draft first
        payload = {
            "baseline_id": TEST_BASELINE_ID,
            "expected_revision": _current_revision(),
            "rule_id": "saved_rule",
            "rule_type": "threshold",
            "params": {"metric_type": "count"},
        }
        client.post("/api/rules/draft/save", json=payload)
        
        # Load it back
        response = client.get(f"/api/rules/draft/{TEST_BASELINE_ID}")
        assert response.status_code == 200
        data = response.json()
        assert data["has_draft"] is True
        assert data["draft_data"] is not None
        assert data["draft_data"]["rule_id"] == "saved_rule"
        assert data["saved_at"] is not None


class TestClearDraftSuccess:
    """A1-9.3: Clear draft successfully."""

    def test_clear_draft_after_save(self):
        # Save a draft first
        payload = {
            "baseline_id": TEST_BASELINE_ID,
            "expected_revision": _current_revision(),
            "rule_id": "to_be_cleared",
            "rule_type": "threshold",
            "params": {},
        }
        client.post("/api/rules/draft/save", json=payload)
        
        # Clear it
        response = client.delete(f"/api/rules/draft/{TEST_BASELINE_ID}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify it's cleared
        repo = BaselineRepository()
        profile = repo.get_by_id(TEST_BASELINE_ID)
        assert profile.working_draft is None

    def test_clear_nonexistent_draft_is_idempotent(self):
        # Clear when no draft exists — should still return success
        response = client.delete(f"/api/rules/draft/{TEST_BASELINE_ID}")
        assert response.status_code == 200


class TestReloadRestoresDraft:
    """A1-9.4: Reload baseline restores draft (auto-recovery simulation)."""

    def test_save_then_load_preserves_data(self):
        # Save a draft with specific data
        payload = {
            "baseline_id": TEST_BASELINE_ID,
            "expected_revision": _current_revision(),
            "rule_id": "recovery_test",
            "rule_type": "threshold",
            "target_type": "devices",
            "severity": "error",
            "params": {"metric_type": "distinct_count", "metric_field": "device_type", "operator": "gt", "expected_value": 5},
        }
        client.post("/api/rules/draft/save", json=payload)
        
        # Simulate "page reload" by loading the draft via API
        response = client.get(f"/api/rules/draft/{TEST_BASELINE_ID}")
        data = response.json()
        
        assert data["has_draft"] is True
        draft = data["draft_data"]
        assert draft["rule_id"] == "recovery_test"
        assert draft["rule_type"] == "threshold"
        assert draft["target_type"] == "devices"
        assert draft["severity"] == "error"
        assert draft["params"]["metric_type"] == "distinct_count"
        assert draft["params"]["operator"] == "gt"


class TestPublishClearsDraft:
    """A1-9.5: Publish success clears draft."""

    def test_publish_success_clears_working_draft(self):
        # Save a draft first
        save_payload = {
            "baseline_id": TEST_BASELINE_ID,
            "expected_revision": _current_revision(),
            "rule_id": "publish_test_rule",
            "rule_type": "threshold",
            "params": {"metric_type": "count", "threshold_key": "T1"},
        }
        client.post("/api/rules/draft/save", json=save_payload)
        
        # Verify draft exists
        load_resp = client.get(f"/api/rules/draft/{TEST_BASELINE_ID}")
        assert load_resp.json()["has_draft"] is True
        
        # Publish the rule (valid params)
        publish_payload = {
            "rule_id": "publish_test_rule",
            "expected_revision": _current_revision(),
            "rule_type": "threshold",
            "target_type": "devices",
            "severity": "error",
            "params": {"metric_type": "count", "threshold_key": "T1"},
        }
        response = client.post(f"/api/rules/publish/{TEST_BASELINE_ID}", json=publish_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify draft is now cleared
        load_resp2 = client.get(f"/api/rules/draft/{TEST_BASELINE_ID}")
        assert load_resp2.json()["has_draft"] is False


class TestInvalidDraftCanSave:
    """A1-9.6: Invalid draft CAN be saved (no compile gate on save)."""

    def test_save_draft_with_missing_params(self):
        """Invalid draft (missing required params) should still be saveable."""
        payload = {
            "baseline_id": TEST_BASELINE_ID,
            "expected_revision": _current_revision(),
            "rule_id": "invalid_rule",
            "rule_type": "threshold",
            "params": {},  # Missing metric_type and threshold_key — invalid for compilation
        }
        response = client.post("/api/rules/draft/save", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_save_draft_with_garbage_params(self):
        """Even garbage data should be saveable — it's just a draft."""
        payload = {
            "baseline_id": TEST_BASELINE_ID,
            "expected_revision": _current_revision(),
            "rule_id": "garbage_rule",
            "rule_type": "nonexistent_type",
            "params": {"random": "data", "numbers": 42},
        }
        response = client.post("/api/rules/draft/save", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestInvalidDraftCannotPublish:
    """A1-9.7: Invalid draft CANNOT be published (publish validation gate still blocks)."""

    def test_publish_invalid_draft_is_blocked(self):
        payload = {
            "rule_id": "bad_publish_rule",
            "expected_revision": _current_revision(),
            "rule_type": "threshold",
            "target_type": "devices",
            "severity": "warning",
            "params": {},  # Missing required fields
        }
        response = client.post(f"/api/rules/publish/{TEST_BASELINE_ID}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["blocked_issues"] is not None
        assert len(data["blocked_issues"]) > 0


class TestSchemaMigrationV11toV12:
    """A1-9.8: Schema migration v1.1 → v1.2 (adds working_draft=null)."""

    def test_v11_data_migrates_to_v12(self):
        """Simulate v1.1 baselines data and verify migration adds working_draft."""
        v11_data = {
            "__schema_version__": "1.1",
            "B_MIGRATION_TEST": {
                "baseline_id": "B_MIGRATION_TEST",
                "baseline_version": "v1.0",
                "recognition_profile": {},
                "naming_profile": {},
                "parameter_profile": {},
                "threshold_profile": {},
                "rule_set": {
                    "rule_1": {"rule_type": "template", "template": "threshold", "severity": "warning", "params": {}}
                },
                "baseline_version_snapshot": {},
                "version_history_meta": {},
            }
        }
        
        # Apply migration
        migrated = _apply_schema_migration(
            "baselines.json", v11_data, BASELINES_SCHEMA_VERSION,
            BASELINES_MIGRATIONS, "__schema_version__"
        )
        
        # Check schema version bumped
        assert migrated["__schema_version__"] == BASELINES_SCHEMA_VERSION
        
        # Check working_draft was added
        assert "working_draft" in migrated["B_MIGRATION_TEST"]
        assert migrated["B_MIGRATION_TEST"]["working_draft"] is None

    def test_pre_schema_data_migrates_all_the_way(self):
        """Pre-schema (v0) data should migrate through all steps to current version."""
        v0_data = {
            "B_PRE_SCHEMA": {
                "baseline_id": "B_PRE_SCHEMA",
                "baseline_version": "v1.0",
                "recognition_profile": {},
                "naming_profile": {},
                "rule_set": {
                    "rule_old": {"template": "threshold", "severity": "warning", "params": {}}
                },
                "baseline_version_snapshot": {"v1.0": "some_string"},
            }
        }
        
        migrated = _apply_schema_migration(
            "baselines.json", v0_data, BASELINES_SCHEMA_VERSION,
            BASELINES_MIGRATIONS, "__schema_version__"
        )
        
        assert migrated["__schema_version__"] == BASELINES_SCHEMA_VERSION
        
        entry = migrated["B_PRE_SCHEMA"]
        # v0→v1.0: version_history_meta added
        assert "version_history_meta" in entry
        # v0→v1.0: snapshot normalized from string to dict
        assert isinstance(entry["baseline_version_snapshot"].get("v1.0"), dict)
        # v1.0→v1.1: rule_type added
        assert entry["rule_set"]["rule_old"]["rule_type"] == "template"
        # v1.1→v1.2: working_draft added
        assert "working_draft" in entry
        assert entry["working_draft"] is None


class TestSaveDraftBaselineNotFound:
    """Edge case: saving draft for a nonexistent baseline."""

    def test_save_draft_nonexistent_baseline_returns_404(self):
        payload = {
            "baseline_id": "NONEXISTENT_BASELINE",
            "expected_revision": 1,
            "rule_id": "test",
            "rule_type": "threshold",
            "params": {},
        }
        response = client.post("/api/rules/draft/save", json=payload)
        assert response.status_code == 404

    def test_clear_draft_nonexistent_baseline_returns_404(self):
        response = client.delete("/api/rules/draft/NONEXISTENT_BASELINE")
        assert response.status_code == 404
