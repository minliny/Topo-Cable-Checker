"""
P0-2/P0-3: Safe JSON Persistence with Corruption Detection & Rolling Backup
P1.1-3: Schema Version & Migration Safety

Key improvements over original:
1. _read_json: Fail-fast on corruption — raises PersistenceCorruptionError instead of returning {}
2. Corrupted files are preserved as .corrupted.<timestamp>.json for forensic analysis
3. Automatic recovery from most recent backup when corruption detected
4. Rolling backup: every _write_json creates a backup, keeps last N copies
5. All persistence errors are logged with file path and context
6. P1.1-3: Schema version identification + migration safety for baselines.json
"""

import json
import os
import tempfile
import shutil
import dataclasses
from typing import Any, Dict, List, Optional
from src.domain.task_model import CheckTask, TaskStatus
from src.domain.baseline_model import BaselineProfile
from src.domain.result_model import (
    RecognitionResultSnapshot, RunExecutionSnapshot, RunSummaryOverview,
    RunStatisticsSnapshot, IssueItem, IssueAggregateSnapshot, DeviceReviewContext, RecheckDiffSnapshot, ExportArtifact
)
from src.crosscutting.config.settings import settings
from src.crosscutting.errors.exceptions import (
    PersistenceCorruptionError, PersistenceRecoveryError, PersistenceError,
    PersistenceSchemaError, ErrorCode
)
from src.crosscutting.logging.logger import get_logger
import datetime

logger = get_logger(__name__)

DATA_DIR = os.path.join(settings.BASE_DIR, "data")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")
MAX_BACKUPS = 5  # Keep last N backup copies per file

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# ==========================================
# P1.1-3: Schema Version & Migration Safety
# ==========================================

# Current schema versions — bump when data structure changes
BASELINES_SCHEMA_VERSION = "1.3"
TASKS_SCHEMA_VERSION = "1.0"

# Supported migration paths: {(from_version, to_version): migration_function}
# Each migration function takes the raw data dict and returns the migrated dict.


def _migrate_baselines_v0_to_v1(data: dict) -> dict:
    """Migrate baselines.json from no-schema (v0 / pre-schema) to v1.0.
    
    v1.0 changes:
    - Adds version_history_meta to each baseline entry (was already done ad-hoc)
    - Normalizes baseline_version_snapshot from dict-of-str to dict-of-dict
    """
    for baseline_id, entry in data.items():
        if baseline_id == "__schema_version__":
            continue
        if not isinstance(entry, dict):
            continue
        # Ensure version_history_meta exists
        if "version_history_meta" not in entry:
            entry["version_history_meta"] = {}
        # Normalize snapshot: if snapshot values are strings instead of dicts, fix them
        snapshots = entry.get("baseline_version_snapshot", {})
        if isinstance(snapshots, dict):
            for ver, snap_data in snapshots.items():
                if isinstance(snap_data, str):
                    # Was stored as just a string — convert to empty dict
                    logger.warning(f"Baseline {baseline_id} snapshot {ver} was string '{snap_data}', normalizing to empty dict")
                    snapshots[ver] = {}
    data["__schema_version__"] = "1.0"
    return data


def _migrate_baselines_v1_to_v1_1(data: dict) -> dict:
    """Migrate baselines.json from v1.0 to v1.1.
    
    v1.1 changes:
    - Ensures all rule entries have rule_type field (default: "template")
    """
    for baseline_id, entry in data.items():
        if baseline_id == "__schema_version__":
            continue
        if not isinstance(entry, dict):
            continue
        rule_set = entry.get("rule_set", {})
        if isinstance(rule_set, dict):
            for rule_id, rule_def in rule_set.items():
                if isinstance(rule_def, dict) and "rule_type" not in rule_def:
                    rule_def["rule_type"] = "template"
                    logger.info(f"Migrated rule {rule_id} in baseline {baseline_id}: added default rule_type=template")
        # Same for snapshots
        snapshots = entry.get("baseline_version_snapshot", {})
        if isinstance(snapshots, dict):
            for ver, snap_data in snapshots.items():
                if isinstance(snap_data, dict):
                    for rule_id, rule_def in snap_data.items():
                        if isinstance(rule_def, dict) and "rule_type" not in rule_def:
                            rule_def["rule_type"] = "template"
    data["__schema_version__"] = "1.1"
    return data


def _migrate_baselines_v1_1_to_v1_2(data: dict) -> dict:
    """Migrate baselines.json from v1.1 to v1.2.
    
    v1.2 changes:
    - Adds working_draft field (null) to each baseline entry for draft persistence.
    - Strict semantics: None = no draft, dict = draft exists. Empty {} is not used.
    """
    for baseline_id, entry in data.items():
        if baseline_id == "__schema_version__":
            continue
        if not isinstance(entry, dict):
            continue
        if "working_draft" not in entry:
            entry["working_draft"] = None
            logger.info(f"Migrated baseline {baseline_id}: added working_draft=null")
    data["__schema_version__"] = "1.2"
    return data


def _migrate_baselines_v1_2_to_v1_3(data: dict) -> dict:
    """Migrate baselines.json from v1.2 to v1.3.
    
    v1.3 changes:
    - Modifies working_draft to be a rule_set-level draft wrapper:
      working_draft = {"rule_set": {...}, "saved_at": "...", "active_rule_id": "..."}
    - Rejects and clears malformed drafts that don't fit old or new structure.
    """
    for baseline_id, entry in data.items():
        if baseline_id == "__schema_version__":
            continue
        if not isinstance(entry, dict):
            continue
        
        draft = entry.get("working_draft")
        if draft is None:
            continue
            
        if not isinstance(draft, dict):
            logger.error(f"Malformed draft in baseline {baseline_id} (not a dict). Clearing.")
            entry["working_draft"] = None
            continue
            
        # If it's already in the new format (has rule_set), leave it alone
        if "rule_set" in draft and isinstance(draft["rule_set"], dict):
            continue
            
        # Try to parse it as an old single-rule draft
        # An old draft has rule_id, rule_type, params, etc. at the top level
        rule_id = draft.get("rule_id")
        rule_type = draft.get("rule_type")
        params = draft.get("params")
        
        # We need at least these fields to do a safe migration
        if rule_id and rule_type and params is not None:
            # We map it to the new wrapper
            new_rule_def = {
                "template": rule_type,  # in old schema, rule_type was actually template
                "rule_type": "template", # new schema default
                "target_type": draft.get("target_type", "devices"),
                "severity": draft.get("severity", "warning"),
                "params": params
            }
            new_draft = {
                "rule_set": {rule_id: new_rule_def},
                "active_rule_id": rule_id,
                "saved_at": draft.get("saved_at", datetime.datetime.now().isoformat())
            }
            entry["working_draft"] = new_draft
            logger.info(f"Migrated baseline {baseline_id} draft from single-rule to rule_set wrapper.")
        else:
            # It's malformed or unrecoverable, clear it to be safe
            logger.error(f"Malformed draft in baseline {baseline_id} missing core fields. Clearing.")
            entry["working_draft"] = None

    data["__schema_version__"] = "1.3"
    return data

# Migration registry
BASELINES_MIGRATIONS = {
    ("0", "1.0"): _migrate_baselines_v0_to_v1,
    ("1.0", "1.1"): _migrate_baselines_v1_to_v1_1,
    ("1.1", "1.2"): _migrate_baselines_v1_1_to_v1_2,
    ("1.2", "1.3"): _migrate_baselines_v1_2_to_v1_3,
}


def _apply_schema_migration(file_name: str, data: dict, current_version: str, 
                             migrations: dict, schema_key: str) -> dict:
    """
    P1.1-3: Apply schema migrations to data read from a JSON file.
    
    Args:
        file_name: Name of the data file (for logging/errors)
        data: Parsed JSON data dict
        current_version: The code's current schema version
        migrations: Dict of {(from, to): migration_fn}
        schema_key: Key in data dict that stores the schema version
    
    Returns:
        Migrated data dict
    
    Raises:
        PersistenceSchemaError: If data version is too new or unsupported
    """
    data_version = data.get(schema_key, None)
    
    if data_version is None:
        # Pre-schema data — treat as version "0"
        logger.info(f"File {file_name} has no {schema_key}, treating as v0 (pre-schema)")
        data_version = "0"
    
    if data_version == current_version:
        # Same version — no migration needed
        return data
    
    # Check if data is newer than code — this is an error
    from packaging.version import Version
    try:
        dv = Version(data_version)
        cv = Version(current_version)
    except Exception:
        # Fallback: simple string comparison
        dv = None
        cv = None
    
    if dv is not None and cv is not None and dv > cv:
        raise PersistenceSchemaError(
            file_name=file_name,
            schema_version=data_version,
            current_version=current_version,
            reason=f"Data schema v{data_version} is newer than code v{current_version}. Please update the application."
        )
    
    # Apply migrations step by step
    current = data_version
    migrated_data = data
    
    while current != current_version:
        # Find a migration from current to some next version
        next_migration = None
        for (from_v, to_v), migration_fn in migrations.items():
            if from_v == current:
                if next_migration is None or Version(to_v) < Version(next_migration[0]):
                    next_migration = (to_v, migration_fn)
        
        if next_migration is None:
            raise PersistenceSchemaError(
                file_name=file_name,
                schema_version=current,
                current_version=current_version,
                reason=f"No migration path from v{current} to v{current_version}. Available migrations: {list(migrations.keys())}"
            )
        
        to_v, migration_fn = next_migration
        logger.info(f"Migrating {file_name} from schema v{current} → v{to_v}")
        try:
            migrated_data = migration_fn(migrated_data)
            current = to_v
        except Exception as e:
            raise PersistenceSchemaError(
                file_name=file_name,
                schema_version=current,
                current_version=current_version,
                reason=f"Migration v{current} → v{to_v} failed: {e}"
            )
    
    # Ensure schema version is stamped
    migrated_data[schema_key] = current_version
    logger.info(f"Successfully migrated {file_name} to schema v{current_version}")
    return migrated_data


def _backup_file(file_name: str) -> Optional[str]:
    """
    Create a rolling backup of the current file before writing.
    Keeps at most MAX_BACKUPS copies, oldest gets deleted.
    Returns the backup file path, or None if no file exists to backup.
    """
    src_path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(src_path):
        return None

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_name = f"{file_name}.bak.{timestamp}"
    backup_path = os.path.join(BACKUP_DIR, backup_name)

    try:
        shutil.copy2(src_path, backup_path)
        logger.info(f"Backup created: {backup_path}")
        _prune_old_backups(file_name)
        return backup_path
    except Exception as e:
        logger.error(f"Failed to create backup for {file_name}: {e}")
        # Non-fatal: we continue even if backup fails, but log it
        return None


def _prune_old_backups(file_name: str):
    """Remove oldest backups beyond MAX_BACKUPS for the given file."""
    prefix = f"{file_name}.bak."
    try:
        backups = sorted([
            f for f in os.listdir(BACKUP_DIR) 
            if f.startswith(prefix)
        ], reverse=True)  # newest first

        for old_backup in backups[MAX_BACKUPS:]:
            old_path = os.path.join(BACKUP_DIR, old_backup)
            os.remove(old_path)
            logger.debug(f"Pruned old backup: {old_path}")
    except Exception as e:
        logger.warning(f"Failed to prune backups for {file_name}: {e}")


def _get_latest_backup(file_name: str) -> Optional[str]:
    """Find the most recent backup file for the given data file."""
    prefix = f"{file_name}.bak."
    try:
        backups = sorted([
            f for f in os.listdir(BACKUP_DIR) 
            if f.startswith(prefix)
        ], reverse=True)  # newest first
        if backups:
            return os.path.join(BACKUP_DIR, backups[0])
    except Exception:
        pass
    return None


def _preserve_corrupted_file(file_name: str) -> Optional[str]:
    """
    Rename a corrupted file to .corrupted.<timestamp>.json for forensic analysis.
    Returns the corrupted file path, or None if file doesn't exist.
    """
    src_path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(src_path):
        return None

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    corrupted_name = f"{file_name}.corrupted.{timestamp}.json"
    corrupted_path = os.path.join(DATA_DIR, corrupted_name)

    try:
        os.rename(src_path, corrupted_path)
        logger.error(f"Corrupted file preserved: {corrupted_path}")
        return corrupted_path
    except Exception as e:
        logger.error(f"Failed to preserve corrupted file {src_path}: {e}")
        return None


def _write_json_debounced(file_name: str, data: Dict):
    """
    PAIN-006: Debounced async-like flush for high-frequency saves.
    Instead of writing immediately, we schedule a write to happen shortly after.
    If another write comes in before the timer fires, the timer is reset.
    For simplicity in this sync environment without a running event loop, 
    we implement a simple time-based batching/throttling in-memory.
    """
    import time
    
    # Global state for debouncing
    if not hasattr(_write_json_debounced, "_pending_writes"):
        _write_json_debounced._pending_writes = {}
        _write_json_debounced._last_write_time = {}
        
    pending = _write_json_debounced._pending_writes
    last_write = _write_json_debounced._last_write_time
    
    now = time.time()
    
    # Always update the pending data
    pending[file_name] = data
    
    # If we haven't written recently (e.g. > 500ms), write immediately
    # Otherwise, we just leave it in pending (it will be flushed on next read or forced flush)
    if file_name not in last_write or (now - last_write[file_name] > 0.5):
        _write_json_direct(file_name, pending[file_name])
        last_write[file_name] = now
        del pending[file_name]

def _flush_pending_writes(file_name: str = None):
    """Force flush any pending writes for a file or all files."""
    if not hasattr(_write_json_debounced, "_pending_writes"):
        return
        
    pending = _write_json_debounced._pending_writes
    last_write = _write_json_debounced._last_write_time
    import time
    
    if file_name:
        if file_name in pending:
            _write_json_direct(file_name, pending[file_name])
            last_write[file_name] = time.time()
            del pending[file_name]
    else:
        for fname, data in list(pending.items()):
            _write_json_direct(fname, data)
            last_write[fname] = time.time()
            del pending[fname]

def _read_json(file_name: str) -> Dict:
    """
    Read and parse a JSON file with fail-fast corruption detection.
    Also flushes any pending writes before reading to ensure consistency.
    """
    # Flush pending writes for this file to ensure we read latest data
    _flush_pending_writes(file_name)
    
    path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(path):
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                logger.warning(f"File {file_name} contains non-dict JSON (type={type(data).__name__}), wrapping")
                data = {}
            return data
    except json.JSONDecodeError as e:
        logger.error(f"JSON corruption detected in {file_name}: {e}")
        # 1. Preserve the corrupted file
        corrupted_path = _preserve_corrupted_file(file_name)
        # 2. Attempt recovery from backup
        backup_path = _get_latest_backup(file_name)
        if backup_path:
            try:
                with open(backup_path, "r", encoding="utf-8") as f:
                    recovered_data = json.load(f)
                # Copy backup to primary location
                shutil.copy2(backup_path, path)
                logger.info(f"Recovered {file_name} from backup: {backup_path}")
                return recovered_data
            except Exception as recovery_err:
                logger.error(f"Backup recovery also failed for {file_name}: {recovery_err}")
                raise PersistenceRecoveryError(
                    file_path=path,
                    backup_path=backup_path,
                    reason=f"Backup at {backup_path} is also invalid: {recovery_err}"
                )
        else:
            # No backup available — this is a data loss situation
            raise PersistenceCorruptionError(
                file_path=path,
                original_error=str(e)
            )
    except Exception as e:
        logger.error(f"Unexpected error reading {file_name}: {e}")
        raise PersistenceError(
            f"Failed to read {file_name}: {e}",
            error_code=ErrorCode.PERSISTENCE_READ_FAILED,
            details={"file_path": path, "original_error": str(e)}
        )


def _write_json_direct(file_name: str, data: Dict):
    """
    Atomic write with pre-write backup.
    
    Steps:
    1. Create rolling backup of current file
    2. Write to temp file
    3. Atomically replace target file
    """
    # 1. Backup before write
    _backup_file(file_name)

    path = os.path.join(DATA_DIR, file_name)
    # 2. Safe atomic write to prevent corruption
    fd, temp_path = tempfile.mkstemp(dir=DATA_DIR)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        os.replace(temp_path, path)
        logger.debug(f"Persisted {file_name} ({len(data)} entries)")
    except Exception as e:
        # Clean up temp file if write failed
        try:
            os.remove(temp_path)
        except OSError:
            pass
        logger.error(f"Failed to write {file_name}: {e}")
        raise PersistenceError(
            f"Failed to write {file_name}: {e}",
            error_code=ErrorCode.PERSISTENCE_WRITE_FAILED,
            details={"file_path": path, "original_error": str(e)}
        )


class BaselineRepository:
    def get_all(self) -> List[BaselineProfile]:
        data = _read_json("baselines.json")
        # P1.1-3: Apply schema migration
        data = _apply_schema_migration(
            "baselines.json", data, BASELINES_SCHEMA_VERSION,
            BASELINES_MIGRATIONS, "__schema_version__"
        )
        # Ensure fallback for newly added extension fields
        profiles = []
        for k, v in data.items():
            if k == "__schema_version__":
                continue
            if not isinstance(v, dict):
                continue
            if "version_history_meta" not in v:
                v["version_history_meta"] = {}
            # A1-1: Ensure working_draft field exists (strict: None means no draft)
            if "working_draft" not in v:
                v["working_draft"] = None
            profiles.append(BaselineProfile(**v))
        return profiles
        
    def get_by_id(self, baseline_id: str) -> BaselineProfile:
        data = _read_json("baselines.json")
        # P1.1-3: Apply schema migration
        data = _apply_schema_migration(
            "baselines.json", data, BASELINES_SCHEMA_VERSION,
            BASELINES_MIGRATIONS, "__schema_version__"
        )
        if baseline_id in data:
            v = data[baseline_id]
            if not isinstance(v, dict):
                return None
            if "version_history_meta" not in v:
                v["version_history_meta"] = {}
            # A1-1: Ensure working_draft field exists (strict: None means no draft)
            if "working_draft" not in v:
                v["working_draft"] = None
            return BaselineProfile(**v)
        return None

    def save(self, profile: BaselineProfile):
        data = _read_json("baselines.json")
        # P1.1-3: Apply schema migration before adding new data
        data = _apply_schema_migration(
            "baselines.json", data, BASELINES_SCHEMA_VERSION,
            BASELINES_MIGRATIONS, "__schema_version__"
        )
        data[profile.baseline_id] = profile.__dict__
        # P1.1-3: Stamp schema version on write
        data["__schema_version__"] = BASELINES_SCHEMA_VERSION
        _write_json_debounced("baselines.json", data)

class TaskRepository:
    def get_by_id(self, task_id: str) -> CheckTask:
        data = _read_json("tasks.json")
        if task_id in data:
            d = data[task_id]
            d["task_status"] = TaskStatus(d["task_status"])
            d["created_at"] = datetime.datetime.fromisoformat(d["created_at"])
            return CheckTask(**d)
        return None

    def save(self, task: CheckTask):
        data = _read_json("tasks.json")
        d = task.__dict__.copy()
        d["task_status"] = d["task_status"].value
        data[task.task_id] = d
        _write_json("tasks.json", data)

class ResultRepository:
    def save_recognition(self, snap: RecognitionResultSnapshot):
        d = _read_json("recognitions.json")
        d[snap.task_id] = snap.__dict__
        _write_json("recognitions.json", d)

    def get_recognition(self, task_id: str) -> RecognitionResultSnapshot:
        d = _read_json("recognitions.json")
        return RecognitionResultSnapshot(**d[task_id]) if task_id in d else None

    def save_run_execution(self, snap: RunExecutionSnapshot):
        d = _read_json("run_executions.json")
        d[snap.run_id] = snap.__dict__
        _write_json("run_executions.json", d)

    def get_run_execution(self, run_id: str) -> RunExecutionSnapshot:
        d = _read_json("run_executions.json")
        if run_id in d:
            snap_data = d[run_id]
            if isinstance(snap_data.get('started_at'), str):
                snap_data['started_at'] = datetime.datetime.fromisoformat(snap_data['started_at'])
            if isinstance(snap_data.get('completed_at'), str):
                snap_data['completed_at'] = datetime.datetime.fromisoformat(snap_data['completed_at'])
            return RunExecutionSnapshot(**snap_data)
        return None

    def save_statistics(self, snap: RunStatisticsSnapshot):
        d = _read_json("run_statistics.json")
        d[snap.run_id] = snap.__dict__
        _write_json("run_statistics.json", d)

    def get_statistics(self, run_id: str) -> RunStatisticsSnapshot:
        d = _read_json("run_statistics.json")
        return RunStatisticsSnapshot(**d[run_id]) if run_id in d else None

    def save_issue_aggregate(self, snap: IssueAggregateSnapshot):
        d = _read_json("issue_aggregates.json")
        dd = snap.__dict__.copy()
        dd["issues"] = [i.__dict__ for i in dd["issues"]]
        d[snap.run_id] = dd
        _write_json("issue_aggregates.json", dd)
        
    def get_issue_aggregate(self, run_id: str) -> IssueAggregateSnapshot:
        d = _read_json("issue_aggregates.json")
        if run_id in d:
            dd = d[run_id]
            dd["issues"] = [IssueItem(**i) for i in dd["issues"]]
            return IssueAggregateSnapshot(**dd)
        return None

    def save_summary(self, summary: RunSummaryOverview):
        d = _read_json("run_summaries.json")
        d[summary.run_id] = summary.__dict__
        _write_json("run_summaries.json", d)
        
    def get_summary(self, run_id: str) -> RunSummaryOverview:
        d = _read_json("run_summaries.json")
        return RunSummaryOverview(**d[run_id]) if run_id in d else None

    def save_diff(self, snap: RecheckDiffSnapshot):
        d = _read_json("run_diffs.json")
        d[f"{snap.prev_run_id}_{snap.curr_run_id}"] = snap.__dict__
        _write_json("run_diffs.json", d)

    def save_review(self, snap: DeviceReviewContext):
        d = _read_json("reviews.json")
        dd = snap.__dict__.copy()
        dd["related_issues"] = [i.__dict__ for i in dd["related_issues"]]
        d[f"{snap.run_id}_{snap.device_name}"] = dd
        _write_json("reviews.json", d)
        
    def get_diff(self, prev_run_id: str, curr_run_id: str) -> RecheckDiffSnapshot:
        d = _read_json("run_diffs.json")
        k = f"{prev_run_id}_{curr_run_id}"
        return RecheckDiffSnapshot(**d[k]) if k in d else None
        
    def get_review(self, run_id: str, device_name: str) -> DeviceReviewContext:
        d = _read_json("reviews.json")
        k = f"{run_id}_{device_name}"
        if k in d:
            dd = d[k]
            dd["related_issues"] = [IssueItem(**i) for i in dd["related_issues"]]
            return DeviceReviewContext(**dd)
        return None

    def save_export(self, snap: ExportArtifact):
        d = _read_json("exports.json")
        dd = snap.__dict__.copy()
        if "data" in dd:
            del dd["data"] # Don't store actual bytes in JSON metadata
        d[f"{snap.run_id}_{snap.format}"] = dd
        _write_json("exports.json", d)

    def get_exports(self, run_id: str) -> List[ExportArtifact]:
        d = _read_json("exports.json")
        exports = []
        for k, v in d.items():
            if k.startswith(f"{run_id}_"):
                v["data"] = b"" # Mock empty data for metadata retrieval
                exports.append(ExportArtifact(**v))
        return exports
