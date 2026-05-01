# backend/workspace/schema.py
"""JSON schema definitions for workspace files."""

from typing import Any, Dict, Optional


# Task definition schema (saved in workspace/tasks/)
TASK_SCHEMA: Dict[str, Any] = {
    "task_id": str,
    "baseline_id": str,
    "data_source_id": str,
    "scope_id": str,
    "parameter_profile_id": Optional[str],
    "threshold_profile_id": Optional[str],
    "created_at": str,
    "updated_at": str,
}

# Run result schema (saved in workspace/runs/)
RUN_SCHEMA: Dict[str, Any] = {
    "run_id": str,
    "task_id": str,
    "baseline_id": str,
    "status": str,  # queued | running | completed | failed
    "started_at": str,
    "completed_at": Optional[str],
    "bundle_id": Optional[str],
    "severity_summary": Dict[str, int],
}

# Version snapshot schema (saved in workspace/snapshots/)
VERSION_SNAPSHOT_SCHEMA: Dict[str, Any] = {
    "version_id": str,
    "baseline_id": str,
    "snapshot": dict,
    "created_at": str,
}

# Report metadata schema (saved in workspace/reports/)
REPORT_SCHEMA: Dict[str, Any] = {
    "report_id": str,
    "run_id": str,
    "format": str,  # html | csv | excel
    "file_path": str,
    "generated_at": str,
}
