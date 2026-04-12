"""
P1.1-3: Tests for schema version & migration safety.

Validates:
1. Data without schema_version is treated as v0 and auto-migrated
2. Data with migratable version is auto-migrated and stamped
3. Data with unsupported/too-new version fails with clear error
4. Migrated data persists with correct schema_version
5. Same-version data passes through without migration
"""

import os
import json
import pytest
from src.infrastructure.repository import (
    _apply_schema_migration, BASELINES_SCHEMA_VERSION, BASELINES_MIGRATIONS,
    BaselineRepository, _read_json, _write_json
)
from src.crosscutting.errors.exceptions import PersistenceSchemaError


class TestSchemaMigrationCore:
    """Unit tests for _apply_schema_migration function."""

    def test_no_schema_version_treated_as_v0(self):
        """Data without __schema_version__ should be treated as v0 and migrated."""
        data = {
            "B001": {
                "baseline_id": "B001",
                "baseline_version": "v1.0",
                "recognition_profile": {"strategy": "excel_basic"},
                "naming_profile": {"strategy": "snake_case"},
                "rule_set": {"R1": {"params": {"key": "val"}}}
            }
        }
        result = _apply_schema_migration(
            "baselines.json", data, BASELINES_SCHEMA_VERSION,
            BASELINES_MIGRATIONS, "__schema_version__"
        )
        # Should be migrated to current version
        assert result["__schema_version__"] == BASELINES_SCHEMA_VERSION
        # Should have added version_history_meta and rule_type
        assert "version_history_meta" in result["B001"]
        assert result["B001"]["rule_set"]["R1"]["rule_type"] == "template"

    def test_same_version_no_migration(self):
        """Data at current schema version should pass through unchanged."""
        data = {
            "__schema_version__": BASELINES_SCHEMA_VERSION,
            "B001": {
                "baseline_id": "B001",
                "baseline_version": "v1.0",
                "recognition_profile": {},
                "naming_profile": {},
            }
        }
        result = _apply_schema_migration(
            "baselines.json", data, BASELINES_SCHEMA_VERSION,
            BASELINES_MIGRATIONS, "__schema_version__"
        )
        assert result["__schema_version__"] == BASELINES_SCHEMA_VERSION
        # Should be exactly the same object
        assert result is data

    def test_too_new_version_fails(self):
        """Data with a newer schema version than code should fail."""
        data = {
            "__schema_version__": "99.0",
            "B001": {"baseline_id": "B001"}
        }
        with pytest.raises(PersistenceSchemaError) as exc_info:
            _apply_schema_migration(
                "baselines.json", data, BASELINES_SCHEMA_VERSION,
                BASELINES_MIGRATIONS, "__schema_version__"
            )
        assert "newer" in str(exc_info.value).lower() or "99.0" in str(exc_info.value)

    def test_unsupported_version_no_path_fails(self):
        """Data at a version with no migration path should fail."""
        data = {
            "__schema_version__": "0.5",  # No migration from 0.5 to anything
        }
        # This should fail because there's no migration from "0.5"
        with pytest.raises(PersistenceSchemaError):
            _apply_schema_migration(
                "baselines.json", data, BASELINES_SCHEMA_VERSION,
                BASELINES_MIGRATIONS, "__schema_version__"
            )

    def test_step_migration_v0_to_v1_to_v1_1(self):
        """Data at v0 should be migrated step by step: v0 → v1.0 → v1.1."""
        data = {
            "B001": {
                "baseline_id": "B001",
                "baseline_version": "v1.0",
                "recognition_profile": {},
                "naming_profile": {},
                "rule_set": {
                    "R1": {"params": {"key": "val"}}  # Missing rule_type
                },
                "baseline_version_snapshot": {
                    "v0.9": "some_string_snapshot"  # String instead of dict
                }
            }
        }
        result = _apply_schema_migration(
            "baselines.json", data, BASELINES_SCHEMA_VERSION,
            BASELINES_MIGRATIONS, "__schema_version__"
        )
        
        # Should be at current version
        assert result["__schema_version__"] == BASELINES_SCHEMA_VERSION
        
        # v0 → v1.0: version_history_meta should be added
        assert "version_history_meta" in result["B001"]
        
        # v0 → v1.0: snapshot string should be normalized
        assert isinstance(result["B001"]["baseline_version_snapshot"]["v0.9"], dict)
        
        # v1.0 → v1.1: rule_type should be added
        assert result["B001"]["rule_set"]["R1"]["rule_type"] == "template"


class TestSchemaMigrationIntegration:
    """Integration tests for BaselineRepository with schema migration."""

    @pytest.fixture(autouse=True)
    def setup_test_data(self, monkeypatch, tmp_path):
        """Redirect persistence to a temp directory."""
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

    def test_read_old_data_auto_migrates(self, tmp_path):
        """Reading pre-schema baselines.json auto-migrates and returns correct profiles."""
        test_data_dir = str(tmp_path / "data")
        
        # Write old-format data without schema_version
        old_data = {
            "B001": {
                "baseline_id": "B001",
                "baseline_version": "v1.0",
                "recognition_profile": {"strategy": "excel_basic"},
                "naming_profile": {"strategy": "snake_case"},
                "rule_set": {"R1": {"params": {"key": "val"}}}
            }
        }
        with open(os.path.join(test_data_dir, "baselines.json"), "w") as f:
            json.dump(old_data, f)

        repo = BaselineRepository()
        profiles = repo.get_all()
        
        assert len(profiles) >= 1
        # Migration should have added version_history_meta and rule_type
        assert profiles[0].version_history_meta == {}
        assert profiles[0].rule_set["R1"]["rule_type"] == "template"
        
        # After saving any profile, the file should have __schema_version__
        repo.save(profiles[0])
        with open(os.path.join(test_data_dir, "baselines.json"), "r") as f:
            persisted = json.load(f)
        assert persisted["__schema_version__"] == BASELINES_SCHEMA_VERSION

    def test_save_stamps_schema_version(self, tmp_path):
        """Saving a baseline stamps the current schema version."""
        test_data_dir = str(tmp_path / "data")
        
        # Start with empty baselines
        with open(os.path.join(test_data_dir, "baselines.json"), "w") as f:
            json.dump({}, f)

        from src.domain.baseline_model import BaselineProfile
        repo = BaselineRepository()
        profile = BaselineProfile(
            baseline_id="B002",
            baseline_version="v1.0",
            recognition_profile={},
            naming_profile={},
        )
        repo.save(profile)

        with open(os.path.join(test_data_dir, "baselines.json"), "r") as f:
            persisted = json.load(f)
        assert persisted["__schema_version__"] == BASELINES_SCHEMA_VERSION
        assert "B002" in persisted

    def test_newer_schema_version_fails_on_read(self, tmp_path):
        """Data with a newer schema version should fail to read."""
        test_data_dir = str(tmp_path / "data")
        
        future_data = {
            "__schema_version__": "99.0",
            "B001": {"baseline_id": "B001", "baseline_version": "v1.0",
                      "recognition_profile": {}, "naming_profile": {}}
        }
        with open(os.path.join(test_data_dir, "baselines.json"), "w") as f:
            json.dump(future_data, f)

        repo = BaselineRepository()
        with pytest.raises(PersistenceSchemaError):
            repo.get_all()

    def test_migrated_data_matches_current_schema(self, tmp_path):
        """After migration, data should be compatible with current BaselineProfile."""
        test_data_dir = str(tmp_path / "data")
        
        # Old data with missing fields
        old_data = {
            "B001": {
                "baseline_id": "B001",
                "baseline_version": "v1.0",
                "recognition_profile": {"strategy": "excel_basic"},
                "naming_profile": {"strategy": "snake_case"},
                "rule_set": {"R1": {"params": {"key": "val"}}}
            }
        }
        with open(os.path.join(test_data_dir, "baselines.json"), "w") as f:
            json.dump(old_data, f)

        repo = BaselineRepository()
        # get_by_id should work without error after migration
        profile = repo.get_by_id("B001")
        assert profile is not None
        assert profile.baseline_id == "B001"
        # Migration should have added rule_type
        assert profile.rule_set["R1"]["rule_type"] == "template"
