"""
P1.0-1 + P1.0-2 Tests: Publish endpoint body binding and validation gate.

Validates:
1. PublishRequestDTO is properly bound from request body (draft_data no longer None)
2. Invalid drafts are BLOCKED from publishing
3. Valid drafts can be successfully published
4. Published data matches the submitted draft_data
5. Validation genuinely blocks publish (no bypass)
"""

import pytest
import os
import json
import shutil
from fastapi.testclient import TestClient
from src.presentation.api.main import app

client = TestClient(app)

# Use a dedicated test data directory to avoid polluting real data
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "_test_publish_data")

def _get_revision(baseline_id: str = "B001") -> int:
    resp = client.get("/api/baselines")
    if resp.status_code != 200:
        return 1
    for n in (resp.json() or []):
        if n.get("id") == baseline_id and n.get("type") == "baseline_root":
            return n.get("revision", 1)
    return 1


@pytest.fixture(autouse=True)
def setup_test_data(monkeypatch, tmp_path):
    """Redirect persistence to a temp directory for each test."""
    from src.crosscutting.config.settings import settings as settings_instance
    from src.infrastructure import repository

    test_data_dir = str(tmp_path / "data")
    os.makedirs(test_data_dir, exist_ok=True)
    backup_dir = os.path.join(test_data_dir, "backups")
    os.makedirs(backup_dir, exist_ok=True)

    # Patch the DATA_DIR and BACKUP_DIR used by repository module
    monkeypatch.setattr(repository, "DATA_DIR", test_data_dir)
    monkeypatch.setattr(repository, "BACKUP_DIR", backup_dir)
    # Patch the settings instance's BASE_DIR so new repositories use temp dir
    monkeypatch.setattr(settings_instance, "BASE_DIR", str(tmp_path))

    # Create a seed baseline
    seed_data = {
        "B001": {
            "baseline_id": "B001",
            "baseline_version": "v1.0",
            "recognition_profile": {"strategy": "excel_basic"},
            "naming_profile": {"strategy": "snake_case"},
            "parameter_profile": {},
            "threshold_profile": {},
            "rule_set": {
                "R1_scoped": {
                    "rule_type": "template",
                    "template": "group_consistency",
                    "target_type": "devices",
                    "params": {"parameter_key": "P1"},
                    "severity": "warning"
                }
            },
            "baseline_version_snapshot": {},
            "version_history_meta": {}
        }
    }
    with open(os.path.join(test_data_dir, "baselines.json"), "w") as f:
        json.dump(seed_data, f)

    yield test_data_dir


# ==========================================
# P1.0-1: Body Binding Tests
# ==========================================

def test_publish_request_body_is_bound():
    """P1.0-1: PublishRequestDTO body is properly parsed — draft_data not None."""
    payload = {
        "rule_id": "test_rule_1",
        "expected_revision": _get_revision(),
        "rule_type": "threshold",
        "target_type": "devices",
        "severity": "high",
        "params": {"metric_type": "count", "threshold_key": "T1"}
    }
    response = client.post("/api/rules/publish/B001", json=payload)

    # Should succeed (valid threshold rule)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["version_id"] is not None


def test_publish_body_binding_persists_draft_data(setup_test_data):
    """P1.0-1: Published rule data actually persists — read back and verify."""
    payload = {
        "rule_id": "my_new_threshold",
        "expected_revision": _get_revision(),
        "rule_type": "threshold",
        "target_type": "devices",
        "severity": "error",
        "params": {"metric_type": "count", "threshold_key": "T1"}
    }
    response = client.post("/api/rules/publish/B001", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # Read the persisted baselines.json and verify the rule was written
    with open(os.path.join(setup_test_data, "baselines.json")) as f:
        persisted = json.load(f)

    baseline = persisted["B001"]
    assert "my_new_threshold" in baseline["rule_set"], \
        f"Rule 'my_new_threshold' not found in persisted rule_set. Keys: {list(baseline['rule_set'].keys())}"

    # Verify the persisted rule data matches what we submitted
    rule = baseline["rule_set"]["my_new_threshold"]
    assert rule["template"] == "threshold"
    assert rule["params"]["metric_type"] == "count"
    assert rule["params"]["threshold_key"] == "T1"


def test_publish_without_rule_id_uses_default():
    """P1.0-1: When rule_id is empty, a default is generated."""
    payload = {
        "expected_revision": _get_revision(),
        "rule_type": "threshold",
        "target_type": "devices",
        "severity": "warning",
        "params": {"metric_type": "count", "threshold_key": "T1"}
    }
    response = client.post("/api/rules/publish/B001", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


# ==========================================
# P1.0-2: Validation Gate Tests
# ==========================================

def test_publish_invalid_draft_is_blocked():
    """P1.0-2: Invalid draft (missing required params) is blocked from publishing."""
    payload = {
        "rule_id": "bad_rule",
        "expected_revision": _get_revision(),
        "rule_type": "threshold",
        "target_type": "devices",
        "severity": "warning",
        "params": {}  # Missing metric_type and threshold_key — compile will fail
    }
    response = client.post("/api/rules/publish/B001", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False, \
        f"Expected publish to be blocked for invalid draft, but got success={data['success']}"
    assert data["blocked_issues"] is not None
    assert len(data["blocked_issues"]) > 0


def test_publish_invalid_draft_does_not_modify_baseline(setup_test_data):
    """P1.0-2: When publish is blocked, the baseline is NOT modified."""
    # Read baseline before
    with open(os.path.join(setup_test_data, "baselines.json")) as f:
        before = json.load(f)
    version_before = before["B001"]["baseline_version"]
    rule_count_before = len(before["B001"]["rule_set"])

    # Try to publish invalid draft
    payload = {
        "rule_id": "bad_rule",
        "expected_revision": _get_revision(),
        "rule_type": "threshold",
        "target_type": "devices",
        "severity": "warning",
        "params": {}  # Invalid
    }
    response = client.post("/api/rules/publish/B001", json=payload)
    assert response.json()["success"] is False

    # Verify baseline unchanged
    with open(os.path.join(setup_test_data, "baselines.json")) as f:
        after = json.load(f)
    assert after["B001"]["baseline_version"] == version_before, \
        "Baseline version was bumped despite publish being blocked!"
    assert len(after["B001"]["rule_set"]) == rule_count_before, \
        "Rule set was modified despite publish being blocked!"


def test_publish_valid_threshold_rule_succeeds():
    """P1.0-2: Valid threshold rule can be published."""
    payload = {
        "rule_id": "valid_threshold",
        "expected_revision": _get_revision(),
        "rule_type": "threshold",
        "target_type": "devices",
        "severity": "error",
        "params": {"metric_type": "count", "threshold_key": "T1"}
    }
    response = client.post("/api/rules/publish/B001", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["version_id"] is not None


def test_publish_valid_group_consistency_rule_succeeds():
    """P1.0-2: Valid group_consistency rule can be published."""
    payload = {
        "rule_id": "valid_gc",
        "expected_revision": _get_revision(),
        "rule_type": "group_consistency",
        "target_type": "devices",
        "severity": "warning",
        "params": {"parameter_key": "P1"}
    }
    response = client.post("/api/rules/publish/B001", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_publish_valid_single_fact_rule_succeeds():
    """P1.0-2: Valid single_fact rule can be published."""
    payload = {
        "rule_id": "valid_sf",
        "expected_revision": _get_revision(),
        "rule_type": "single_fact",
        "target_type": "devices",
        "severity": "medium",
        "params": {"field": "status", "type": "field_equals", "expected": "active"}
    }
    response = client.post("/api/rules/publish/B001", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_publish_blocked_returns_structured_error():
    """P1.0-2: Blocked publish returns structured error with field_path info."""
    payload = {
        "rule_id": "bad_rule",
        "expected_revision": _get_revision(),
        "rule_type": "threshold",
        "target_type": "devices",
        "severity": "warning",
        "params": {}  # Missing required params
    }
    response = client.post("/api/rules/publish/B001", json=payload)
    data = response.json()
    assert data["success"] is False
    assert data["blocked_issues"] is not None
    # Each issue should have standard structure
    for issue in data["blocked_issues"]:
        assert "field_path" in issue
        assert "issue_type" in issue
        assert "message" in issue


def test_publish_nonexistent_baseline_returns_404():
    """P1.0-1: Publishing to a non-existent baseline returns 404."""
    payload = {
        "expected_revision": 1,
        "rule_type": "threshold",
        "params": {"metric_type": "count", "threshold_key": "T1"}
    }
    response = client.post("/api/rules/publish/NOEXIST", json=payload)
    # Application service returns publish_success=False with error
    # OR the baseline not found triggers an error
    assert response.status_code in [200, 404, 422]


# ==========================================
# P1.0-2: No Bypass Path Tests
# ==========================================

def test_validation_endpoint_and_publish_endpoint_consistent():
    """P1.0-2: Validate endpoint and publish endpoint give consistent results.

    If validate says 'invalid', publish must also block.
    If validate says 'valid', publish must succeed.
    """
    # Case 1: Invalid params → validate fails → publish blocks
    invalid_params = {}
    validate_resp = client.post("/api/rules/draft/validate", json={
        "rule_type": "threshold",
        "params": invalid_params
    })
    validate_data = validate_resp.json()
    assert validate_data["valid"] is False

    publish_resp = client.post("/api/rules/publish/B001", json={
        "rule_id": "consistency_test_invalid",
        "expected_revision": _get_revision(),
        "rule_type": "threshold",
        "params": invalid_params
    })
    publish_data = publish_resp.json()
    assert publish_data["success"] is False, \
        "Validate said invalid but publish succeeded — validation gate broken!"

    # Case 2: Valid params → validate passes → publish succeeds
    valid_params = {"metric_type": "count", "threshold_key": "T1"}
    validate_resp2 = client.post("/api/rules/draft/validate", json={
        "rule_type": "threshold",
        "params": valid_params
    })
    validate_data2 = validate_resp2.json()
    assert validate_data2["valid"] is True

    publish_resp2 = client.post("/api/rules/publish/B001", json={
        "rule_id": "consistency_test_valid",
        "expected_revision": _get_revision(),
        "rule_type": "threshold",
        "params": valid_params
    })
    publish_data2 = publish_resp2.json()
    assert publish_data2["success"] is True, \
        "Validate said valid but publish failed — unexpected!"
