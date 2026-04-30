# backend/routers/rules.py
# Rule API endpoints

from fastapi import APIRouter, HTTPException
from ..models.baseline import RuleDefinition, RuleSet
from ..data import MOCK_RULES, MOCK_RULESETS

router = APIRouter(prefix="/api", tags=["rules"])


@router.get("/rules/definitions")
async def get_rule_definitions():
    """Get all rule definitions"""
    return {"rules": MOCK_RULES}


@router.get("/rulesets")
async def get_rulesets():
    """Get all rule sets"""
    return {"rulesets": MOCK_RULESETS}


@router.patch("/rules/{rule_id}/override")
async def update_rule_override(rule_id: str, request: dict):
    """Update rule override"""
    rule = next((r for r in MOCK_RULES if r.id == rule_id), None)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"status": "ok"}