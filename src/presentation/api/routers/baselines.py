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

    return VersionMetaDTO(
        version_id=version_id,
        baseline_id=baseline_id,
        version_label=f"{version_id} (Archived)",
        summary="Retrieved from history",
        publisher="System",
        published_at="2026-04-10T00:00:00Z" # Mocked metadata since baseline.json doesn't track this currently
    )


@router.get("/{baseline_id}/diff", response_model=DiffSourceTargetDTO)
def get_baseline_diff(
    baseline_id: str, 
    source: str = "draft", 
    target: str = "previous_version"
):
    """
    Mocked Diff response. The backend currently has `RecheckService` diff, 
    but it compares "Runs" not "Baseline Versions".
    To unblock UI integration, we provide a structured mock matching DTO.
    """
    return {
        "source_version_id": source,
        "target_version_id": target,
        "diff_summary": {
            "added": 1,
            "removed": 0,
            "modified": 0
        },
        "rules": [
            {
                "rule_id": "rule-new-1",
                "change_type": "added",
                "changed_fields": [],
                "old_value": None,
                "new_value": { "rule_type": "threshold", "params": {"metric_type": "count"} }
            }
        ]
    }
