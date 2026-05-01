# backend/routers/versions.py
# Version management API endpoints

from fastapi import APIRouter, HTTPException, Query
from ..services.version_service import VersionService

router = APIRouter(prefix="/api", tags=["versions"])
service = VersionService()


@router.get("/baselines/{baseline_id}/versions")
async def get_versions(baseline_id: str):
    """Get all versions for a baseline"""
    return {"versions": service.get_versions_by_baseline(baseline_id)}


@router.get("/versions/diff")
async def get_version_diff(
    from_version: str = Query(...),
    to_version: str = Query(...),
):
    """Get version diff snapshot"""
    diff = service.get_version_diff(from_version, to_version)
    if not diff:
        raise HTTPException(status_code=404, detail="Version diff not found")
    return {"diff": diff}


@router.get("/versions/{version_id}")
async def get_version_snapshot(version_id: str):
    """Get version snapshot"""
    snapshot = service.get_version_snapshot(version_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Version not found")
    return {"snapshot": snapshot}


@router.post("/baselines/{baseline_id}/versions")
async def create_version(baseline_id: str, request: dict):
    """Create a new version"""
    return {"version_id": service.create_version(baseline_id, request)}


@router.post("/versions/{version_id}/publish")
async def publish_version(version_id: str, request: dict):
    """Publish a version"""
    service.publish_version(version_id, request)
    return {"status": "ok"}
