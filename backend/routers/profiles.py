# backend/routers/profiles.py
# Profile and selector API endpoints

from fastapi import APIRouter
from ..data import MOCK_PARAMETER_PROFILES, MOCK_THRESHOLD_PROFILES, MOCK_SCOPE_SELECTORS

router = APIRouter(prefix="/api", tags=["profiles"])


@router.get("/profiles/parameters")
async def get_parameter_profiles():
    """Get all parameter profiles"""
    return {"profiles": MOCK_PARAMETER_PROFILES}


@router.get("/profiles/thresholds")
async def get_threshold_profiles():
    """Get all threshold profiles"""
    return {"profiles": MOCK_THRESHOLD_PROFILES}


@router.get("/scopes/selectors")
async def get_scope_selectors():
    """Get all scope selectors"""
    return {"selectors": MOCK_SCOPE_SELECTORS}