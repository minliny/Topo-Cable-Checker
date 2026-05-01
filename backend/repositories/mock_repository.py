# backend/repositories/mock_repository.py
# Unified repository layer wrapping mock_data
# NOT connected to real database or external services

from typing import Optional

from ..data import (
    MOCK_BASELINES,
    MOCK_RULESETS,
    MOCK_RULES,
    MOCK_PARAMETER_PROFILES,
    MOCK_THRESHOLD_PROFILES,
    MOCK_SCOPE_SELECTORS,
    MOCK_DATA_SOURCES,
    MOCK_EXECUTION_SCOPES,
    MOCK_VERSION_SNAPSHOTS,
    MOCK_VERSION_DIFF_SNAPSHOTS,
    MOCK_RUNS,
    MOCK_BUNDLES,
    MOCK_RECHECK_DIFF_SNAPSHOTS,
    BASELINE_PROFILE_MAP,
    BASELINE_VERSION_SNAPSHOTS,
)

from ..models.baseline import (
    Baseline,
    RuleSet,
    RuleDefinition,
    ParameterProfile,
    ThresholdProfile,
    ScopeSelector,
)
from ..models.execution import (
    DataSource,
    ExecutionScope,
    RunHistoryEntry,
    CheckResultBundle,
    IssueItem,
)
from ..models.version import VersionSnapshot, VersionDiffSnapshot
from ..models.diff import RecheckDiffSnapshot


class MockRepository:
    """Repository layer that wraps mock_data.
    All data access goes through this class.
    Future database migration only needs to replace this class.
    """

    # Baselines
    def get_all_baselines(self) -> list[Baseline]:
        return list(MOCK_BASELINES)

    def get_baseline_by_id(self, baseline_id: str) -> Optional[Baseline]:
        return next((b for b in MOCK_BASELINES if b.id == baseline_id), None)

    def get_baseline_profile_map(self, baseline_id: str) -> Optional[dict]:
        return BASELINE_PROFILE_MAP.get(baseline_id)

    def get_baseline_version_snapshot(self, baseline_id: str) -> Optional[dict]:
        return BASELINE_VERSION_SNAPSHOTS.get(baseline_id)

    # Rulesets
    def get_all_rulesets(self) -> list[RuleSet]:
        return list(MOCK_RULESETS)

    def get_rulesets_by_ids(self, ruleset_ids: list[str]) -> list[RuleSet]:
        return [rs for rs in MOCK_RULESETS if rs.ruleset_id in ruleset_ids]

    # Rules
    def get_all_rules(self) -> list[RuleDefinition]:
        return list(MOCK_RULES)

    def get_rule_by_id(self, rule_id: str) -> Optional[RuleDefinition]:
        return next((r for r in MOCK_RULES if r.id == rule_id), None)

    # Profiles
    def get_all_parameter_profiles(self) -> list[ParameterProfile]:
        return list(MOCK_PARAMETER_PROFILES)

    def get_parameter_profile_by_id(self, profile_id: str) -> Optional[ParameterProfile]:
        return next((p for p in MOCK_PARAMETER_PROFILES if p.profile_id == profile_id), None)

    def get_all_threshold_profiles(self) -> list[ThresholdProfile]:
        return list(MOCK_THRESHOLD_PROFILES)

    def get_threshold_profile_by_id(self, profile_id: str) -> Optional[ThresholdProfile]:
        return next((p for p in MOCK_THRESHOLD_PROFILES if p.profile_id == profile_id), None)

    # Scope Selectors
    def get_all_scope_selectors(self) -> list[ScopeSelector]:
        return list(MOCK_SCOPE_SELECTORS)

    def get_scope_selector_by_id(self, scope_id: str) -> Optional[ScopeSelector]:
        return next((s for s in MOCK_SCOPE_SELECTORS if s.scope_id == scope_id), None)

    # Data Sources
    def get_all_data_sources(self) -> list[DataSource]:
        return list(MOCK_DATA_SOURCES)

    # Execution Scopes
    def get_all_execution_scopes(self) -> list[ExecutionScope]:
        return list(MOCK_EXECUTION_SCOPES)

    # Versions
    def get_all_versions(self) -> list[VersionSnapshot]:
        return list(MOCK_VERSION_SNAPSHOTS.values())

    def get_versions_by_baseline_id(self, baseline_id: str) -> list[VersionSnapshot]:
        return [v for v in MOCK_VERSION_SNAPSHOTS.values() if v.baseline_id == baseline_id]

    def get_version_by_id(self, version_id: str) -> Optional[VersionSnapshot]:
        return MOCK_VERSION_SNAPSHOTS.get(version_id)

    def get_version_diff(self, diff_id: str) -> Optional[VersionDiffSnapshot]:
        return MOCK_VERSION_DIFF_SNAPSHOTS.get(diff_id)

    def get_version_count(self) -> int:
        return len(MOCK_VERSION_SNAPSHOTS)

    # Runs
    def get_all_runs(self) -> list[RunHistoryEntry]:
        return list(MOCK_RUNS)

    def get_run_by_id(self, run_id: str) -> Optional[RunHistoryEntry]:
        return next((r for r in MOCK_RUNS if r.run_id == run_id), None)

    # Bundles
    def get_bundle_by_id(self, bundle_id: str) -> Optional[CheckResultBundle]:
        return MOCK_BUNDLES.get(bundle_id)

    # Issues
    def get_issue_by_id(self, issue_id: str) -> Optional[IssueItem]:
        for bundle in MOCK_BUNDLES.values():
            for issue in bundle.issues:
                if issue.issue_id == issue_id:
                    return issue
        return None

    # Recheck Diff
    def get_recheck_diff(self, diff_id: str) -> Optional[RecheckDiffSnapshot]:
        return MOCK_RECHECK_DIFF_SNAPSHOTS.get(diff_id)
