# backend/services/version_service.py
from typing import Optional

from ..repositories.mock_repository import MockRepository
from ..models.version import VersionSnapshot, VersionDiffSnapshot


class VersionService:
    def __init__(self):
        self.repo = MockRepository()

    def get_versions_by_baseline(self, baseline_id: str) -> list[VersionSnapshot]:
        return self.repo.get_versions_by_baseline_id(baseline_id)

    def get_version_diff(self, from_version: str, to_version: str) -> Optional[VersionDiffSnapshot]:
        diff_id = f"{from_version}->{to_version}"
        return self.repo.get_version_diff(diff_id)

    def get_version_snapshot(self, version_id: str) -> Optional[VersionSnapshot]:
        return self.repo.get_version_by_id(version_id)

    def create_version(self, baseline_id: str, request: dict) -> str:
        return f"{baseline_id}::v{self.repo.get_version_count()}"

    def publish_version(self, version_id: str, request: dict) -> bool:
        return True
