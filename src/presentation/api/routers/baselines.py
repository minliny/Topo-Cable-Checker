from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.presentation.api.dto_models import BaselineNodeDTO, VersionMetaDTO, DiffSourceTargetDTO
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
        rules.append({
            "rule_id": r.rule_id, "change_type": "added", "changed_fields": [], "old_value": None, "new_value": r.after
        })
    for r in diff_view.removed_rules:
        rules.append({
            "rule_id": r.rule_id, "change_type": "removed", "changed_fields": [], "old_value": r.before, "new_value": None
        })
    for r in diff_view.modified_rules:
        rules.append({
            "rule_id": r.rule_id, "change_type": "modified", "changed_fields": r.changed_fields, "old_value": r.before, "new_value": r.after
        })

    return {
        "source_version_id": source,
        "target_version_id": actual_target,
        "diff_summary": {
            "added": len(diff_view.added_rules),
            "removed": len(diff_view.removed_rules),
            "modified": len(diff_view.modified_rules)
        },
        "rules": rules
    }
