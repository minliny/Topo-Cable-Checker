# backend/services/execution_service.py
from typing import Optional

from ..repositories.provider import get_repository
from ..engine.mock_engine import MockEngineAdapter
from ..models.execution import DataSource, ExecutionScope


class ExecutionService:
    def __init__(self):
        self.repo = get_repository()
        self.engine = MockEngineAdapter()

    def get_data_sources(self) -> list[DataSource]:
        return self.repo.get_all_data_sources()

    def get_scopes(self) -> list[ExecutionScope]:
        return self.repo.get_all_execution_scopes()

    async def get_recognition_status(self) -> str:
        return await self.engine.get_recognition_status()

    async def start_recognition(self, request: dict) -> str:
        data_source_id = request.get("data_source_id", "ds-001")
        scope_id = request.get("scope_id", "scope-full")
        return await self.engine.start_recognition(data_source_id, scope_id)

    async def confirm_recognition(self, request: dict) -> bool:
        recognition_id = request.get("recognition_id", "rec-001")
        return await self.engine.confirm_recognition(recognition_id)

    async def start_check(self, request: dict) -> str:
        baseline_id = request.get("baseline_id", "baseline-001")
        data_source_id = request.get("data_source_id", "ds-001")
        scope_id = request.get("scope_id", "scope-full")
        parameter_profile_id = request.get("parameter_profile_id")
        threshold_profile_id = request.get("threshold_profile_id")
        return await self.engine.start_check(
            baseline_id=baseline_id,
            data_source_id=data_source_id,
            scope_id=scope_id,
            parameter_profile_id=parameter_profile_id,
            threshold_profile_id=threshold_profile_id,
        )
