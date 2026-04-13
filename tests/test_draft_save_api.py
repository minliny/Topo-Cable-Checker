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
            "rule_set": {
                "draft_rule_1": {
                    "rule_type": "template",
                    "template": "threshold",
                    "target_type": "devices",
                    "severity": "warning",
                    "params": {"metric_type": "count", "threshold_key": "T1"}
                }
            },
            "active_rule_id": "draft_rule_1"
        }
        response = client.post("/api/rules/draft/save", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["saved_at"] is not None
        assert "draft_snapshot" in data

    def test_save_draft_persists_working_draft(self):
        payload = {
            "baseline_id": TEST_BASELINE_ID,
            "rule_set": {
                "draft_rule_2": {
                    "rule_type": "template",
                    "template": "group_consistency",
                    "target_type": "devices",
                    "severity": "info",
                    "params": {"parameter_key": "P1"}
                }
            },
            "active_rule_id": "draft_rule_2"
        }
        client.post("/api/rules/draft/save", json=payload)
        
        # Verify via repository directly
        repo = BaselineRepository()
        profile = repo.get_by_id(TEST_BASELINE_ID)
        assert profile is not None
        assert profile.working_draft is not None
        assert profile.working_draft.get("active_rule_id") == "draft_rule_2"
        assert "draft_rule_2" in profile.working_draft.get("rule_set", {})

    def test_save_draft_overwrites_previous(self):
        # Save first draft
        payload1 = {
            "baseline_id": TEST_BASELINE_ID,
            "rule_set": {
                "draft_v1": {
                    "rule_type": "template",
                    "template": "threshold",
                    "target_type": "devices",
                    "severity": "high",
                    "params": {"metric_type": "count"}
                }
            },
            "active_rule_id": "draft_v1"
        }
        client.post("/api/rules/draft/save", json=payload1)
        
        # Save second draft (should overwrite)
        payload2 = {
            "baseline_id": TEST_BASELINE_ID,
            "rule_set": {
                "draft_v2": {
                    "rule_type": "template",
                    "template": "single_fact",
                    "target_type": "devices",
                    "severity": "info",
                    "params": {"field": "status"}
                }
            },
            "active_rule_id": "draft_v2"
        }
        response = client.post("/api/rules/draft/save", json=payload2)
        assert response.status_code == 200
        
        repo = BaselineRepository()
        profile = repo.get_by_id(TEST_BASELINE_ID)
        assert profile.working_draft["active_rule_id"] == "draft_v2"
        assert "draft_v2" in profile.working_draft["rule_set"]


class TestLoadDraftSuccess:
    """A1-9.2: Load draft successfully."""

    def test_load_draft_when_none_exists(self):
        # Ensure it handles no existing draft
        response = client.get(f"/api/rules/draft/{TEST_BASELINE_ID}")
        assert response.status_code == 200
        data = response.json()
        assert data["has_draft"] is False
        assert data["draft_data"] is None

    def test_load_draft_after_save(self):
        # Save a draft first
        payload = {
            "baseline_id": TEST_BASELINE_ID,
            "rule_set": {
                "saved_rule": {
                    "rule_type": "template",
                    "template": "threshold",
                    "target_type": "devices",
                    "severity": "warning",
                    "params": {"metric_type": "count"}
                }
            },
            "active_rule_id": "saved_rule"
        }
        client.post("/api/rules/draft/save", json=payload)
        
        # Load it back
        response = client.get(f"/api/rules/draft/{TEST_BASELINE_ID}")
        assert response.status_code == 200
        data = response.json()
        assert data["has_draft"] is True
        assert data["draft_data"] is not None
        assert data["draft_data"]["active_rule_id"] == "saved_rule"
        assert "saved_rule" in data["draft_data"]["rule_set"]
        assert data["saved_at"] is not None


class TestClearDraftSuccess:
    """A1-9.3: Clear draft successfully."""

    def test_clear_draft_after_save(self):
        # Save a draft first
        payload = {
            "baseline_id": TEST_BASELINE_ID,
            "rule_set": {
                "to_be_cleared": {
                    "rule_type": "template",
                    "template": "threshold",
                    "target_type": "devices",
                    "severity": "warning",
                    "params": {}
                }
            },
            "active_rule_id": "to_be_cleared"
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
            "rule_set": {
                "recovery_test": {
                    "rule_type": "template",
                    "template": "threshold",
                    "target_type": "devices",
                    "severity": "error",
                    "params": {"metric_type": "distinct_count", "metric_field": "device_type", "operator": "gt", "expected_value": 5}
                }
            },
            "active_rule_id": "recovery_test"
        }
        client.post("/api/rules/draft/save", json=payload)
        
        # Simulate "page reload" by loading the draft via API
        response = client.get(f"/api/rules/draft/{TEST_BASELINE_ID}")
        data = response.json()
        
        assert data["has_draft"] is True
        draft = data["draft_data"]
        assert draft["active_rule_id"] == "recovery_test"
        rule_draft = draft["rule_set"]["recovery_test"]
        assert rule_draft["rule_type"] == "template"
        assert rule_draft["template"] == "threshold"
        assert rule_draft["target_type"] == "devices"
        assert rule_draft["severity"] == "error"
        assert rule_draft["params"]["metric_type"] == "distinct_count"
        assert rule_draft["params"]["operator"] == "gt"


class TestPublishClearsDraft:
    """A1-9.5: Publish success clears draft."""

    def test_publish_success_clears_working_draft(self):
        # Save a draft first
        save_payload = {
            "baseline_id": TEST_BASELINE_ID,
            "rule_set": {
                "publish_test_rule": {
                    "rule_type": "template",
                    "template": "threshold",
                    "target_type": "devices",
                    "severity": "error",
                    "params": {"metric_type": "count", "threshold_key": "T1"}
                }
            },
            "active_rule_id": "publish_test_rule"
        }
        client.post("/api/rules/draft/save", json=save_payload)
        
        # Verify draft exists
        load_resp = client.get(f"/api/rules/draft/{TEST_BASELINE_ID}")
        assert load_resp.json()["has_draft"] is True
        
        # The test originally expected a successful publish to clear the draft.
        # But we modified the publish endpoint structure. Let's make sure the payload has a rule_set.
        publish_payload = {
            "baseline_id": TEST_BASELINE_ID,
            "rule_set": {
                "publish_test_rule": {
                    "rule_type": "template",
                    "template": "threshold",
                    "target_type": "devices",
                    "severity": "error",
                    "params": {"metric_type": "count", "threshold_key": "T1"}
                }
            }
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
            "rule_set": {
                "invalid_rule": {
                    "rule_type": "template",
                    "template": "threshold",
                    "target_type": "devices",
                    "severity": "warning",
                    "params": {}  # Missing metric_type and threshold_key — invalid for compilation
                }
            },
            "active_rule_id": "invalid_rule"
        }
        response = client.post("/api/rules/draft/save", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_save_draft_with_garbage_params(self):
        """Even garbage data should be saveable — it's just a draft."""
        payload = {
            "baseline_id": TEST_BASELINE_ID,
            "rule_set": {
                "garbage_rule": {
                    "rule_type": "nonexistent_type",
                    "params": {"random": "data", "numbers": 42}
                }
            },
            "active_rule_id": "garbage_rule"
        }
        response = client.post("/api/rules/draft/save", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestInvalidDraftCannotPublish:
    """A1-9.7: Invalid draft CANNOT be published (publish validation gate still blocks)."""

    def test_publish_invalid_draft_is_blocked(self):
        payload = {
            "baseline_id": TEST_BASELINE_ID,
            "rule_set": {
                "bad_publish_rule": {
                    "rule_type": "template",
                    "template": "threshold",
                    "target_type": "devices",
                    "severity": "warning",
                    "params": {},  # Missing required fields
                }
            }
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
            "rule_set": {
                "test": {
                    "rule_type": "template",
                    "template": "threshold",
                    "params": {}
                }
            },
            "active_rule_id": "test"
        }
        response = client.post("/api/rules/draft/save", json=payload)
        assert response.status_code == 404

    def test_clear_draft_nonexistent_baseline_returns_404(self):
        response = client.delete("/api/rules/draft/NONEXISTENT_BASELINE")
        assert response.status_code == 404
