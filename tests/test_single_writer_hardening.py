import os
import json
import time
import multiprocessing as mp
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


def _lock_worker(lock_path: str, ready: mp.Event, hold_s: float):
    import fcntl

    os.makedirs(os.path.dirname(lock_path), exist_ok=True)
    f = open(lock_path, "a+")
    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
    ready.set()
    time.sleep(hold_s)
    try:
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception:
        pass
    try:
        f.close()
    except Exception:
        pass


def test_single_writer_lock_timeout_returns_423(setup_isolated_data_dir, monkeypatch):
    from src.infrastructure import repository

    lock_path = os.path.join(repository.DATA_DIR, "baselines.json.lock")

    client.post("/api/baselines/bootstrap-default")
    rev = client.get("/api/rules/draft/B001").json()["base_revision"]

    ready = mp.Event()
    p = mp.Process(target=_lock_worker, args=(lock_path, ready, 2.0))
    p.start()
    try:
        assert ready.wait(timeout=2.0) is True

        monkeypatch.setattr(repository, "BASELINES_LOCK_TIMEOUT_S", 0.1, raising=False)

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

        assert resp.status_code == 423
        body = resp.json()
        assert body["error_code"] == "P1010"
    finally:
        p.terminate()
        p.join(timeout=2.0)
