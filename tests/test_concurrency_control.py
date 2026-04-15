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


def _get_baseline_revision(baseline_id: str) -> int:
    resp = client.get("/api/baselines")
    assert resp.status_code == 200
    for n in resp.json():
        if n.get("id") == baseline_id and n.get("type") == "baseline_root":
            return n.get("revision", 1)
    return 1


def test_stale_draft_save_returns_409():
    client.post("/api/baselines/bootstrap-default")
    rev = _get_baseline_revision("B001")

    payload = {
        "baseline_id": "B001",
        "expected_revision": rev,
        "rule_id": "r1",
        "rule_type": "threshold",
        "target_type": "devices",
        "severity": "warning",
        "params": {"metric_type": "count", "threshold_key": "T1"},
    }
    ok = client.post("/api/rules/draft/save", json=payload)
    assert ok.status_code == 200
    new_rev = ok.json().get("new_revision")
    assert new_rev == rev + 1

    stale = client.post("/api/rules/draft/save", json=payload)
    assert stale.status_code == 409
    body = stale.json()
    assert body["error_code"] == "P1009"


def test_stale_publish_returns_409():
    client.post("/api/baselines/bootstrap-default")
    rev = _get_baseline_revision("B001")

    payload = {
        "rule_id": "rule_x",
        "expected_revision": rev,
        "rule_type": "threshold",
        "target_type": "devices",
        "severity": "warning",
        "params": {"metric_type": "count", "threshold_key": "T1"},
    }

    ok = client.post("/api/rules/publish/B001", json=payload)
    assert ok.status_code == 200
    assert ok.json()["success"] is True

    stale = client.post("/api/rules/publish/B001", json=payload)
    assert stale.status_code == 409
    body = stale.json()
    assert body["error_code"] == "P1009"


def test_restore_draft_does_not_mutate_revision():
    client.post("/api/baselines/bootstrap-default")
    rev = _get_baseline_revision("B001")

    resp = client.post("/api/rules/restore-draft", json={"baseline_id": "B001", "version_id": "v1.0"})
    assert resp.status_code == 200
    assert _get_baseline_revision("B001") == rev
