# backend/engine/mock_engine.py
# Mock implementation of EngineAdapter.
# Returns mock-compatible data. No real computation, no external services.

from typing import Optional

from .interface import EngineAdapter
from ..repositories.mock_repository import MockRepository
from ..models.execution import (
    CheckResultBundle,
    DataSource,
    ExecutionScope,
    IssueItem,
    RecognitionResult,
    RunHistoryEntry,
)
from ..models.diff import RecheckDiffSnapshot


class MockEngineAdapter(EngineAdapter):
    """Mock engine adapter that delegates to MockRepository.
    All responses are pre-computed mock data.
    """

    def __init__(self):
        self.repo = MockRepository()

    # ── Recognition ──────────────────────────────────────────────

    async def get_recognition_status(self) -> str:
        return "not_started"

    async def start_recognition(self, data_source_id: str, scope_id: str) -> str:
        return "rec-001"

    async def get_recognition_result(self, recognition_id: str) -> Optional[RecognitionResult]:
        return RecognitionResult(
            recognized_device_count=150,
            unmatched_device_count=0,
            out_of_scope_device_count=0,
            warnings=[],
        )

    async def confirm_recognition(self, recognition_id: str) -> bool:
        return True

    # ── Execution ────────────────────────────────────────────────

    async def start_check(
        self,
        baseline_id: str,
        data_source_id: str,
        scope_id: str,
        parameter_profile_id: Optional[str] = None,
        threshold_profile_id: Optional[str] = None,
    ) -> str:
        return "run-new-001"

    async def get_run_status(self, run_id: str) -> str:
        return "completed"

    # ── Results ──────────────────────────────────────────────────

    async def get_bundle(self, run_id: str) -> Optional[CheckResultBundle]:
        # Find the run and return its bundle
        run = self.repo.get_run_by_id(run_id)
        if run and run.bundle_id:
            return self.repo.get_bundle_by_id(run.bundle_id)
        # Fallback: try direct bundle lookup
        return self.repo.get_bundle_by_id(run_id)

    async def get_issue(self, issue_id: str) -> Optional[IssueItem]:
        return self.repo.get_issue_by_id(issue_id)

    # ── Diff ─────────────────────────────────────────────────────

    async def get_recheck_diff(
        self, base_run_id: str, target_run_id: str
    ) -> Optional[RecheckDiffSnapshot]:
        diff_id = f"{base_run_id}->{target_run_id}"
        return self.repo.get_recheck_diff(diff_id)

    # ── Metadata ─────────────────────────────────────────────────

    async def list_data_sources(self) -> list[DataSource]:
        return self.repo.get_all_data_sources()

    async def list_scopes(self) -> list[ExecutionScope]:
        return self.repo.get_all_execution_scopes()
