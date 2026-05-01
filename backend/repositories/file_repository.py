# backend/repositories/file_repository.py
# Local JSON file repository scaffold.
# Reads/writes workspace/ JSON files. No database, no ORM, no SQLite.

from typing import Optional

from .interface import Repository
from ..workspace.manager import WorkspaceManager
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


class FileRepository(Repository):
    """Repository backed by local workspace JSON files.

    Status: PARTIALLY IMPLEMENTED
    - Task/Run/Snapshot save/load implemented
    - Baseline/Rule/Profile read falls back to MockRepository until migration

    Migration plan:
    1. Save all mock data as JSON files to workspace/
    2. Implement remaining read methods
    3. Switch provider default from MockRepository to FileRepository
    """

    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace = WorkspaceManager(workspace_root)
        # Fallback to mock for reads until data is migrated
        from .mock_repository import MockRepository
        self._mock = MockRepository()

    # ── Baselines (fallback to mock until migrated) ──────────────

    def get_all_baselines(self) -> list[Baseline]:
        return self._mock.get_all_baselines()

    def get_baseline_by_id(self, baseline_id: str) -> Optional[Baseline]:
        return self._mock.get_baseline_by_id(baseline_id)

    def get_baseline_profile_map(self, baseline_id: str) -> Optional[dict]:
        return self._mock.get_baseline_profile_map(baseline_id)

    def get_baseline_version_snapshot(self, baseline_id: str) -> Optional[dict]:
        return self._mock.get_baseline_version_snapshot(baseline_id)

    # ── Rulesets (fallback to mock until migrated) ───────────────

    def get_all_rulesets(self) -> list[RuleSet]:
        return self._mock.get_all_rulesets()

    def get_rulesets_by_ids(self, ruleset_ids: list[str]) -> list[RuleSet]:
        return self._mock.get_rulesets_by_ids(ruleset_ids)

    # ── Rules (fallback to mock until migrated) ──────────────────

    def get_all_rules(self) -> list[RuleDefinition]:
        return self._mock.get_all_rules()

    def get_rule_by_id(self, rule_id: str) -> Optional[RuleDefinition]:
        return self._mock.get_rule_by_id(rule_id)

    # ── Profiles (fallback to mock until migrated) ───────────────

    def get_all_parameter_profiles(self) -> list[ParameterProfile]:
        return self._mock.get_all_parameter_profiles()

    def get_parameter_profile_by_id(self, profile_id: str) -> Optional[ParameterProfile]:
        return self._mock.get_parameter_profile_by_id(profile_id)

    def get_all_threshold_profiles(self) -> list[ThresholdProfile]:
        return self._mock.get_all_threshold_profiles()

    def get_threshold_profile_by_id(self, profile_id: str) -> Optional[ThresholdProfile]:
        return self._mock.get_threshold_profile_by_id(profile_id)

    # ── Scope Selectors (fallback to mock until migrated) ────────

    def get_all_scope_selectors(self) -> list[ScopeSelector]:
        return self._mock.get_all_scope_selectors()

    def get_scope_selector_by_id(self, scope_id: str) -> Optional[ScopeSelector]:
        return self._mock.get_scope_selector_by_id(scope_id)

    # ── Data Sources (fallback to mock until migrated) ───────────

    def get_all_data_sources(self) -> list[DataSource]:
        return self._mock.get_all_data_sources()

    # ── Execution Scopes (fallback to mock until migrated) ───────

    def get_all_execution_scopes(self) -> list[ExecutionScope]:
        return self._mock.get_all_execution_scopes()

    # ── Versions (fallback to mock until migrated) ───────────────

    def get_all_versions(self) -> list[VersionSnapshot]:
        return self._mock.get_all_versions()

    def get_versions_by_baseline_id(self, baseline_id: str) -> list[VersionSnapshot]:
        return self._mock.get_versions_by_baseline_id(baseline_id)

    def get_version_by_id(self, version_id: str) -> Optional[VersionSnapshot]:
        return self._mock.get_version_by_id(version_id)

    def get_version_diff(self, diff_id: str) -> Optional[VersionDiffSnapshot]:
        return self._mock.get_version_diff(diff_id)

    def get_version_count(self) -> int:
        return self._mock.get_version_count()

    # ── Runs (partially implemented: save/load via workspace) ─────

    def get_all_runs(self) -> list[RunHistoryEntry]:
        # Try workspace first, fallback to mock
        ws_runs = self.workspace.list_runs()
        if ws_runs:
            return [RunHistoryEntry(**r) for r in ws_runs]
        return self._mock.get_all_runs()

    def get_run_by_id(self, run_id: str) -> Optional[RunHistoryEntry]:
        ws_run = self.workspace.load_run(run_id)
        if ws_run:
            return RunHistoryEntry(**ws_run)
        return self._mock.get_run_by_id(run_id)

    # ── Bundles (fallback to mock until migrated) ────────────────

    def get_bundle_by_id(self, bundle_id: str) -> Optional[CheckResultBundle]:
        return self._mock.get_bundle_by_id(bundle_id)

    # ── Issues (fallback to mock until migrated) ─────────────────

    def get_issue_by_id(self, issue_id: str) -> Optional[IssueItem]:
        return self._mock.get_issue_by_id(issue_id)

    # ── Recheck Diff (fallback to mock until migrated) ───────────

    def get_recheck_diff(self, diff_id: str) -> Optional[RecheckDiffSnapshot]:
        return self._mock.get_recheck_diff(diff_id)

    # ── Workspace-specific methods ───────────────────────────────

    def save_task(self, task: dict) -> None:
        """Save a task to workspace."""
        self.workspace.save_task(task)

    def save_run(self, run: dict) -> None:
        """Save a run to workspace."""
        self.workspace.save_run(run)

    def save_snapshot(self, snapshot: dict) -> None:
        """Save a snapshot to workspace."""
        self.workspace.save_snapshot(snapshot)

    def save_report(self, report: dict, content: str) -> None:
        """Save a report to workspace."""
        self.workspace.save_report(report, content)
