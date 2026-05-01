# backend/services/run_service.py
from typing import Optional

from ..repositories.mock_repository import MockRepository
from ..engine.mock_engine import MockEngineAdapter
from ..models.execution import RunHistoryEntry, CheckResultBundle, IssueItem


class RunService:
    def __init__(self):
        self.repo = MockRepository()
        self.engine = MockEngineAdapter()

    def get_all_runs(self) -> list[RunHistoryEntry]:
        return self.repo.get_all_runs()

    def get_run_detail(self, run_id: str) -> Optional[dict]:
        run = self.repo.get_run_by_id(run_id)
        if not run:
            return None
        bundle = self.repo.get_bundle_by_id(run.bundle_id) if run.bundle_id else None
        return {"run": run, "bundle": bundle}

    async def get_bundle(self, bundle_id: str) -> Optional[CheckResultBundle]:
        # Prefer engine adapter for bundle retrieval
        bundle = await self.engine.get_bundle(bundle_id)
        if bundle:
            return bundle
        # Fallback to repository
        return self.repo.get_bundle_by_id(bundle_id)

    async def get_issue(self, issue_id: str) -> Optional[IssueItem]:
        # Prefer engine adapter for issue retrieval
        issue = await self.engine.get_issue(issue_id)
        if issue:
            return issue
        # Fallback to repository
        return self.repo.get_issue_by_id(issue_id)
