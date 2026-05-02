# backend/services/run_service.py
from typing import Optional

from ..repositories.provider import get_repository
from ..engine.provider import get_engine
from ..models.execution import RunHistoryEntry, CheckResultBundle, IssueItem


class RunService:
    def __init__(self):
        self.repo = get_repository()
        self.engine = get_engine()

    def get_all_runs(self) -> list[RunHistoryEntry]:
        return self.repo.get_all_runs()

    def get_run_detail(self, run_id: str) -> Optional[dict]:
        run = self.repo.get_run_by_id(run_id)
        if not run:
            return None
        bundle = self.repo.get_bundle_by_id(run.bundle_id) if run.bundle_id else None
        return {"run": run, "bundle": bundle}

    async def get_bundle(self, bundle_id: str) -> Optional[CheckResultBundle]:
        bundle = await self.engine.get_bundle(bundle_id)
        if bundle:
            return bundle
        return self.repo.get_bundle_by_id(bundle_id)

    async def get_issue(self, issue_id: str) -> Optional[IssueItem]:
        issue = await self.engine.get_issue(issue_id)
        if issue:
            return issue
        return self.repo.get_issue_by_id(issue_id)
