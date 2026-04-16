import os
import pytest

import src.infrastructure.repository as repository
from src.infrastructure.repository import BaselineRepository


def test_baseline_repository_save_rejects_dict_profile(tmp_path, monkeypatch):
    monkeypatch.setattr(repository, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(repository, "BACKUP_DIR", os.path.join(str(tmp_path), "backups"))

    repo = BaselineRepository()

    with pytest.raises(TypeError):
        repo.save({"baseline_id": "B001", "revision": 1}, expected_revision=0)
