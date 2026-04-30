# backend/models/schemas.py
# Pydantic models matching frontend/src/api/contracts.ts
# These models define the API DTOs for the backend

from .baseline import (
    Baseline,
    RuleSet,
    RuleDefinition,
    ParameterProfile,
    ThresholdProfile,
    ScopeSelector,
)
from .execution import (
    DataSource,
    ExecutionScope,
    RecognitionResult,
    RunHistoryEntry,
    CheckResultBundle,
    IssueItem,
    SeveritySummary,
)
from .version import VersionSnapshot, VersionDiffSnapshot, VersionChangeSummary
from .diff import RecheckDiffSnapshot

__all__ = [
    # Baseline
    "Baseline",
    "RuleSet",
    "RuleDefinition",
    "ParameterProfile",
    "ThresholdProfile",
    "ScopeSelector",
    # Execution
    "DataSource",
    "ExecutionScope",
    "RecognitionResult",
    "RunHistoryEntry",
    "CheckResultBundle",
    "IssueItem",
    "SeveritySummary",
    # Version
    "VersionSnapshot",
    "VersionDiffSnapshot",
    "VersionChangeSummary",
    # Diff
    "RecheckDiffSnapshot",
]
