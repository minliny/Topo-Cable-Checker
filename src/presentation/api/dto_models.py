from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# ==========================================
# Responses DTOs (Outbound to UI)
# ==========================================

class BaselineNodeDTO(BaseModel):
    id: str
    type: str  # 'baseline_root', 'working_draft', 'published_version', 'rollback_candidate'
    name: str
    baseline_id: str
    parent_id: Optional[str] = None
    version_id: Optional[str] = None
    source_version_id: Optional[str] = None
    source_version_label: Optional[str] = None
    status: Optional[str] = None

class VersionMetaDTO(BaseModel):
    version_id: str
    baseline_id: str
    version_label: str
    summary: str
    publisher: str
    published_at: str
    parent_version_id: Optional[str] = None

class ValidationIssueDTO(BaseModel):
    field_path: str
    issue_type: str  # 'error' or 'warning'
    message: str
    suggestion: Optional[str] = None

class ValidationResultDTO(BaseModel):
    valid: bool
    issues: List[ValidationIssueDTO]

class PublishResultDTO(BaseModel):
    success: bool
    version_id: Optional[str] = None
    version_label: Optional[str] = None
    summary: Optional[str] = None
    blocked_issues: Optional[List[ValidationIssueDTO]] = None

class RollbackCandidateDTO(BaseModel):
    baseline_id: str
    source_version_id: str
    source_version_label: str
    draft_data: Any
    rule_set: Optional[Dict[str, Any]] = None  # B2: Full rule set for complete rollback

class DiffFieldChangeDTO(BaseModel):
    """P1.1-2: Single field-level before/after change for human readability."""
    field_name: str
    old_value: Any = None
    new_value: Any = None

class DiffSummaryDTO(BaseModel):
    added: int
    removed: int
    modified: int

class DiffRuleDTO(BaseModel):
    rule_id: str
    change_type: str  # 'added', 'removed', 'modified'
    changed_fields: Optional[List[str]] = None
    field_changes: Optional[List[DiffFieldChangeDTO]] = None  # P1.1-2: per-field before/after
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    human_summary: Optional[str] = None  # P1.1-2: human-readable one-liner e.g. "severity: warning → error"

class DiffSourceTargetDTO(BaseModel):
    source_version_id: str
    target_version_id: str
    diff_summary: DiffSummaryDTO
    human_readable_summary: Optional[str] = None  # P1.1-2: e.g. "2 rules added, 1 modified (severity changes)"
    rules: List[DiffRuleDTO]

# ==========================================
# Requests DTOs (Inbound from UI)
# ==========================================

class ValidateRequestDTO(BaseModel):
    rule_type: str
    params: Dict[str, Any]

class PublishRequestDTO(BaseModel):
    """P1.0-1: Explicit request body for publish endpoint."""
    rule_set: Optional[Dict[str, Any]] = None
    # For backward compatibility
    rule_id: Optional[str] = None
    rule_type: Optional[str] = None
    target_type: Optional[str] = None
    severity: Optional[str] = None
    params: Optional[Dict[str, Any]] = None

class RollbackRequestDTO(BaseModel):
    baseline_id: str
    version_id: str

# ==========================================
# A1-4: Save Draft / Load Draft DTOs
# ==========================================

class SaveDraftRequestDTO(BaseModel):
    """A1-4: Request body for saving a working draft."""
    baseline_id: str
    rule_set: Dict[str, Any]
    active_rule_id: Optional[str] = None

class SaveDraftResultDTO(BaseModel):
    """A1-4: Response for save draft operation."""
    success: bool
    saved_at: str
    draft_snapshot: Dict[str, Any]

class LoadDraftResultDTO(BaseModel):
    """A1-4: Response for load draft operation."""
    has_draft: bool
    draft_data: Optional[Dict[str, Any]] = None
    saved_at: Optional[str] = None
