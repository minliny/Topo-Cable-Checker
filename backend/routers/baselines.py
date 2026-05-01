# backend/routers/baselines.py
# Baseline API endpoints

from fastapi import APIRouter, HTTPException, status
from typing import Optional
from ..services.baseline_service import BaselineService

router = APIRouter(prefix="/api/baselines", tags=["baselines"])
service = BaselineService()


@router.get("")
async def get_baselines():
    """Get all baselines"""
    return {"baselines": service.get_all_baselines()}


@router.get("/{baseline_id}")
async def get_baseline(baseline_id: str):
    """Get baseline detail"""
    detail = service.get_baseline_detail(baseline_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Baseline not found")
    return detail


@router.patch("/{baseline_id}")
async def update_baseline(baseline_id: str, request: dict):
    """Update baseline"""
    if not service.update_baseline(baseline_id, request):
        raise HTTPException(status_code=404, detail="Baseline not found")
    return {"status": "ok"}


@router.get("/{baseline_id}/profile-map")
async def get_baseline_profile_map(baseline_id: str):
    """Get baseline profile mapping"""
    profile_map = service.get_baseline_profile_map(baseline_id)
    if not profile_map:
        raise HTTPException(status_code=404, detail="Baseline not found")
    return profile_map


@router.get("/{baseline_id}/version-snapshot")
async def get_baseline_version_snapshot(baseline_id: str):
    """Get baseline version snapshot"""
    snapshot = service.get_baseline_version_snapshot(baseline_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Baseline not found")
    return snapshot
