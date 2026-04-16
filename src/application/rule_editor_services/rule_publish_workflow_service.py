from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import datetime
import copy
from src.application.rule_editor_services.rule_editor_mvp_service import RuleDraftView
from src.application.rule_editor_services.rule_editor_governance_bridge_service import RuleEditorGovernanceBridgeService
from src.domain.interfaces import IBaselineRepository

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
    new_revision: Optional[int] = None

class RulePublishWorkflowService:
    """
    Manages the workflow of taking a draft rule, validating it via the bridge,
    and publishing it into a formal baseline version.
    """
    def __init__(
        self, 
        repo: IBaselineRepository,
        bridge: Optional[RuleEditorGovernanceBridgeService] = None
    ):
        self.repo = repo
        self.bridge = bridge or RuleEditorGovernanceBridgeService()

    def publish_draft(self, baseline_id: str, draft: RuleDraftView, expected_revision: int, change_note: str = "") -> RulePublishResult:
        # 1. Compile & Validate using the bridge
        compile_result = self.bridge.compile_draft_preview(draft)
        
        if not compile_result.compile_success:
            failures = [
                RulePublishFailure(
                    error_type=err.error_type,
                    message=err.message,
                    field_name=err.field_name
                )
                for err in compile_result.validation_errors
            ]
            return RulePublishResult(publish_success=False, errors=failures)

        # 2. Retrieve baseline
        baseline = self.repo.get_by_id(baseline_id)
        if not baseline:
            return RulePublishResult(
                publish_success=False,
                errors=[RulePublishFailure("not_found", f"Baseline {baseline_id} not found")]
            )

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
        rule_def = draft.to_rule_def()
        
        is_new = draft.rule_id not in new_rule_set
        new_rule_set[draft.rule_id] = rule_def

        added = 1 if is_new else 0
        modified = 0 if is_new else 1
        
        # 6. Apply updates and save
        baseline.rule_set = new_rule_set
        baseline.baseline_version = new_version
        baseline.baseline_version_snapshot = snapshots
        # A1-7: Clear working_draft after successful publish
        baseline.working_draft = None

        self.repo.save(baseline, expected_revision=expected_revision)

        updated_baseline = self.repo.get_by_id(baseline_id)
        new_rev = getattr(updated_baseline, "revision", 1)

        # 7. Build summary
        action_verb = "Added" if is_new else "Modified"
        summary_text = f"{action_verb} rule '{draft.rule_id}' ({draft.rule_type}). {change_note}".strip()

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

        return RulePublishResult(publish_success=True, summary=summary, errors=[], new_revision=new_rev)
