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

    yield str(tmp_path)


def _events_path(base_dir: str) -> str:
    return os.path.join(base_dir, "data", "observations", "events.jsonl")


def _read_events(path: str):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f.read().splitlines() if line.strip()]


def test_draft_save_records_event(setup_isolated_data_dir):
    base_dir = setup_isolated_data_dir
    client.post("/api/baselines/bootstrap-default")

    rev = client.get("/api/rules/draft/B001").json()["base_revision"]
    resp = client.post(
        "/api/rules/draft/save",
        headers={"X-Actor": "test-user"},
        json={
            "baseline_id": "B001",
            "expected_revision": rev,
            "rule_id": "r1",
            "rule_type": "threshold",
            "target_type": "devices",
            "severity": "warning",
            "params": {"metric_type": "count", "threshold_key": "T1"},
        },
    )
    assert resp.status_code == 200

    events = _read_events(_events_path(base_dir))
    assert any(e["event_type"] == "draft_saved" and e["baseline_id"] == "B001" and e.get("actor") == "test-user" for e in events)


def test_record_event_is_best_effort_and_does_not_break_api(setup_isolated_data_dir, monkeypatch):
    from src.crosscutting.observation import recorder as rec

    def boom(*args, **kwargs):
        raise RuntimeError("disk full")

    monkeypatch.setattr(rec, "_append_line", boom)

    client.post("/api/baselines/bootstrap-default")
    rev = client.get("/api/rules/draft/B001").json()["base_revision"]
    resp = client.post(
        "/api/rules/draft/save",
        json={
            "baseline_id": "B001",
            "expected_revision": rev,
            "rule_id": "r1",
            "rule_type": "threshold",
            "target_type": "devices",
            "severity": "warning",
            "params": {"metric_type": "count", "threshold_key": "T1"},
        },
    )
    assert resp.status_code == 200


def test_event_log_rotates_when_exceeds_max_bytes(setup_isolated_data_dir, monkeypatch):
    from src.crosscutting.observation import recorder as rec

    base_dir = setup_isolated_data_dir
    monkeypatch.setattr(rec, "MAX_BYTES", 200)
    monkeypatch.setattr(rec, "BACKUP_COUNT", 2)

    client.post("/api/baselines/bootstrap-default")
    rev = client.get("/api/rules/draft/B001").json()["base_revision"]

    for i in range(20):
        resp = client.post(
            "/api/rules/draft/save",
            json={
                "baseline_id": "B001",
                "expected_revision": rev,
                "rule_id": f"r{i}",
                "rule_type": "threshold",
                "target_type": "devices",
                "severity": "warning",
                "params": {"metric_type": "count", "threshold_key": "T1"},
            },
        )
        assert resp.status_code in (200, 409)
        if resp.status_code == 200:
            rev = resp.json()["new_revision"]
        else:
            rev = client.get("/api/rules/draft/B001").json()["base_revision"]

    base = _events_path(base_dir)
    rotated = base + ".1"
    assert os.path.exists(base)
    assert os.path.exists(rotated)

