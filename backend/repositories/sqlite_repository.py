# backend/repositories/sqlite_repository.py
# SQLite repository scaffold.
# NOT enabled by default. All methods raise NotImplementedError or return None.
# Future Phase 2 will implement actual SQLite persistence.

from typing import Optional

from .interface import Repository
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


class SQLiteRepository(Repository):
    """SQLite-backed repository scaffold.

    Status: NOT IMPLEMENTED
    This class exists as a placeholder for future database integration.
    Do NOT use in production until fully implemented.

    Migration plan:
    1. Define SQLite schema matching mock_data structures
    2. Implement each method with actual SQL queries
    3. Add connection pooling and transaction support
    4. Switch provider default from MockRepository to SQLiteRepository
    """

    def __init__(self, db_path: str = "topochecker.db"):
        self.db_path = db_path

    # ── Baselines ────────────────────────────────────────────────

    def get_all_baselines(self) -> list[Baseline]:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    def get_baseline_by_id(self, baseline_id: str) -> Optional[Baseline]:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    def get_baseline_profile_map(self, baseline_id: str) -> Optional[dict]:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    def get_baseline_version_snapshot(self, baseline_id: str) -> Optional[dict]:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    # ── Rulesets ─────────────────────────────────────────────────

    def get_all_rulesets(self) -> list[RuleSet]:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    def get_rulesets_by_ids(self, ruleset_ids: list[str]) -> list[RuleSet]:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    # ── Rules ────────────────────────────────────────────────────

    def get_all_rules(self) -> list[RuleDefinition]:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    def get_rule_by_id(self, rule_id: str) -> Optional[RuleDefinition]:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    # ── Profiles ─────────────────────────────────────────────────

    def get_all_parameter_profiles(self) -> list[ParameterProfile]:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    def get_parameter_profile_by_id(self, profile_id: str) -> Optional[ParameterProfile]:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    def get_all_threshold_profiles(self) -> list[ThresholdProfile]:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    def get_threshold_profile_by_id(self, profile_id: str) -> Optional[ThresholdProfile]:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    # ── Scope Selectors ──────────────────────────────────────────

    def get_all_scope_selectors(self) -> list[ScopeSelector]:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    def get_scope_selector_by_id(self, scope_id: str) -> Optional[ScopeSelector]:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    # ── Data Sources ─────────────────────────────────────────────

    def get_all_data_sources(self) -> list[DataSource]:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    # ── Execution Scopes ─────────────────────────────────────────

    def get_all_execution_scopes(self) -> list[ExecutionScope]:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    # ── Versions ─────────────────────────────────────────────────

    def get_all_versions(self) -> list[VersionSnapshot]:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    def get_versions_by_baseline_id(self, baseline_id: str) -> list[VersionSnapshot]:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    def get_version_by_id(self, version_id: str) -> Optional[VersionSnapshot]:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    def get_version_diff(self, diff_id: str) -> Optional[VersionDiffSnapshot]:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    def get_version_count(self) -> int:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    # ── Runs ─────────────────────────────────────────────────────

    def get_all_runs(self) -> list[RunHistoryEntry]:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    def get_run_by_id(self, run_id: str) -> Optional[RunHistoryEntry]:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    # ── Bundles ──────────────────────────────────────────────────

    def get_bundle_by_id(self, bundle_id: str) -> Optional[CheckResultBundle]:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    # ── Issues ───────────────────────────────────────────────────

    def get_issue_by_id(self, issue_id: str) -> Optional[IssueItem]:
        raise NotImplementedError("SQLiteRepository not yet implemented")

    # ── Recheck Diff ─────────────────────────────────────────────

    def get_recheck_diff(self, diff_id: str) -> Optional[RecheckDiffSnapshot]:
        raise NotImplementedError("SQLiteRepository not yet implemented")
