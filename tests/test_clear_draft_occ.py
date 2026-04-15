import os
import json
import pytest
from fastapi.testclient import TestClient
from src.presentation.api.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_isolated_data_dir(monkeypatch, tmp_path):
    from src.crosscutting.config.settings import settings as settings_instance
    from src.infrastructure import repository

    test_data_dir = str(tmp_path / "data")
    os.makedirs(test_data_dir, exist_ok=True)
    backup_dir = os.path.join(test_data_dir, "backups")
    os.makedirs(backup_dir, exist_ok=True)

    monkeypatch.setattr(repository, "DATA_DIR", test_data_dir)
    monkeypatch.setattr(repository, "BACKUP_DIR", backup_dir)
    monkeypatch.setattr(settings_instance, "BASE_DIR", str(tmp_path))

    with open(os.path.join(test_data_dir, "baselines.json"), "w") as f:
        json.dump({"__schema_version__": "1.2"}, f)

    yield


def _get_revision(baseline_id: str = "B001") -> int:
    resp = client.get("/api/baselines")
    assert resp.status_code == 200
    for n in resp.json():
        if n.get("id") == baseline_id and n.get("type") == "baseline_root":
            return n.get("revision", 1)
    return 1


def test_clear_draft_stale_token_returns_409():
    client.post("/api/baselines/bootstrap-default")
    rev = _get_revision("B001")

    save_payload = {
        "baseline_id": "B001",
        "expected_revision": rev,
        "rule_id": "r1",
        "rule_type": "threshold",
        "target_type": "devices",
        "severity": "warning",
        "params": {"metric_type": "count", "threshold_key": "T1"},
    }
    save_resp = client.post("/api/rules/draft/save", json=save_payload)
    assert save_resp.status_code == 200
    new_rev = save_resp.json().get("new_revision")
    assert new_rev == rev + 1

    stale_clear = client.delete(f"/api/rules/draft/B001?expected_revision={rev}")
    assert stale_clear.status_code == 409
    assert stale_clear.json()["error_code"] == "P1009"


def test_clear_draft_valid_token_happy_path():
    client.post("/api/baselines/bootstrap-default")
    rev = _get_revision("B001")

    save_resp = client.post("/api/rules/draft/save", json={
        "baseline_id": "B001",
        "expected_revision": rev,
        "rule_id": "r1",
        "rule_type": "threshold",
        "target_type": "devices",
        "severity": "warning",
        "params": {"metric_type": "count", "threshold_key": "T1"},
    })
    assert save_resp.status_code == 200
    updated_rev = save_resp.json().get("new_revision")

    clear_resp = client.delete(f"/api/rules/draft/B001?expected_revision={updated_rev}")
    assert clear_resp.status_code == 200
    data = clear_resp.json()
    assert data["success"] is True

    load_resp = client.get("/api/rules/draft/B001")
    assert load_resp.status_code == 200
    assert load_resp.json()["has_draft"] is False

