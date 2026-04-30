# backend/routers/baselines.py
# Baseline API endpoints

from fastapi import APIRouter, HTTPException, status
from typing import Optional
from ..models.baseline import Baseline, RuleSet, RuleDefinition, ParameterProfile, ThresholdProfile, ScopeSelector
from ..data import (
    MOCK_BASELINES,
    MOCK_RULESETS,
    MOCK_RULES,
    MOCK_PARAMETER_PROFILES,
    MOCK_THRESHOLD_PROFILES,
    MOCK_SCOPE_SELECTORS,
    BASELINE_PROFILE_MAP,
    BASELINE_VERSION_SNAPSHOTS,
)

router = APIRouter(prefix="/api/baselines", tags=["baselines"])


@router.get("")
async def get_baselines():
    """Get all baselines"""
    return {"baselines": MOCK_BASELINES}


@router.get("/{baseline_id}")
async def get_baseline(baseline_id: str):
    """Get baseline detail"""
    baseline = next((b for b in MOCK_BASELINES if b.id == baseline_id), None)
    if not baseline:
        raise HTTPException(status_code=404, detail="Baseline not found")

    profile_map = BASELINE_PROFILE_MAP.get(baseline_id, {})
    rulesets = [rs for rs in MOCK_RULESETS if rs.ruleset_id in profile_map.get("ruleset_ids", [])]

    pp = next((p for p in MOCK_PARAMETER_PROFILES if p.profile_id == profile_map.get("parameter_profile_id")), None)
    tp = next((p for p in MOCK_THRESHOLD_PROFILES if p.profile_id == profile_map.get("threshold_profile_id")), None)
    sc = next((s for s in MOCK_SCOPE_SELECTORS if s.scope_id == profile_map.get("scope_selector_id")), None)

    return {
        "baseline": baseline,
        "rulesets": rulesets,
        "rules": MOCK_RULES,
        "parameter_profile": pp,
        "threshold_profile": tp,
        "scope_selector": sc,
    }


@router.patch("/{baseline_id}")
async def update_baseline(baseline_id: str, request: dict):
    """Update baseline"""
    baseline = next((b for b in MOCK_BASELINES if b.id == baseline_id), None)
    if not baseline:
        raise HTTPException(status_code=404, detail="Baseline not found")
    return {"status": "ok"}


@router.get("/{baseline_id}/profile-map")
async def get_baseline_profile_map(baseline_id: str):
    """Get baseline profile mapping"""
    profile_map = BASELINE_PROFILE_MAP.get(baseline_id, {})
    if not profile_map:
        raise HTTPException(status_code=404, detail="Baseline not found")
    return profile_map


@router.get("/{baseline_id}/version-snapshot")
async def get_baseline_version_snapshot(baseline_id: str):
    """Get baseline version snapshot"""
    snapshot = BASELINE_VERSION_SNAPSHOTS.get(baseline_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Baseline not found")
    return snapshot