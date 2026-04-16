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
    RuleDefinitionDTO,
    ValidateRequestDTO, ValidationResultDTO, ValidationIssueDTO,
    PublishRequestDTO, PublishResultDTO, RestoreDraftRequestDTO, RestoreDraftResultDTO,
    SaveDraftRequestDTO, SaveDraftResultDTO, LoadDraftResultDTO
)
from src.presentation.api.dependencies import get_baseline_service, get_baseline_repository, get_history_service, get_draft_save_service
from src.application.baseline_services.baseline_service import BaselineService
from src.application.rule_editor_services.rule_baseline_history_service import RuleBaselineHistoryService
from src.application.rule_editor_services.rule_draft_save_service import RuleDraftSaveService
from src.application.rule_editor_services.rule_publish_workflow_service import RulePublishWorkflowService
from src.application.rule_editor_services.rule_editor_mvp_service import (
    RuleDraftView, RuleDraftValidationResult
)
from src.application.rule_editor_services.rule_editor_governance_bridge_service import RuleEditorGovernanceBridgeService
from src.application.rule_editor_services.rule_editor_mvp_service import RuleDraftView
from src.crosscutting.logging.logger import get_logger
from src.crosscutting.errors.exceptions import DomainError, ErrorCode
from src.crosscutting.observation.recorder import record_event

logger = get_logger(__name__)

router = APIRouter()


@router.post("/draft/validate", response_model=ValidationResultDTO)
def validate_draft(req: ValidateRequestDTO):
    """
    Validates a rule configuration by invoking the domain RuleCompiler via BridgeService.
    Maps application errors into strict UI `ValidationIssueDTO` objects.
    """
    bridge = RuleEditorGovernanceBridgeService()
    
    # Wrap request as DraftView
    draft_view = RuleDraftView(
        rule_id="draft_rule",
        rule_type=req.rule_type,
        target_type="devices", # Dummy for validation
        severity="warning",
        params=req.params
    )
    
    result = bridge.compile_draft_preview(draft_view)
    
    issues = []
    if not result.compile_success:
        for error in result.validation_errors:
            # Fallback path if field_name is not extracted by bridge
            field_path = error.field_name
            if not field_path:
                field_path = "params"
                if "metric_type" in error.message:
                    field_path = "params.metric_type"
                elif "threshold_key" in error.message:
                    field_path = "params.threshold_key"
                elif "group_key" in error.message:
                    field_path = "params.group_key"
            else:
                field_path = f"params.{field_path}"
                
            issues.append(ValidationIssueDTO(
                field_path=field_path,
                issue_type="error",
                message=error.message,
                suggestion="Check the rule documentation for required parameters."
            ))
            
    return ValidationResultDTO(
        valid=result.compile_success,
        issues=issues
    )


@router.post("/publish/{baseline_id}", response_model=PublishResultDTO)
def publish_baseline(
    baseline_id: str,
    req: PublishRequestDTO,
    request: Request,
    baseline_repo=Depends(get_baseline_repository),
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
    publish_svc = RulePublishWorkflowService(repo=svc.repo)
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

    draft_dto = RuleDefinitionDTO(
        rule_id=first_rule.get("rule_id", "unknown"),
        rule_type=first_rule.get("rule_type", "template"),
        target_type=first_rule.get("target_type", "devices"),
        severity=first_rule.get("severity", "warning"),
        params=first_rule.get("params", {})
    )
    
    rule_set_dto = {}
    if rule_set:
        for k, v in rule_set.items():
            rule_set_dto[k] = RuleDefinitionDTO(
                rule_id=v.get("rule_id", k),
                rule_type=v.get("rule_type", "template"),
                target_type=v.get("target_type", "devices"),
                severity=v.get("severity", "warning"),
                params=v.get("params", {})
            )

    return RestoreDraftResultDTO(
        baseline_id=req.baseline_id,
        restored_from_version_id=req.version_id,
        restored_from_version_label=f"{req.version_id} (History)",
        draft_data=draft_dto,
        rule_set=rule_set_dto
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
    
    # Map the internal working draft to the typed DTO
    draft_dto = None
    if result.draft_data:
        draft_dto = RuleDefinitionDTO(
            rule_id=result.draft_data.get("rule_id", "unknown"),
            rule_type=result.draft_data.get("rule_type", "template"),
            target_type=result.draft_data.get("target_type", "devices"),
            severity=result.draft_data.get("severity", "warning"),
            params=result.draft_data.get("params", {})
        )


    return LoadDraftResultDTO(
        has_draft=result.has_draft,
        draft_data=draft_dto,
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
