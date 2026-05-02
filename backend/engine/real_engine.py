# backend/engine/real_engine.py
# RealEngineAdapter scaffold: implements EngineAdapter interface.
# WARNING: This is a scaffold only. Methods raise NotImplementedError.
# No real check engine integration, no Excel reading, no database, no external AI.

import os
from typing import Optional

from .interface import EngineAdapter
from ..repositories.provider import get_repository
from ..models.execution import (
    CheckResultBundle,
    DataSource,
    ExecutionScope,
    IssueItem,
    RecognitionResult,
    RunHistoryEntry,
)
from ..models.diff import RecheckDiffSnapshot


class RealEngineAdapter(EngineAdapter):
    """Real engine adapter scaffold.

    WARNING: This is a development scaffold only.
    All methods raise NotImplementedError.

    To activate: set TOPOCHECKER_ENGINE=real
    This is NOT for production use.
    """

    def __init__(self):
        self.repo = get_repository()

    # ── Recognition ──────────────────────────────────────────────

    async def get_recognition_status(self) -> str:
        raise NotImplementedError(
            "RealEngineAdapter: get_recognition_status not implemented (scaffold only)"
        )

    async def start_recognition(self, data_source_id: str, scope_id: str) -> str:
        raise NotImplementedError(
            "RealEngineAdapter: start_recognition not implemented (scaffold only)"
        )

    async def get_recognition_result(self, recognition_id: str) -> Optional[RecognitionResult]:
        raise NotImplementedError(
            "RealEngineAdapter: get_recognition_result not implemented (scaffold only)"
        )

    async def confirm_recognition(self, recognition_id: str) -> bool:
        raise NotImplementedError(
            "RealEngineAdapter: confirm_recognition not implemented (scaffold only)"
        )

    # ── Execution ────────────────────────────────────────────────

    async def start_check(
        self,
        baseline_id: str,
        data_source_id: str,
        scope_id: str,
        parameter_profile_id: Optional[str] = None,
        threshold_profile_id: Optional[str] = None,
    ) -> str:
        raise NotImplementedError(
            "RealEngineAdapter: start_check not implemented (scaffold only)"
        )

    async def get_run_status(self, run_id: str) -> str:
        raise NotImplementedError(
            "RealEngineAdapter: get_run_status not implemented (scaffold only)"
        )

    # ── Results ──────────────────────────────────────────────────

    async def get_bundle(self, run_id: str) -> Optional[CheckResultBundle]:
        raise NotImplementedError(
            "RealEngineAdapter: get_bundle not implemented (scaffold only)"
        )

    async def get_issue(self, issue_id: str) -> Optional[IssueItem]:
        raise NotImplementedError(
            "RealEngineAdapter: get_issue not implemented (scaffold only)"
        )

    # ── Diff ─────────────────────────────────────────────────────

    async def get_recheck_diff(
        self, base_run_id: str, target_run_id: str
    ) -> Optional[RecheckDiffSnapshot]:
        raise NotImplementedError(
            "RealEngineAdapter: get_recheck_diff not implemented (scaffold only)"
        )

    # ── Metadata (optional, may delegate to repository) ──────────

    async def list_data_sources(self) -> list[DataSource]:
        raise NotImplementedError(
            "RealEngineAdapter: list_data_sources not implemented (scaffold only)"
        )

    async def list_scopes(self) -> list[ExecutionScope]:
        raise NotImplementedError(
            "RealEngineAdapter: list_scopes not implemented (scaffold only)"
        )
