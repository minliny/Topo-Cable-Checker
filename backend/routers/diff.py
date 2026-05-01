# backend/routers/diff.py
# Diff compare API endpoints

from fastapi import APIRouter, HTTPException, Query
from ..services.diff_service import DiffService

router = APIRouter(prefix="/api", tags=["diff"])
service = DiffService()


@router.get("/diff/recheck")
async def get_recheck_diff(
    base_run_id: str = Query(...),
    target_run_id: str = Query(...)
):
    """Get recheck diff between two runs"""
    diff = await service.get_recheck_diff(base_run_id, target_run_id)
    if not diff:
        raise HTTPException(status_code=404, detail="Diff not found")
    return {"diff": diff}
