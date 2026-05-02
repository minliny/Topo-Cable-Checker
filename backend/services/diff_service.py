# backend/services/diff_service.py
from typing import Optional

from ..repositories.provider import get_repository
from ..engine.provider import get_engine
from ..models.diff import RecheckDiffSnapshot


class DiffService:
    def __init__(self):
        self.repo = get_repository()
        self.engine = get_engine()

    async def get_recheck_diff(self, base_run_id: str, target_run_id: str) -> Optional[RecheckDiffSnapshot]:
        diff = await self.engine.get_recheck_diff(base_run_id, target_run_id)
        if diff:
            return diff
        diff_id = f"{base_run_id}->{target_run_id}"
        return self.repo.get_recheck_diff(diff_id)
