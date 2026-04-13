from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import datetime
import copy
from src.application.rule_editor_services.rule_editor_mvp_service import RuleDraftView, RuleDraftValidationResult
from src.application.rule_editor_services.rule_editor_governance_bridge_service import RuleEditorGovernanceBridgeService
from src.domain.interfaces import IBaselineRepository
from src.infrastructure.repository import BaselineRepository

@dataclass
class RulePublishFailure:
    error_type: str
    message: str
    field_name: Optional[str] = None

@dataclass
class PublishedBaselineSummaryView:
    baseline_id: str
    baseline_version: str
    published_rule_count: int
    changed_rule_count: int
    added_rules: int
    modified_rules: int
    removed_rules: int
    summary_text: str
    published_at: str

@dataclass
class RulePublishResult:
    publish_success: bool
    summary: Optional[PublishedBaselineSummaryView] = None
    errors: List[RulePublishFailure] = None  # None = no errors, [] = empty error list

class RulePublishWorkflowService:
    """
    Manages the workflow of taking a draft rule, validating it via the bridge,
    and publishing it into a formal baseline version.
    """
    def __init__(
        self, 
        repo: Optional[IBaselineRepository] = None,
        bridge: Optional[RuleEditorGovernanceBridgeService] = None
    ):
        self.repo = repo or BaselineRepository()
        self.bridge = bridge or RuleEditorGovernanceBridgeService()

    def publish_draft(self, baseline_id: str, draft: dict, change_note: str = "") -> RulePublishResult:
        # 1. Compile & Validate using the bridge for each rule in the draft
        failures = []
        for rule_id, rule_def in draft.items():
            # Build temporary RuleDraftView for bridge validation
            draft_view = RuleDraftView(
                rule_id=rule_id,
                rule_type=rule_def.get("template", "unknown"),
                target_type=rule_def.get("target_type", "unknown"),
                severity=rule_def.get("severity", "unknown"),
                params=rule_def.get("params", {}),
                validation_result=RuleDraftValidationResult(True, {})
            )
            compile_result = self.bridge.compile_draft_preview(draft_view)
            
            if not compile_result.compile_success:
                for err in compile_result.validation_errors:
                    failures.append(
                        RulePublishFailure(
                            error_type=err.error_type,
                            message=f"[{rule_id}] {err.message}",
                            field_name=err.field_name
                        )
                    )
        
        if failures:
            return RulePublishResult(publish_success=False, errors=failures)

        # 2. Retrieve baseline
        baseline = self.repo.get_by_id(baseline_id)
        if not baseline:
            return RulePublishResult(
                publish_success=False,
                errors=[RulePublishFailure("not_found", f"Baseline {baseline_id} not found")]
            )

        # Handle object or dict access
        if isinstance(baseline, dict):
            current_version = baseline.get("baseline_version", "v1.0")
            old_rule_set = baseline.get("rule_set", {})
            snapshots = baseline.get("baseline_version_snapshot", {})
        else:
            current_version = getattr(baseline, "baseline_version", "v1.0")
            old_rule_set = getattr(baseline, "rule_set", {})
            snapshots = getattr(baseline, "baseline_version_snapshot", {})

        if not snapshots:
            snapshots = {}

        # 3. Create snapshot of old rules
        snapshots[current_version] = copy.deepcopy(old_rule_set)

        # 4. Bump version
        try:
            major, minor = current_version.lstrip("v").split(".")
            new_version = f"v{major}.{int(minor) + 1}"
        except Exception:
            new_version = f"{current_version}_new"

        # 5. Calculate Diff for Summary
        new_rule_set = copy.deepcopy(old_rule_set)
        
        added = 0
        modified = 0
        for rule_id, rule_def in draft.items():
            if rule_id not in new_rule_set:
                added += 1
            else:
                modified += 1
            new_rule_set[rule_id] = rule_def
        
        # 6. Apply updates and save
        if isinstance(baseline, dict):
            baseline["rule_set"] = new_rule_set
            baseline["baseline_version"] = new_version
            baseline["baseline_version_snapshot"] = snapshots
            # A1-7: Clear working_draft after successful publish
            baseline["working_draft"] = None
        else:
            baseline.rule_set = new_rule_set
            baseline.baseline_version = new_version
            baseline.baseline_version_snapshot = snapshots
            # A1-7: Clear working_draft after successful publish
            baseline.working_draft = None

        self.repo.save(baseline)

        # 7. Build summary
        action_verb = "Modified" if modified > 0 else "Added"
        rule_ids = ", ".join(draft.keys())
        summary_text = f"{action_verb} rules '{rule_ids}'. {change_note}".strip()

        summary = PublishedBaselineSummaryView(
            baseline_id=baseline_id,
            baseline_version=new_version,
            published_rule_count=len(new_rule_set),
            changed_rule_count=1,
            added_rules=added,
            modified_rules=modified,
            removed_rules=0,
            summary_text=summary_text,
            published_at=datetime.datetime.now().isoformat()
        )

        return RulePublishResult(publish_success=True, summary=summary, errors=[])
