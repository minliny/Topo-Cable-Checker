# backend/models/version.py
# Version-related models

from typing import Optional
from pydantic import BaseModel


class VersionChangeItem(BaseModel):
    rule_id: str
    rule_name: str
    change_type: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None


class VersionDiffFieldChange(BaseModel):
    field_name: str
    change_type: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None


class VersionDiffSnapshot(BaseModel):
    diff_id: str
    from_version: str
    to_version: str
    summary: dict
    rule_changes: list[VersionChangeItem] = []
    field_changes: list[VersionDiffFieldChange] = []
    created_at: Optional[str] = None


class VersionSnapshot(BaseModel):
    version_id: str
    baseline_id: str
    version: str
    description: str
    status: str
    rule_count: int
    change_summary: dict = {}
    created_at: Optional[str] = None
    published_at: Optional[str] = None


class VersionChangeSummary(BaseModel):
    baseline_id: str
    rule_added_count: int
    rule_removed_count: int
    rule_modified_count: int
    parameter_changed_count: int
    threshold_changed_count: int