from fastapi import APIRouter, Depends, HTTPException
from typing import List
import json
from src.presentation.api.dto_models import BaselineNodeDTO, VersionMetaDTO, DiffSourceTargetDTO, RollbackEffectDiffDTO, BaselineVersionRuleSetDTO
from src.presentation.api.dependencies import get_baseline_service, get_history_service
from src.application.baseline_services.baseline_service import BaselineService
from src.application.rule_editor_services.rule_baseline_history_service import RuleBaselineHistoryService

router = APIRouter()

@router.get("", response_model=List[BaselineNodeDTO])
def get_baselines(
    svc: BaselineService = Depends(get_baseline_service),
    hist_svc: RuleBaselineHistoryService = Depends(get_history_service)
):
    """
    Retrieve all baselines and aggregate them into a UI-friendly tree structure.
    (Root -> Draft / Versions)
    """
    profiles = svc.list_baselines()
    nodes = []

    for p in profiles:
        # 1. Root Node
        root_id = p.baseline_id
        nodes.append(BaselineNodeDTO(
            id=root_id,
            type="baseline_root",
            name=f"Baseline {p.baseline_id}",
            baseline_id=root_id,
            version_id="root"
        ))

        # 2. Draft Node
        nodes.append(BaselineNodeDTO(
            id=f"{root_id}-draft",
            type="working_draft",
            name="Draft",
            baseline_id=root_id,
            parent_id=root_id,
            version_id="draft",
            status="draft"
        ))

        # 3. History Version Nodes
        # Use existing RuleBaselineHistoryService to fetch versions
        try:
            versions = hist_svc.list_baseline_versions(root_id)
            for v in versions:
                nodes.append(BaselineNodeDTO(
                    id=f"{root_id}-{v.version}",
                    type="published_version",
                    name=f"{v.version} ({'Prod' if v.is_current else 'Archived'})",
                    baseline_id=root_id,
                    parent_id=root_id,
                    version_id=v.version,
                    status="published" if v.is_current else "archived"
                ))
        except Exception as e:
            # Fallback if history service fails
            print(f"Warning: Failed to fetch history for {root_id}: {e}")

    return nodes


@router.get("/{baseline_id}/versions/{version_id}", response_model=VersionMetaDTO)
def get_version_meta(baseline_id: str, version_id: str, svc: BaselineService = Depends(get_baseline_service)):
    """
    Retrieve metadata for a specific version.
    """
    baseline = svc.get_baseline(baseline_id)
    if not baseline:
        raise HTTPException(status_code=404, detail="Baseline not found")

    meta = getattr(baseline, "version_history_meta", {}).get(version_id, {})

    return VersionMetaDTO(
        version_id=version_id,
        baseline_id=baseline_id,
        version_label=f"{version_id} ({'Prod' if baseline.baseline_version == version_id else 'Archived'})",
        summary=meta.get("summary", "Retrieved from history"),
        publisher=meta.get("publisher", "System"),
        published_at=meta.get("published_at", "2026-04-10T00:00:00Z"),
        parent_version_id=meta.get("parent_version", None)
    )


@router.get("/{baseline_id}/versions/{version_id}/rule-set", response_model=BaselineVersionRuleSetDTO)
def get_version_rule_set(
    baseline_id: str,
    version_id: str,
    hist_svc: RuleBaselineHistoryService = Depends(get_history_service),
    svc: BaselineService = Depends(get_baseline_service),
):
    baseline = svc.get_baseline(baseline_id)
    if not baseline:
        raise HTTPException(status_code=404, detail="Baseline not found")

    rule_set = hist_svc.get_baseline_version(baseline_id, version_id)
    if rule_set is None:
        raise HTTPException(status_code=404, detail="Version not found")

    return {
        "baseline_id": baseline_id,
        "version_id": version_id,
        "rule_set": rule_set
    }


@router.get("/{baseline_id}/diff", response_model=DiffSourceTargetDTO)
def get_baseline_diff(
    baseline_id: str, 
    source: str = "draft", 
    target: str = "previous_version",
    hist_svc: RuleBaselineHistoryService = Depends(get_history_service),
    svc: BaselineService = Depends(get_baseline_service)
):
    """
    Real Diff response using Domain RuleBaselineHistoryService.
    It compares two snapshots (or the current draft vs snapshot) 
    and outputs the unified DiffSourceTargetDTO.
    """
    # If target is abstract "previous_version", find the latest one from metadata
    baseline = svc.get_baseline(baseline_id)
    if not baseline:
        raise HTTPException(status_code=404, detail="Baseline not found")
        
    actual_target = target
    if target == "previous_version":
        # Usually the previous is the baseline_version unless we are comparing against it
        actual_target = getattr(baseline, "baseline_version", "v1.0")

    # Use the domain service to perform actual JSON diffing
    diff_view = hist_svc.diff_versions(baseline_id, source, actual_target)
    
    if not diff_view:
        raise HTTPException(status_code=404, detail="Could not compute diff for versions")

    # Map the Domain DiffView to our API DTO
    rules = []
    
    for r in diff_view.added_rules:
        rule_type = r.after.get("rule_type", r.after.get("template", "rule")) if r.after else "rule"
        rules.append({
            "rule_id": r.rule_id, "change_type": "added",
            "changed_fields": [], "field_changes": [],
            "old_value": None, "new_value": r.after,
            "human_summary": f"New {rule_type} rule added"
        })
    for r in diff_view.removed_rules:
        rule_type = r.before.get("rule_type", r.before.get("template", "rule")) if r.before else "rule"
        rules.append({
            "rule_id": r.rule_id, "change_type": "removed",
            "changed_fields": [], "field_changes": [],
            "old_value": r.before, "new_value": None,
            "human_summary": f"{rule_type} rule removed"
        })
    for r in diff_view.modified_rules:
        # B1: Build per-field before/after using deep_changes (recursive) when available
        field_changes = []
        human_parts = []
        if r.before and r.after:
            if r.deep_changes:
                # B1: Use deep_diff results with full nested paths
                for dc in r.deep_changes:
                    field_changes.append({
                        "field_name": dc.field_path,
                        "old_value": dc.old_value,
                        "new_value": dc.new_value
                    })
                    human_parts.append(f"{dc.field_path}: {json.dumps(dc.old_value, default=str)} → {json.dumps(dc.new_value, default=str)}")
            else:
                # Fallback to shallow field-level comparison
                for f in r.changed_fields:
                    old_v = r.before.get(f)
                    new_v = r.after.get(f)
                    field_changes.append({
                        "field_name": f,
                        "old_value": old_v,
                        "new_value": new_v
                    })
                    human_parts.append(f"{f}: {json.dumps(old_v, default=str)} → {json.dumps(new_v, default=str)}")
        
        human_summary = "; ".join(human_parts) if human_parts else f"{len(r.changed_fields)} field(s) changed"
        rules.append({
            "rule_id": r.rule_id, "change_type": "modified",
            "changed_fields": r.changed_fields,
            "field_changes": field_changes,
            "old_value": r.before, "new_value": r.after,
            "human_summary": human_summary
        })

    # Build global human-readable summary
    parts = []
    n_added = len(diff_view.added_rules)
    n_removed = len(diff_view.removed_rules)
    n_modified = len(diff_view.modified_rules)
    if n_added:
        parts.append(f"{n_added} rule(s) added")
    if n_removed:
        parts.append(f"{n_removed} rule(s) removed")
    if n_modified:
        # Extract common modification themes
        all_changed = set()
        for r in diff_view.modified_rules:
            all_changed.update(r.changed_fields)
        detail = f" ({', '.join(sorted(all_changed))})" if all_changed else ""
        parts.append(f"{n_modified} rule(s) modified{detail}")
    human_readable_summary = "; ".join(parts) if parts else "No changes detected"

    return {
        "source_version_id": source,
        "target_version_id": actual_target,
        "diff_summary": {
            "added": n_added,
            "removed": n_removed,
            "modified": n_modified
        },
        "human_readable_summary": human_readable_summary,
        "rules": rules
    }


@router.get("/{baseline_id}/restore-draft-effect-diff", response_model=RollbackEffectDiffDTO)
def get_restore_draft_effect_diff(
    baseline_id: str,
    target: str,
    hist_svc: RuleBaselineHistoryService = Depends(get_history_service),
    svc: BaselineService = Depends(get_baseline_service),
):
    """
    Preview how restoring a historical version into the draft would differ from
    the current published baseline. This endpoint does not mutate server state.
    """
    baseline = svc.get_baseline(baseline_id)
    if not baseline:
        raise HTTPException(status_code=404, detail="Baseline not found")

    current_version_id = getattr(baseline, "baseline_version", None)
    if not current_version_id:
        raise HTTPException(status_code=404, detail="Baseline current version not found")

    diff_view = hist_svc.diff_versions(baseline_id, current_version_id, target)
    if not diff_view:
        raise HTTPException(status_code=404, detail="Could not compute diff for versions")

    rules = []
    for r in diff_view.added_rules:
        rule_type = r.after.get("rule_type", r.after.get("template", "rule")) if r.after else "rule"
        rules.append({
            "rule_id": r.rule_id, "change_type": "added",
            "changed_fields": [], "field_changes": [],
            "old_value": None, "new_value": r.after,
            "human_summary": f"New {rule_type} rule added"
        })
    for r in diff_view.removed_rules:
        rule_type = r.before.get("rule_type", r.before.get("template", "rule")) if r.before else "rule"
        rules.append({
            "rule_id": r.rule_id, "change_type": "removed",
            "changed_fields": [], "field_changes": [],
            "old_value": r.before, "new_value": None,
            "human_summary": f"{rule_type} rule removed"
        })
    for r in diff_view.modified_rules:
        field_changes = []
        human_parts = []
        if r.before and r.after:
            if r.deep_changes:
                for dc in r.deep_changes:
                    field_changes.append({
                        "field_name": dc.field_path,
                        "old_value": dc.old_value,
                        "new_value": dc.new_value
                    })
                    human_parts.append(f"{dc.field_path}: {json.dumps(dc.old_value, default=str)} → {json.dumps(dc.new_value, default=str)}")
            else:
                for f in r.changed_fields:
                    old_v = r.before.get(f)
                    new_v = r.after.get(f)
                    field_changes.append({
                        "field_name": f,
                        "old_value": old_v,
                        "new_value": new_v
                    })
                    human_parts.append(f"{f}: {json.dumps(old_v, default=str)} → {json.dumps(new_v, default=str)}")

        human_summary = "; ".join(human_parts) if human_parts else f"{len(r.changed_fields)} field(s) changed"
        rules.append({
            "rule_id": r.rule_id, "change_type": "modified",
            "changed_fields": r.changed_fields,
            "field_changes": field_changes,
            "old_value": r.before, "new_value": r.after,
            "human_summary": human_summary
        })

    parts = []
    n_added = len(diff_view.added_rules)
    n_removed = len(diff_view.removed_rules)
    n_modified = len(diff_view.modified_rules)
    if n_added:
        parts.append(f"{n_added} rule(s) added")
    if n_removed:
        parts.append(f"{n_removed} rule(s) removed")
    if n_modified:
        all_changed = set()
        for r in diff_view.modified_rules:
            all_changed.update(r.changed_fields)
        detail = f" ({', '.join(sorted(all_changed))})" if all_changed else ""
        parts.append(f"{n_modified} rule(s) modified{detail}")
    human_readable_summary = "; ".join(parts) if parts else "No changes detected"

    return {
        "baseline_id": baseline_id,
        "current_version_id": current_version_id,
        "target_version_id": target,
        "rollback_effect_diff": {
            "source_version_id": current_version_id,
            "target_version_id": target,
            "diff_summary": {
                "added": n_added,
                "removed": n_removed,
                "modified": n_modified
            },
            "human_readable_summary": human_readable_summary,
            "rules": rules
        }
    }
