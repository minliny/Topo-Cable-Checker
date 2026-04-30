# backend/routers/versions.py
# Version management API endpoints

from fastapi import APIRouter, HTTPException, Query
from ..models.version import VersionSnapshot, VersionDiffSnapshot
from ..data import MOCK_VERSION_SNAPSHOTS, MOCK_VERSION_DIFF_SNAPSHOTS

router = APIRouter(prefix="/api", tags=["versions"])


@router.get("/baselines/{baseline_id}/versions")
async def get_versions(baseline_id: str):
    """Get all versions for a baseline"""
    versions = [v for v in MOCK_VERSION_SNAPSHOTS.values() if v.baseline_id == baseline_id]
    return {"versions": versions}


@router.get("/versions/diff")
async def get_version_diff(
    from_version: str = Query(...),
    to_version: str = Query(...),
):
    """Get version diff snapshot"""
    diff_id = f"{from_version}->{to_version}"
    diff = MOCK_VERSION_DIFF_SNAPSHOTS.get(diff_id)
    if not diff:
        raise HTTPException(status_code=404, detail="Version diff not found")
    return {"diff": diff}


@router.get("/versions/{version_id}")
async def get_version_snapshot(version_id: str):
    """Get version snapshot"""
    snapshot = MOCK_VERSION_SNAPSHOTS.get(version_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Version not found")
    return {"snapshot": snapshot}


@router.post("/baselines/{baseline_id}/versions")
async def create_version(baseline_id: str, request: dict):
    """Create a new version"""
    return {"version_id": f"{baseline_id}::v{len(MOCK_VERSION_SNAPSHOTS)}"}


@router.post("/versions/{version_id}/publish")
async def publish_version(version_id: str, request: dict):
    """Publish a version"""
    return {"status": "ok"}
