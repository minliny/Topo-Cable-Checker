# backend/models/execution.py
# Execution-related models

from typing import Optional
from pydantic import BaseModel


class SeveritySummary(BaseModel):
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0


class IssueItem(BaseModel):
    issue_id: str
    run_id: str
    rule_id: str
    rule_name: str
    severity: str
    entity_type: str
    entity_id: str
    entity_name: str
    message: str
    parameters: dict = {}
    detected_at: Optional[str] = None


class IssueDiffItem(BaseModel):
    diff_type: str
    issue: IssueItem


class CheckResultBundle(BaseModel):
    bundle_id: str
    run_id: str
    baseline_id: str
    from_run_id: Optional[str] = None
    to_run_id: Optional[str] = None
    severity_summary: SeveritySummary
    issue_count: int
    issues: list[IssueItem] = []
    created_at: Optional[str] = None


class DataSource(BaseModel):
    dataset_id: str
    name: str
    device_count: int
    description: Optional[str] = None


class ExecutionScope(BaseModel):
    scope_id: str
    method: str
    description: Optional[str] = None


class RecognitionResult(BaseModel):
    recognized_device_count: int
    unmatched_device_count: int
    out_of_scope_device_count: int
    warnings: list[str] = []


class RecognitionStatus(str):
    NOT_STARTED = "not_started"
    READY = "ready"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class RunHistoryEntry(BaseModel):
    run_id: str
    baseline_id: str
    baseline_name: str
    scenario_id: str
    status: str
    severity_summary: SeveritySummary
    device_count: int
    issue_count: int
    data_source_id: str
    scope_id: str
    bundle_id: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None