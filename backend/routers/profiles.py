# backend/routers/profiles.py
# Profile and selector API endpoints

from fastapi import APIRouter
from ..services.profile_service import ProfileService

router = APIRouter(prefix="/api", tags=["profiles"])
service = ProfileService()


@router.get("/profiles/parameters")
async def get_parameter_profiles():
    """Get all parameter profiles"""
    return {"profiles": service.get_parameter_profiles()}


@router.get("/profiles/thresholds")
async def get_threshold_profiles():
    """Get all threshold profiles"""
    return {"profiles": service.get_threshold_profiles()}


@router.get("/scopes/selectors")
async def get_scope_selectors():
    """Get all scope selectors"""
    return {"selectors": service.get_scope_selectors()}
