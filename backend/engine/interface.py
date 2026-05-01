# backend/engine/interface.py
# Engine Adapter abstract interface
# Defines the contract between backend services and the check engine.
# Future real engine implementations must conform to this interface.

from abc import ABC, abstractmethod
from typing import Optional

from ..models.execution import (
    CheckResultBundle,
    DataSource,
    ExecutionScope,
    IssueItem,
    RecognitionResult,
    RunHistoryEntry,
)
from ..models.diff import RecheckDiffSnapshot


class EngineAdapter(ABC):
    """Abstract adapter for the topology check engine.

    Responsibilities:
    - Recognition: preview device recognition before check
    - Execution: start check runs and track progress
    - Results: retrieve check results (bundles, issues)
    - Diff: compute recheck diffs between runs

    Implementations:
    - MockEngineAdapter: returns mock data, no real computation
    - RealEngineAdapter: (future) connects to actual check engine
    """

    # ── Recognition ──────────────────────────────────────────────

    @abstractmethod
    async def get_recognition_status(self) -> str:
        """Return current recognition status: not_started | ready | confirmed | rejected"""
        ...

    @abstractmethod
    async def start_recognition(self, data_source_id: str, scope_id: str) -> str:
        """Start device recognition for the given data source and scope.
        Returns recognition_id.
        """
        ...

    @abstractmethod
    async def get_recognition_result(self, recognition_id: str) -> Optional[RecognitionResult]:
        """Get recognition result preview."""
        ...

    @abstractmethod
    async def confirm_recognition(self, recognition_id: str) -> bool:
        """Confirm recognition result and allow check to proceed."""
        ...

    # ── Execution ────────────────────────────────────────────────

    @abstractmethod
    async def start_check(
        self,
        baseline_id: str,
        data_source_id: str,
        scope_id: str,
        parameter_profile_id: Optional[str] = None,
        threshold_profile_id: Optional[str] = None,
    ) -> str:
        """Start a check run.
        Returns run_id.
        """
        ...

    @abstractmethod
    async def get_run_status(self, run_id: str) -> str:
        """Return run status: queued | running | completed | failed"""
        ...

    # ── Results ──────────────────────────────────────────────────

    @abstractmethod
    async def get_bundle(self, run_id: str) -> Optional[CheckResultBundle]:
        """Get the full check result bundle for a run."""
        ...

    @abstractmethod
    async def get_issue(self, issue_id: str) -> Optional[IssueItem]:
        """Get detailed information for a single issue."""
        ...

    # ── Diff ─────────────────────────────────────────────────────

    @abstractmethod
    async def get_recheck_diff(
        self, base_run_id: str, target_run_id: str
    ) -> Optional[RecheckDiffSnapshot]:
        """Get pre-computed recheck diff between two runs.
        The engine is responsible for diff computation, not the frontend.
        """
        ...

    # ── Metadata (optional, may delegate to repository) ──────────

    @abstractmethod
    async def list_data_sources(self) -> list[DataSource]:
        """List available data sources."""
        ...

    @abstractmethod
    async def list_scopes(self) -> list[ExecutionScope]:
        """List available execution scopes."""
        ...
