# backend/services/baseline_service.py
from typing import Optional

from ..repositories.provider import get_repository
from ..models.baseline import Baseline


class BaselineService:
    def __init__(self):
        self.repo = get_repository()

    def get_all_baselines(self) -> list[Baseline]:
        return self.repo.get_all_baselines()

    def get_baseline_detail(self, baseline_id: str) -> Optional[dict]:
        baseline = self.repo.get_baseline_by_id(baseline_id)
        if not baseline:
            return None

        profile_map = self.repo.get_baseline_profile_map(baseline_id) or {}
        rulesets = self.repo.get_rulesets_by_ids(profile_map.get("ruleset_ids", []))
        pp = self.repo.get_parameter_profile_by_id(profile_map.get("parameter_profile_id"))
        tp = self.repo.get_threshold_profile_by_id(profile_map.get("threshold_profile_id"))
        sc = self.repo.get_scope_selector_by_id(profile_map.get("scope_selector_id"))

        return {
            "baseline": baseline,
            "rulesets": rulesets,
            "rules": self.repo.get_all_rules(),
            "parameter_profile": pp,
            "threshold_profile": tp,
            "scope_selector": sc,
        }

    def update_baseline(self, baseline_id: str, request: dict) -> bool:
        baseline = self.repo.get_baseline_by_id(baseline_id)
        return baseline is not None

    def get_baseline_profile_map(self, baseline_id: str) -> Optional[dict]:
        return self.repo.get_baseline_profile_map(baseline_id)

    def get_baseline_version_snapshot(self, baseline_id: str) -> Optional[dict]:
        return self.repo.get_baseline_version_snapshot(baseline_id)
