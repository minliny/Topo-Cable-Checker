# backend/routers/execution.py
# Execution config API endpoints

from fastapi import APIRouter, HTTPException
from ..services.execution_service import ExecutionService

router = APIRouter(prefix="/api", tags=["execution"])
service = ExecutionService()


@router.get("/data-sources")
async def get_data_sources():
    """Get all data sources"""
    return {"data_sources": service.get_data_sources()}


@router.get("/scopes")
async def get_scopes():
    """Get all execution scopes"""
    return {"scopes": service.get_scopes()}


@router.get("/recognition/status")
async def get_recognition_status():
    """Get current recognition status"""
    return {"status": await service.get_recognition_status()}


@router.post("/recognition/start")
async def start_recognition(request: dict):
    """Start recognition process"""
    return {"recognition_id": await service.start_recognition(request)}


@router.post("/recognition/confirm")
async def confirm_recognition(request: dict):
    """Confirm recognition result"""
    await service.confirm_recognition(request)
    return {"status": "ok"}


@router.post("/checks/start")
async def start_check(request: dict):
    """Start check execution"""
    return {"run_id": await service.start_check(request)}
