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

    yield test_data_dir


def test_bootstrap_default_is_create_if_absent_and_does_not_overwrite(setup_isolated_data_dir):
    baselines_path = os.path.join(setup_isolated_data_dir, "baselines.json")

    existing = {
        "__schema_version__": "1.2",
        "B001": {
            "baseline_id": "B001",
            "baseline_version": "v9.9",
            "recognition_profile": {"strategy": "custom"},
            "naming_profile": {"strategy": "custom"},
            "parameter_profile": {},
            "threshold_profile": {},
            "rule_set": {"marker_rule": {"rule_type": "template", "template": "single_fact", "params": {"field": "x", "type": "field_equals", "expected": "y"}}},
            "baseline_version_snapshot": {},
            "version_history_meta": {},
            "working_draft": {"rule_id": "draft_marker"},
            "revision": 7,
        }
    }

    with open(baselines_path, "w") as f:
        json.dump(existing, f)

    resp = client.post("/api/baselines/bootstrap-default")
    assert resp.status_code == 200

    with open(baselines_path, "r") as f:
        after = json.load(f)

    assert after["B001"]["baseline_version"] == "v9.9"
    assert after["B001"]["rule_set"] == existing["B001"]["rule_set"]
    assert after["B001"]["working_draft"] == existing["B001"]["working_draft"]
    assert after["B001"]["revision"] == 7

