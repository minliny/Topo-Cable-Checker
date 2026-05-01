# backend/routers/runs.py
# Run history API endpoints

from fastapi import APIRouter, HTTPException
from ..services.run_service import RunService

router = APIRouter(prefix="/api", tags=["runs"])
service = RunService()


@router.get("/runs")
async def get_run_history():
    """Get all run history"""
    return {"runs": service.get_all_runs()}


@router.get("/runs/{run_id}")
async def get_run_detail(run_id: str):
    """Get run detail with optional bundle"""
    detail = service.get_run_detail(run_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Run not found")
    return detail


@router.get("/bundles/{bundle_id}")
async def get_bundle(bundle_id: str):
    """Get check result bundle"""
    bundle = await service.get_bundle(bundle_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Bundle not found")
    return {"bundle": bundle}


@router.get("/issues/{issue_id}")
async def get_issue_detail(issue_id: str):
    """Get issue detail"""
    issue = await service.get_issue(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return {"issue": issue}
