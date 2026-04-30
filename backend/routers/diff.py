# backend/routers/diff.py
# Diff compare API endpoints

from fastapi import APIRouter, HTTPException, Query
from ..models.diff import RecheckDiffSnapshot
from ..data import MOCK_RECHECK_DIFF_SNAPSHOTS

router = APIRouter(prefix="/api", tags=["diff"])


@router.get("/diff/recheck")
async def get_recheck_diff(
    base_run_id: str = Query(...),
    target_run_id: str = Query(...)
):
    """Get recheck diff between two runs"""
    diff_id = f"{base_run_id}->{target_run_id}"
    diff = MOCK_RECHECK_DIFF_SNAPSHOTS.get(diff_id)
    if not diff:
        raise HTTPException(status_code=404, detail="Diff not found")
    return {"diff": diff}