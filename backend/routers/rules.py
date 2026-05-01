# backend/routers/rules.py
# Rule API endpoints

from fastapi import APIRouter, HTTPException
from ..services.rule_service import RuleService

router = APIRouter(prefix="/api", tags=["rules"])
service = RuleService()


@router.get("/rules/definitions")
async def get_rule_definitions():
    """Get all rule definitions"""
    return {"rules": service.get_all_rules()}


@router.get("/rulesets")
async def get_rulesets():
    """Get all rule sets"""
    return {"rulesets": service.get_all_rulesets()}


@router.patch("/rules/{rule_id}/override")
async def update_rule_override(rule_id: str, request: dict):
    """Update rule override"""
    if not service.update_rule_override(rule_id, request):
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"status": "ok"}
