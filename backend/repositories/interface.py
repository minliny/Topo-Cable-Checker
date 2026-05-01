# backend/repositories/interface.py
# Repository abstract interface
# Defines the contract for all data access layers.
# Future database implementations must conform to this interface.

from abc import ABC, abstractmethod
from typing import Optional

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


class Repository(ABC):
    """Abstract repository for all data access.

    Implementations:
    - MockRepository: in-memory mock data
    - SQLiteRepository: (future) SQLite-backed persistence
    """

    # ── Baselines ────────────────────────────────────────────────

    @abstractmethod
    def get_all_baselines(self) -> list[Baseline]: ...

    @abstractmethod
    def get_baseline_by_id(self, baseline_id: str) -> Optional[Baseline]: ...

    @abstractmethod
    def get_baseline_profile_map(self, baseline_id: str) -> Optional[dict]: ...

    @abstractmethod
    def get_baseline_version_snapshot(self, baseline_id: str) -> Optional[dict]: ...

    # ── Rulesets ─────────────────────────────────────────────────

    @abstractmethod
    def get_all_rulesets(self) -> list[RuleSet]: ...

    @abstractmethod
    def get_rulesets_by_ids(self, ruleset_ids: list[str]) -> list[RuleSet]: ...

    # ── Rules ────────────────────────────────────────────────────

    @abstractmethod
    def get_all_rules(self) -> list[RuleDefinition]: ...

    @abstractmethod
    def get_rule_by_id(self, rule_id: str) -> Optional[RuleDefinition]: ...

    # ── Profiles ─────────────────────────────────────────────────

    @abstractmethod
    def get_all_parameter_profiles(self) -> list[ParameterProfile]: ...

    @abstractmethod
    def get_parameter_profile_by_id(self, profile_id: str) -> Optional[ParameterProfile]: ...

    @abstractmethod
    def get_all_threshold_profiles(self) -> list[ThresholdProfile]: ...

    @abstractmethod
    def get_threshold_profile_by_id(self, profile_id: str) -> Optional[ThresholdProfile]: ...

    # ── Scope Selectors ──────────────────────────────────────────

    @abstractmethod
    def get_all_scope_selectors(self) -> list[ScopeSelector]: ...

    @abstractmethod
    def get_scope_selector_by_id(self, scope_id: str) -> Optional[ScopeSelector]: ...

    # ── Data Sources ─────────────────────────────────────────────

    @abstractmethod
    def get_all_data_sources(self) -> list[DataSource]: ...

    # ── Execution Scopes ─────────────────────────────────────────

    @abstractmethod
    def get_all_execution_scopes(self) -> list[ExecutionScope]: ...

    # ── Versions ─────────────────────────────────────────────────

    @abstractmethod
    def get_all_versions(self) -> list[VersionSnapshot]: ...

    @abstractmethod
    def get_versions_by_baseline_id(self, baseline_id: str) -> list[VersionSnapshot]: ...

    @abstractmethod
    def get_version_by_id(self, version_id: str) -> Optional[VersionSnapshot]: ...

    @abstractmethod
    def get_version_diff(self, diff_id: str) -> Optional[VersionDiffSnapshot]: ...

    @abstractmethod
    def get_version_count(self) -> int: ...

    # ── Runs ─────────────────────────────────────────────────────

    @abstractmethod
    def get_all_runs(self) -> list[RunHistoryEntry]: ...

    @abstractmethod
    def get_run_by_id(self, run_id: str) -> Optional[RunHistoryEntry]: ...

    # ── Bundles ──────────────────────────────────────────────────

    @abstractmethod
    def get_bundle_by_id(self, bundle_id: str) -> Optional[CheckResultBundle]: ...

    # ── Issues ───────────────────────────────────────────────────

    @abstractmethod
    def get_issue_by_id(self, issue_id: str) -> Optional[IssueItem]: ...

    # ── Recheck Diff ─────────────────────────────────────────────

    @abstractmethod
    def get_recheck_diff(self, diff_id: str) -> Optional[RecheckDiffSnapshot]: ...
