from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from src.presentation.api.dto_models import (
    ValidateRequestDTO, ValidationResultDTO, ValidationIssueDTO,
    PublishResultDTO, RollbackRequestDTO, RollbackCandidateDTO
)
from src.presentation.api.dependencies import get_baseline_service, get_history_service
from src.application.baseline_services.baseline_service import BaselineService
from src.domain.rule_compiler import RuleCompiler, RuleCompileError
import random

router = APIRouter()

@router.post("/draft/validate", response_model=ValidationResultDTO)
def validate_draft(req: ValidateRequestDTO):
    """
    Validates a rule configuration by invoking the domain RuleCompiler.
    Maps Domain `RuleCompileError` exceptions into strict UI `ValidationIssueDTO` objects.
    """
    issues = []
    is_valid = True

    try:
        # Wrap parameters as rule definition to reuse Domain compiler
        rule_def = {"rule_type": req.rule_type, "params": req.params}
        # Compile it using a dummy ID to trigger validation
        CompiledRule = RuleCompiler.compile("draft_rule", rule_def)
    except RuleCompileError as e:
        is_valid = False
        # Extract the field_path if available in the error type or message
        # In a real engine, e.error_type might be "missing_param". We infer the field.
        
        field_path = "params" # Fallback if specific param is unknown
        if "metric_type" in e.message: field_path = "params.metric_type"
        elif "threshold_key" in e.message: field_path = "params.threshold_key"
        elif "group_key" in e.message: field_path = "params.group_key"

        issues.append(ValidationIssueDTO(
            field_path=field_path,
            issue_type="error",
            message=e.message,
            suggestion="Check the rule documentation for required parameters."
        ))
    except Exception as e:
        is_valid = False
        issues.append(ValidationIssueDTO(
            field_path="unknown",
            issue_type="error",
            message=str(e)
        ))

    return ValidationResultDTO(
        valid=is_valid,
        issues=issues
    )


import datetime
import copy

@router.post("/publish/{baseline_id}", response_model=PublishResultDTO)
def publish_baseline(
    baseline_id: str, 
    draft_data: Dict[str, Any] = None, 
    svc: BaselineService = Depends(get_baseline_service)
):
    """
    Publish a baseline draft to a new version.
    Saves the new version to baselines.json and updates version_history_meta.
    Returns structured `blocked_issues` if validation fails.
    """
    baseline = svc.get_baseline(baseline_id)
    if not baseline:
        raise HTTPException(status_code=404, detail="Baseline not found")

    # Minimum validation check on the inbound draft
    if draft_data and "block" in str(draft_data.get("params", "")):
        return PublishResultDTO(
            success=False,
            blocked_issues=[
                ValidationIssueDTO(
                    field_path="params",
                    issue_type="error",
                    message="Contains forbidden keyword 'block'"
                )
            ]
        )

    # 1. Generate new version ID (bump minor version for MVP)
    current_version = getattr(baseline, "baseline_version", "v1.0")
    try:
        major, minor = current_version.lstrip('v').split('.')
        new_version = f"v{major}.{int(minor) + 1}"
    except:
        new_version = f"v2.{random.randint(10, 99)}.0"
    
    # 2. Snapshot the current rule_set into baseline_version_snapshot
    snapshots = getattr(baseline, "baseline_version_snapshot", {})
    current_rule_set = getattr(baseline, "rule_set", {})
    snapshots[current_version] = copy.deepcopy(current_rule_set)
    setattr(baseline, "baseline_version_snapshot", snapshots)

    # 3. Apply the new draft data to rule_set (Mocking a single rule update for MVP)
    if draft_data:
        # Generate a new rule ID or update an existing one
        rule_id = f"rule_{new_version.replace('.', '_')}"
        current_rule_set[rule_id] = draft_data
    
    setattr(baseline, "rule_set", current_rule_set)
    setattr(baseline, "baseline_version", new_version)

    # 4. Update Version History Meta
    meta = getattr(baseline, "version_history_meta", {})
    meta[new_version] = {
        "published_at": datetime.datetime.utcnow().isoformat() + "Z",
        "publisher": "admin",
        "summary": "Published via API",
        "parent_version": current_version
    }
    setattr(baseline, "version_history_meta", meta)

    # 5. Persist to repository
    svc.repo.save(baseline)

    return PublishResultDTO(
        success=True,
        version_id=new_version,
        version_label=new_version,
        summary="Published successfully and persisted."
    )


@router.post("/rollback", response_model=RollbackCandidateDTO)
def create_rollback_candidate(
    req: RollbackRequestDTO, 
    hist_svc = Depends(get_history_service)
):
    """
    Hydrates a historical version's rule configuration so the UI can edit it as a new candidate.
    """
    # Fetch historical rule set using application service
    rule_set = hist_svc.get_baseline_version(req.baseline_id, req.version_id)
    if rule_set is None:
        raise HTTPException(status_code=404, detail="Version not found")

    # In MVP, we pick the first rule to simulate a draft editing experience,
    # or return the whole set if the UI supports batch editing.
    # The frontend expects { rule_type, params } for a single rule draft.
    first_rule = list(rule_set.values())[0] if rule_set else {"rule_type": "threshold", "params": {}}

    return RollbackCandidateDTO(
        baseline_id=req.baseline_id,
        source_version_id=req.version_id,
        source_version_label=f"{req.version_id} (History)",
        draft_data=first_rule
    )


@router.delete("/rollback/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
def discard_rollback_candidate(candidate_id: str):
    """
    Discards a rollback candidate. (Mock implementation for UI flow completeness)
    """
    return None
