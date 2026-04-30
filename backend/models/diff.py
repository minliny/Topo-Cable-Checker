# backend/models/diff.py
# Diff-related models

from typing import Optional
from pydantic import BaseModel
from .execution import IssueItem, SeveritySummary


class IssueCountChange(BaseModel):
    added: int = 0
    removed: int = 0
    unchanged: int = 0
    severity_changed: int = 0


class RecheckDiffSnapshot(BaseModel):
    diff_id: str
    base_run_id: str
    target_run_id: str
    summary: dict
    issue_count_change: IssueCountChange
    severity_change: dict
    added_issues: list[IssueItem] = []
    removed_issues: list[IssueItem] = []
    changed_issues: list[IssueItem] = []
    unchanged_issues: list[IssueItem] = []
    created_at: Optional[str] = None