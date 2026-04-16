import os
import pytest

from src.application.baseline_services.baseline_service import BaselineService
from src.infrastructure.repository import BaselineRepository
import src.infrastructure.repository as repository
from src.crosscutting.config.settings import settings as settings_instance


@pytest.fixture
def isolated_data_dir(tmp_path, monkeypatch):
    test_data_dir = str(tmp_path / "data")
    test_backup_dir = str(tmp_path / "data" / "backups")
    os.makedirs(test_backup_dir, exist_ok=True)

    monkeypatch.setattr(repository, "DATA_DIR", test_data_dir)
    monkeypatch.setattr(repository, "BACKUP_DIR", test_backup_dir)
    monkeypatch.setattr(settings_instance, "BASE_DIR", str(tmp_path))

    yield tmp_path


def test_list_baselines_is_read_only_when_empty(isolated_data_dir):
    repo = BaselineRepository()
    svc = BaselineService(repo)
    baselines = svc.list_baselines()

    assert baselines == []
    assert not os.path.exists(os.path.join(repository.DATA_DIR, "baselines.json"))


def test_bootstrap_default_is_explicit_and_idempotent(isolated_data_dir):
    repo = BaselineRepository()
    svc = BaselineService(repo)

    b1 = svc.bootstrap_default_baseline()
    b2 = svc.bootstrap_default_baseline()

    assert b1.baseline_id == "B001"
    assert b2.baseline_id == "B001"

    baselines = svc.list_baselines()
    assert len(baselines) == 1
    assert baselines[0].baseline_id == "B001"

