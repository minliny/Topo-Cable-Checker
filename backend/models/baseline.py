# backend/models/baseline.py
# Baseline-related models

from typing import Optional, Union, List
from pydantic import BaseModel


class ParameterProfile(BaseModel):
    profile_id: str
    name: str
    description: Optional[str] = None
    parameters: dict


class ThresholdProfile(BaseModel):
    profile_id: str
    name: str
    description: Optional[str] = None
    thresholds: dict


class ScopeSelector(BaseModel):
    scope_id: str
    name: str
    description: Optional[str] = None
    selector_type: str


class RuleSet(BaseModel):
    ruleset_id: str
    name: str
    description: Optional[str] = None
    rule_ids: List[str] = []


class ParameterDefinition(BaseModel):
    name: str
    type: str
    default: Optional[Union[float, str, bool]] = None
    unit: Optional[str] = None
    description: Optional[str] = None


class ConditionExpression(BaseModel):
    expression: str
    description: Optional[str] = None


class RuleDefinition(BaseModel):
    id: str
    name: str
    enabled: bool = True
    category: str
    severity: str
    condition: ConditionExpression
    parameters: List[ParameterDefinition] = []
    description: Optional[str] = None


class Baseline(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    version: str
    status: str = "draft"
    identification_strategy: dict = {}
    naming_template: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
