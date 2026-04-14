from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# ==========================================
# Responses DTOs (Outbound to UI)
# ==========================================

class BaselineNodeDTO(BaseModel):
    id: str
    type: str  # 'baseline_root', 'working_draft', 'published_version', 'restored_draft'
    name: str
    baseline_id: str
    parent_id: Optional[str] = None
    version_id: Optional[str] = None
    restored_from_version_id: Optional[str] = None
    restored_from_version_label: Optional[str] = None
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

class RestoreDraftResultDTO(BaseModel):
    baseline_id: str
    restored_from_version_id: str
    restored_from_version_label: str
    draft_data: Any
    rule_set: Optional[Dict[str, Any]] = None

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

class RollbackEffectDiffDTO(BaseModel):
    baseline_id: str
    current_version_id: str
    target_version_id: str
    rollback_effect_diff: DiffSourceTargetDTO

class BaselineVersionRuleSetDTO(BaseModel):
    baseline_id: str
    version_id: str
    rule_set: Dict[str, Any]

# ==========================================
# Requests DTOs (Inbound from UI)
# ==========================================

class ValidateRequestDTO(BaseModel):
    rule_type: str
    params: Dict[str, Any]

class PublishRequestDTO(BaseModel):
    """P1.0-1: Explicit request body for publish endpoint."""
    rule_id: str = ""
    rule_type: str
    target_type: str = "devices"
    severity: str = "warning"
    params: Dict[str, Any]

class RestoreDraftRequestDTO(BaseModel):
    baseline_id: str
    version_id: str

# ==========================================
# A1-4: Save Draft / Load Draft DTOs
# ==========================================

class SaveDraftRequestDTO(BaseModel):
    """A1-4: Request body for saving a working draft."""
    baseline_id: str
    rule_id: str = ""
    rule_type: str
    target_type: str = "devices"
    severity: str = "warning"
    params: Dict[str, Any]

class SaveDraftResultDTO(BaseModel):
    """A1-4: Response for save draft operation."""
    success: bool
    saved_at: Optional[str] = None
    message: Optional[str] = None

class LoadDraftResultDTO(BaseModel):
    """A1-4: Response for load draft operation."""
    has_draft: bool
    draft_data: Optional[Any] = None
    saved_at: Optional[str] = None
