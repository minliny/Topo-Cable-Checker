# backend/routers/execution.py
# Execution config API endpoints

from fastapi import APIRouter, HTTPException
from ..models.execution import DataSource, ExecutionScope, RecognitionResult
from ..data import MOCK_DATA_SOURCES, MOCK_EXECUTION_SCOPES

router = APIRouter(prefix="/api", tags=["execution"])


@router.get("/data-sources")
async def get_data_sources():
    """Get all data sources"""
    return {"data_sources": MOCK_DATA_SOURCES}


@router.get("/scopes")
async def get_scopes():
    """Get all execution scopes"""
    return {"scopes": MOCK_EXECUTION_SCOPES}


@router.get("/recognition/status")
async def get_recognition_status():
    """Get current recognition status"""
    return {"status": "not_started"}


@router.post("/recognition/start")
async def start_recognition(request: dict):
    """Start recognition process"""
    return {"recognition_id": "rec-001"}


@router.post("/recognition/confirm")
async def confirm_recognition(request: dict):
    """Confirm recognition result"""
    return {"status": "ok"}


@router.post("/checks/start")
async def start_check(request: dict):
    """Start check execution"""
    return {"run_id": "run-new-001"}