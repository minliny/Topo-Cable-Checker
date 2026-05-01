# backend/services/diff_service.py
from typing import Optional

from ..repositories.mock_repository import MockRepository
from ..engine.mock_engine import MockEngineAdapter
from ..models.diff import RecheckDiffSnapshot


class DiffService:
    def __init__(self):
        self.repo = MockRepository()
        self.engine = MockEngineAdapter()

    async def get_recheck_diff(self, base_run_id: str, target_run_id: str) -> Optional[RecheckDiffSnapshot]:
        # Prefer engine adapter for diff computation
        diff = await self.engine.get_recheck_diff(base_run_id, target_run_id)
        if diff:
            return diff
        # Fallback to repository
        diff_id = f"{base_run_id}->{target_run_id}"
        return self.repo.get_recheck_diff(diff_id)
