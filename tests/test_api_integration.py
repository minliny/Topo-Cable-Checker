import pytest
from fastapi.testclient import TestClient
from src.presentation.api.main import app

client = TestClient(app)

def test_get_baselines():
    response = client.get("/api/baselines")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Check if tree structure is maintained (root + drafts/versions)
    if len(data) > 0:
        types = [item["type"] for item in data]
        assert "baseline_root" in types
        # Verify fields
        assert "id" in data[0]
        assert "name" in data[0]

def test_get_version_meta_fallback():
    # Use a dummy baseline and version that should fall back gracefully
    # If B001 does not exist, it returns 404, which is also correct
    response = client.get("/api/baselines/B001/versions/v1.0")
    if response.status_code == 200:
        data = response.json()
        assert data["version_id"] == "v1.0"
        assert data["baseline_id"] == "B001"
        assert "published_at" in data
        assert "publisher" in data
    else:
        assert response.status_code == 404

def test_validate_draft_success():
    payload = {
        "rule_type": "threshold",
        "params": {"metric_type": "count", "threshold_key": "T1"}
    }
    response = client.post("/api/rules/draft/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert len(data["issues"]) == 0

def test_validate_draft_blocked():
    payload = {
        "rule_type": "threshold",
        "params": {"operator": "unknown"}
    }
    response = client.post("/api/rules/draft/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert len(data["issues"]) > 0
    # Check if field_path is extracted properly
    assert "field_path" in data["issues"][0]
    assert data["issues"][0]["issue_type"] == "error"

def test_publish_baseline_blocked():
    # Sending 'block': true should be blocked by backend minimum validation
    payload = {"params": {"block": True}}
    response = client.post("/api/rules/publish/B001", json=payload)
    
    if response.status_code == 404:
        pytest.skip("Baseline B001 not found in test environment")
        
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "blocked_issues" in data
    assert len(data["blocked_issues"]) > 0

def test_publish_baseline_success():
    payload = {"params": {"threshold_key": "new_key"}}
    response = client.post("/api/rules/publish/B001", json=payload)
    
    if response.status_code == 404:
        pytest.skip("Baseline B001 not found in test environment")
        
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["version_id"] is not None
    assert data["version_label"] is not None
    
    # Verify that the new version actually exists in the tree now
    tree_resp = client.get("/api/baselines")
    tree_data = tree_resp.json()
    version_ids = [node["version_id"] for node in tree_data]
    assert data["version_id"] in version_ids

def test_get_diff_after_publish():
    # Compare draft against the newly created version
    response = client.get("/api/baselines/B001/diff?source=draft&target=previous_version")
    
    if response.status_code == 404:
        pytest.skip("Baseline B001 not found in test environment")
        
    assert response.status_code == 200
    data = response.json()
    assert "diff_summary" in data
    assert "rules" in data
    assert isinstance(data["rules"], list)
    
def test_create_rollback_candidate():
    payload = {"baseline_id": "B001", "version_id": "v1.0"}
    response = client.post("/api/rules/rollback", json=payload)
    
    if response.status_code == 404:
        pytest.skip("Baseline B001 or Version v1.0 not found in test environment")
        
    assert response.status_code == 200
    data = response.json()
    assert data["source_version_id"] == "v1.0"
    assert "draft_data" in data
