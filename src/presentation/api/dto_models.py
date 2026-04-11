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

class DiffSummaryDTO(BaseModel):
    added: int
    removed: int
    modified: int

class DiffRuleDTO(BaseModel):
    rule_id: str
    change_type: str  # 'added', 'removed', 'modified'
    changed_fields: Optional[List[str]] = None
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None

class DiffSourceTargetDTO(BaseModel):
    source_version_id: str
    target_version_id: str
    diff_summary: DiffSummaryDTO
    rules: List[DiffRuleDTO]

# ==========================================
# Requests DTOs (Inbound from UI)
# ==========================================

class ValidateRequestDTO(BaseModel):
    rule_type: str
    params: Dict[str, Any]

class RollbackRequestDTO(BaseModel):
    baseline_id: str
    version_id: str
