"""
P1.0-1/P1.0-2: Rules API Router — Publish with real validation gate.

Key fixes:
1. PublishRequestDTO: explicit body binding (draft_data is no longer silently None)
2. Publish connects to RulePublishWorkflowService which compile+validates before persisting
3. Invalid drafts are BLOCKED from publishing — no bypass path
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, Any
from src.presentation.api.dto_models import (
    ValidateRequestDTO, ValidationResultDTO, ValidationIssueDTO,
    PublishRequestDTO, PublishResultDTO, RestoreDraftRequestDTO, RestoreDraftResultDTO,
    SaveDraftRequestDTO, SaveDraftResultDTO, LoadDraftResultDTO
)
from src.presentation.api.dependencies import get_baseline_service, get_history_service, get_draft_save_service
from src.application.baseline_services.baseline_service import BaselineService
from src.application.rule_editor_services.rule_baseline_history_service import RuleBaselineHistoryService
from src.application.rule_editor_services.rule_draft_save_service import RuleDraftSaveService
from src.application.rule_editor_services.rule_publish_workflow_service import RulePublishWorkflowService
from src.application.rule_editor_services.rule_editor_mvp_service import (
    RuleDraftView, RuleDraftValidationResult
)
from src.domain.rule_compiler import RuleCompiler, RuleCompileError
from src.crosscutting.logging.logger import get_logger
from src.crosscutting.errors.exceptions import DomainError, ErrorCode
from src.crosscutting.observation.recorder import record_event

logger = get_logger(__name__)

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
        # UI uses 'rule_type' to mean 'template'
        rule_def = {"rule_type": "template", "template": req.rule_type, "params": req.params}
        # Compile it using a dummy ID to trigger validation
        compiled_rule = RuleCompiler.compile("draft_rule", rule_def)
    except RuleCompileError as e:
        is_valid = False
        # Extract the field_path if available in the error type or message
        field_path = "params"  # Fallback if specific param is unknown
        if "metric_type" in e.message:
            field_path = "params.metric_type"
        elif "threshold_key" in e.message:
            field_path = "params.threshold_key"
        elif "group_key" in e.message:
            field_path = "params.group_key"

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


@router.post("/publish/{baseline_id}", response_model=PublishResultDTO)
def publish_baseline(
    baseline_id: str,
    req: PublishRequestDTO,
    request: Request,
    svc: BaselineService = Depends(get_baseline_service),
    hist_svc: RuleBaselineHistoryService = Depends(get_history_service)
):
    """
    P1.0-1/P1.0-2: Publish a baseline draft with real compile+validate gate.

    Flow:
    1. Convert PublishRequestDTO → RuleDraftView (application layer model)
    2. RulePublishWorkflowService.publish_draft() compiles and validates the draft
    3. If validation fails → return blocked_issues (no publish)
    4. If validation passes → persist version bump + rule data → return success
    """
    # Build the application-layer draft from the explicit request body
    rule_id = req.rule_id or f"rule_{req.rule_type}"
    draft = RuleDraftView(
        rule_id=rule_id,
        rule_type=req.rule_type,
        target_type=req.target_type,
        severity=req.severity,
        params=req.params,
        # We do NOT carry prior UI validation_result here —
        # the publish workflow will re-compile via RuleCompiler independently
    )

    # Delegate to the application service which compiles+validates before persisting
    publish_svc = RulePublishWorkflowService(
        repo=svc.repo,
    )
    result = publish_svc.publish_draft(baseline_id, draft, expected_revision=req.expected_revision)

    if not result.publish_success:
        # P1.0-2: Validation genuinely blocked the publish
        blocked_issues = [
            ValidationIssueDTO(
                field_path=err.field_name or "unknown",
                issue_type="error",
                message=err.message,
            )
            for err in (result.errors or [])
        ]
        logger.warning(
            f"Publish BLOCKED for baseline={baseline_id} rule={rule_id} "
            f"issues={len(blocked_issues)}"
        )
        return PublishResultDTO(
            success=False,
            blocked_issues=blocked_issues,
        )

    # Publish succeeded — result.summary has the version info
    summary = result.summary
    logger.info(
        f"Publish SUCCESS for baseline={baseline_id} version={summary.baseline_version} "
        f"rules={summary.published_rule_count}"
    )
    record_event(
        event_type="publish_executed",
        baseline_id=baseline_id,
        request_id=getattr(request.state, "request_id", None),
        actor=request.headers.get("X-Actor"),
        context={"version_id": summary.baseline_version, "rule_id": draft.rule_id},
    )

    return PublishResultDTO(
        success=True,
        version_id=summary.baseline_version,
        version_label=summary.baseline_version,
        summary=summary.summary_text,
        new_revision=result.new_revision,
    )


@router.post("/restore-draft", response_model=RestoreDraftResultDTO)
def restore_historical_version_to_draft(
    req: RestoreDraftRequestDTO,
    hist_svc: RuleBaselineHistoryService = Depends(get_history_service)
):
    """
    Load a historical version's rules into an editable draft payload.

    This endpoint does not perform a persistent rollback and does not create a
    server-side candidate entity. It only hydrates historical rules so the UI
    can review, edit, save, and later publish them as a new version.
    """
    rule_set = hist_svc.get_baseline_version(req.baseline_id, req.version_id)
    if rule_set is None:
        raise HTTPException(status_code=404, detail="Version not found")

    first_rule = list(rule_set.values())[0] if rule_set else {"rule_type": "threshold", "params": {}}

    return RestoreDraftResultDTO(
        baseline_id=req.baseline_id,
        restored_from_version_id=req.version_id,
        restored_from_version_label=f"{req.version_id} (History)",
        draft_data=first_rule,
        rule_set=rule_set
    )


# ==========================================
# A1-4: Draft Save / Load / Clear API
# ==========================================

@router.post("/draft/save", response_model=SaveDraftResultDTO)
def save_draft(
    req: SaveDraftRequestDTO,
    request: Request,
    svc: RuleDraftSaveService = Depends(get_draft_save_service)
):
    """
    A1-4/A1-8: Save a working draft to the baseline.
    
    Important: Invalid drafts CAN be saved (no compile gate).
    This allows users to save work-in-progress.
    Invalid drafts are still blocked from publishing by the Publish Validation Gate.
    """
    prev = svc.load_draft(req.baseline_id)
    prev_rule_id = None
    if prev.has_draft and prev.draft_data:
        prev_rule_id = prev.draft_data.get("rule_id")

    result = svc.save_draft(
        baseline_id=req.baseline_id,
        rule_id=req.rule_id,
        rule_type=req.rule_type,
        target_type=req.target_type,
        severity=req.severity,
        params=req.params,
        expected_revision=req.expected_revision,
    )
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.message or "Baseline not found"
        )

    record_event(
        event_type="draft_saved",
        baseline_id=req.baseline_id,
        request_id=getattr(request.state, "request_id", None),
        actor=request.headers.get("X-Actor"),
        context={"rule_id": req.rule_id, "rule_type": req.rule_type},
    )
    if prev_rule_id and prev_rule_id != req.rule_id:
        record_event(
            event_type="draft_overwritten",
            baseline_id=req.baseline_id,
            request_id=getattr(request.state, "request_id", None),
            actor=request.headers.get("X-Actor"),
            context={"prev_rule_id": prev_rule_id, "rule_id": req.rule_id},
        )
    
    return SaveDraftResultDTO(
        success=result.success,
        saved_at=result.saved_at,
        message=result.message,
        new_revision=result.new_revision,
    )


@router.get("/draft/{baseline_id}", response_model=LoadDraftResultDTO)
def load_draft(
    baseline_id: str,
    svc: RuleDraftSaveService = Depends(get_draft_save_service)
):
    """
    A1-4/A1-6: Load a working draft from the baseline.
    
    Used for draft auto-recovery: when entering a baseline editing context,
    the UI first loads any existing working draft.
    """
    result = svc.load_draft(baseline_id)
    
    return LoadDraftResultDTO(
        has_draft=result.has_draft,
        draft_data=result.draft_data,
        saved_at=result.saved_at,
        base_revision=result.base_revision,
    )


@router.delete("/draft/{baseline_id}", status_code=status.HTTP_200_OK)
def clear_draft(
    baseline_id: str,
    expected_revision: int,
    request: Request,
    svc: RuleDraftSaveService = Depends(get_draft_save_service)
):
    new_rev = svc.clear_draft(baseline_id, expected_revision=expected_revision)
    if new_rev is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Baseline {baseline_id} not found"
        )
    record_event(
        event_type="clear_draft",
        baseline_id=baseline_id,
        request_id=getattr(request.state, "request_id", None),
        actor=request.headers.get("X-Actor"),
        context={"new_revision": new_rev},
    )
    return {"success": True, "message": "Draft cleared", "new_revision": new_rev}
