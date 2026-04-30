# backend/routers/runs.py
# Run history API endpoints

from fastapi import APIRouter, HTTPException
from ..models.execution import RunHistoryEntry, CheckResultBundle
from ..data import MOCK_RUNS, MOCK_BUNDLES

router = APIRouter(prefix="/api", tags=["runs"])


@router.get("/runs")
async def get_run_history():
    """Get all run history"""
    return {"runs": MOCK_RUNS}


@router.get("/runs/{run_id}")
async def get_run_detail(run_id: str):
    """Get run detail with optional bundle"""
    run = next((r for r in MOCK_RUNS if r.run_id == run_id), None)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    bundle = MOCK_BUNDLES.get(run.bundle_id) if run.bundle_id else None
    return {"run": run, "bundle": bundle}


@router.get("/bundles/{bundle_id}")
async def get_bundle(bundle_id: str):
    """Get check result bundle"""
    bundle = MOCK_BUNDLES.get(bundle_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Bundle not found")
    return {"bundle": bundle}


@router.get("/issues/{issue_id}")
async def get_issue_detail(issue_id: str):
    """Get issue detail"""
    for bundle in MOCK_BUNDLES.values():
        for issue in bundle.issues:
            if issue.issue_id == issue_id:
                return {"issue": issue}
    raise HTTPException(status_code=404, detail="Issue not found")