# backend/services/profile_service.py
from ..repositories.mock_repository import MockRepository
from ..models.baseline import ParameterProfile, ThresholdProfile, ScopeSelector


class ProfileService:
    def __init__(self):
        self.repo = MockRepository()

    def get_parameter_profiles(self) -> list[ParameterProfile]:
        return self.repo.get_all_parameter_profiles()

    def get_threshold_profiles(self) -> list[ThresholdProfile]:
        return self.repo.get_all_threshold_profiles()

    def get_scope_selectors(self) -> list[ScopeSelector]:
        return self.repo.get_all_scope_selectors()
