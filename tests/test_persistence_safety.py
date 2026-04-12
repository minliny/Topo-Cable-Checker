"""
P0-2/P0-3: Persistence Safety & Backup Tests

Verifies:
- Corrupted JSON files are NOT silently swallowed (no more returning {})
- Corrupted files are preserved for forensic analysis
- Automatic recovery from backup when corruption detected
- Rolling backup mechanism works correctly
- Backup pruning limits disk usage
"""

import json
import os
import pytest
import tempfile
import shutil
from src.infrastructure.repository import (
    _read_json, _write_json, _backup_file, _prune_old_backups,
    _get_latest_backup, _preserve_corrupted_file,
    DATA_DIR, BACKUP_DIR, MAX_BACKUPS
)
from src.crosscutting.errors.exceptions import (
    PersistenceCorruptionError, PersistenceRecoveryError
)


class TestCorruptionDetection:
    """P0-2: Corrupted JSON must never be silently swallowed."""

    def test_corrupted_file_raises_not_empty_dict(self, tmp_path, monkeypatch):
        """When a JSON file is corrupted, _read_json must NOT return {}."""
        # Redirect DATA_DIR to temp
        monkeypatch.setattr("src.infrastructure.repository.DATA_DIR", str(tmp_path))
        monkeypatch.setattr("src.infrastructure.repository.BACKUP_DIR", str(tmp_path / "backups"))
        os.makedirs(str(tmp_path / "backups"), exist_ok=True)

        # Write corrupted JSON
        corrupted_file = tmp_path / "test_corrupt.json"
        corrupted_file.write_text("{ this is not valid json }}}", encoding="utf-8")

        # Must raise, not return {}
        with pytest.raises(PersistenceCorruptionError) as exc_info:
            _read_json("test_corrupt.json")

        assert "corrupted" in str(exc_info.value).lower()
        # Original file should have been preserved as .corrupted
        corrupted_copies = list(tmp_path.glob("test_corrupt.json.corrupted.*"))
        assert len(corrupted_copies) == 1, "Corrupted file should be preserved"

    def test_nonexistent_file_returns_empty_dict(self, tmp_path, monkeypatch):
        """When file does not exist, {} is the correct behavior."""
        monkeypatch.setattr("src.infrastructure.repository.DATA_DIR", str(tmp_path))
        monkeypatch.setattr("src.infrastructure.repository.BACKUP_DIR", str(tmp_path / "backups"))
        os.makedirs(str(tmp_path / "backups"), exist_ok=True)

        result = _read_json("nonexistent.json")
        assert result == {}

    def test_valid_file_returns_data(self, tmp_path, monkeypatch):
        """Valid JSON file returns parsed data."""
        monkeypatch.setattr("src.infrastructure.repository.DATA_DIR", str(tmp_path))
        monkeypatch.setattr("src.infrastructure.repository.BACKUP_DIR", str(tmp_path / "backups"))
        os.makedirs(str(tmp_path / "backups"), exist_ok=True)

        test_data = {"key1": "value1", "key2": 42}
        valid_file = tmp_path / "valid.json"
        valid_file.write_text(json.dumps(test_data), encoding="utf-8")

        result = _read_json("valid.json")
        assert result == test_data


class TestBackupRecovery:
    """P0-2/P0-3: Corrupted file triggers automatic recovery from backup."""

    def test_recovery_from_backup_on_corruption(self, tmp_path, monkeypatch):
        """When primary file is corrupted but backup exists, recover from backup."""
        monkeypatch.setattr("src.infrastructure.repository.DATA_DIR", str(tmp_path))
        monkeypatch.setattr("src.infrastructure.repository.BACKUP_DIR", str(tmp_path / "backups"))
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir(exist_ok=True)

        # Create a valid backup
        good_data = {"baseline": "v1", "rules": {"r1": {"type": "threshold"}}}
        backup_file = backup_dir / "test_recover.json.bak.20260411_120000_000000"
        backup_file.write_text(json.dumps(good_data), encoding="utf-8")

        # Create a corrupted primary file
        primary_file = tmp_path / "test_recover.json"
        primary_file.write_text("{{{corrupted", encoding="utf-8")

        # _read_json should recover from backup
        result = _read_json("test_recover.json")
        assert result == good_data

        # Primary file should now contain recovered data
        recovered = json.loads(primary_file.read_text(encoding="utf-8"))
        assert recovered == good_data

    def test_corruption_with_no_backup_raises(self, tmp_path, monkeypatch):
        """When primary file is corrupted and no backup exists, raise PersistenceCorruptionError."""
        monkeypatch.setattr("src.infrastructure.repository.DATA_DIR", str(tmp_path))
        monkeypatch.setattr("src.infrastructure.repository.BACKUP_DIR", str(tmp_path / "backups"))
        os.makedirs(str(tmp_path / "backups"), exist_ok=True)

        # Create only a corrupted primary file, no backups
        primary_file = tmp_path / "no_backup.json"
        primary_file.write_text("bad json {{{", encoding="utf-8")

        with pytest.raises(PersistenceCorruptionError):
            _read_json("no_backup.json")

    def test_corrupted_backup_also_raises(self, tmp_path, monkeypatch):
        """When both primary and backup are corrupted, raise PersistenceRecoveryError."""
        monkeypatch.setattr("src.infrastructure.repository.DATA_DIR", str(tmp_path))
        monkeypatch.setattr("src.infrastructure.repository.BACKUP_DIR", str(tmp_path / "backups"))
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir(exist_ok=True)

        # Corrupted backup
        backup_file = backup_dir / "both_bad.json.bak.20260411_120000_000000"
        backup_file.write_text("also broken {{{", encoding="utf-8")

        # Corrupted primary
        primary_file = tmp_path / "both_bad.json"
        primary_file.write_text("bad json {{{", encoding="utf-8")

        with pytest.raises(PersistenceRecoveryError):
            _read_json("both_bad.json")


class TestRollingBackup:
    """P0-3: Rolling backup mechanism."""

    def test_write_creates_backup(self, tmp_path, monkeypatch):
        """_write_json creates a backup of the previous version."""
        monkeypatch.setattr("src.infrastructure.repository.DATA_DIR", str(tmp_path))
        monkeypatch.setattr("src.infrastructure.repository.BACKUP_DIR", str(tmp_path / "backups"))
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir(exist_ok=True)

        # Write initial data
        _write_json("test_backup.json", {"version": 1})
        # Write again (should create backup of version 1)
        _write_json("test_backup.json", {"version": 2})

        # Backup should exist
        backups = list(backup_dir.glob("test_backup.json.bak.*"))
        assert len(backups) >= 1, "At least one backup should exist"

        # Backup should contain version 1
        backup_data = json.loads(backups[0].read_text(encoding="utf-8"))
        assert backup_data["version"] == 1

    def test_multiple_writes_create_multiple_backups(self, tmp_path, monkeypatch):
        """Multiple writes create multiple backup files."""
        monkeypatch.setattr("src.infrastructure.repository.DATA_DIR", str(tmp_path))
        monkeypatch.setattr("src.infrastructure.repository.BACKUP_DIR", str(tmp_path / "backups"))
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir(exist_ok=True)

        for i in range(3):
            _write_json("test_multi.json", {"version": i})

        backups = sorted(backup_dir.glob("test_multi.json.bak.*"))
        assert len(backups) == 2, f"Expected 2 backups (original + 2 writes), got {len(backups)}"

    def test_backup_pruning_limits_count(self, tmp_path, monkeypatch):
        """Old backups beyond MAX_BACKUPS are pruned."""
        monkeypatch.setattr("src.infrastructure.repository.DATA_DIR", str(tmp_path))
        monkeypatch.setattr("src.infrastructure.repository.BACKUP_DIR", str(tmp_path / "backups"))
        monkeypatch.setattr("src.infrastructure.repository.MAX_BACKUPS", 3)
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir(exist_ok=True)

        # Write more than MAX_BACKUPS times
        for i in range(6):
            _write_json("test_prune.json", {"version": i})

        backups = list(backup_dir.glob("test_prune.json.bak.*"))
        assert len(backups) <= 3, f"Should have at most 3 backups, got {len(backups)}"

    def test_latest_backup_found_correctly(self, tmp_path, monkeypatch):
        """_get_latest_backup finds the most recent backup."""
        monkeypatch.setattr("src.infrastructure.repository.DATA_DIR", str(tmp_path))
        monkeypatch.setattr("src.infrastructure.repository.BACKUP_DIR", str(tmp_path / "backups"))
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir(exist_ok=True)

        # Create backups with timestamps
        for ts in ["20260411_100000", "20260411_110000", "20260411_120000"]:
            f = backup_dir / f"test_latest.json.bak.{ts}_000000"
            f.write_text('{"version": "old"}', encoding="utf-8")

        latest = _get_latest_backup("test_latest.json")
        assert latest is not None
        assert "120000" in latest


class TestCorruptedFilePreservation:
    """P0-2: Corrupted files are preserved for forensic analysis."""

    def test_corrupted_file_preserved_on_read(self, tmp_path, monkeypatch):
        """When corruption detected during read, file is renamed to .corrupted."""
        monkeypatch.setattr("src.infrastructure.repository.DATA_DIR", str(tmp_path))
        monkeypatch.setattr("src.infrastructure.repository.BACKUP_DIR", str(tmp_path / "backups"))
        os.makedirs(str(tmp_path / "backups"), exist_ok=True)

        # Write corrupted content
        bad_file = tmp_path / "forensic.json"
        bad_file.write_text("NOT JSON AT ALL", encoding="utf-8")

        with pytest.raises(PersistenceCorruptionError):
            _read_json("forensic.json")

        # Original file should be gone (renamed)
        assert not bad_file.exists(), "Original corrupted file should be renamed"

        # Corrupted copy should exist
        corrupted = list(tmp_path.glob("forensic.json.corrupted.*"))
        assert len(corrupted) == 1
        assert corrupted[0].read_text(encoding="utf-8") == "NOT JSON AT ALL"
