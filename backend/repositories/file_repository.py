# backend/repositories/file_repository.py
# Local JSON file repository scaffold.
# Reads/writes workspace/ JSON files. No database, no ORM, no SQLite.

import json
from typing import Optional, List, Dict, Any

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

    Status: PHASE 2 — Fixture-aware
    - Reads workspace JSON files first, falls back to MockRepository if missing
    - Task/Run/Snapshot save/load implemented via WorkspaceManager
    - Baseline/Rule/Profile read from workspace/inputs/ JSON or fallback to mock

    Migration plan:
    1. Run scripts/export_mock_to_workspace.sh to populate workspace/
    2. FileRepository reads from workspace JSON files
    3. Switch provider default from MockRepository to FileRepository
    """

    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace = WorkspaceManager(workspace_root)
        # Fallback to mock for reads until data is migrated
        from .mock_repository import MockRepository
        self._mock = MockRepository()

    # ── Helper: load JSON from workspace/inputs ──────────────────

    def _load_json(self, filename: str) -> Optional[Any]:
        """Load a JSON file from workspace/inputs/."""
        path = self.workspace.paths.inputs / filename
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_json_list(self, filename: str) -> List[Dict[str, Any]]:
        """Load a JSON list from workspace/inputs/, fallback to empty list."""
        data = self._load_json(filename)
        if data is None:
            return []
        if isinstance(data, list):
            return data
        return []

    def _load_json_dict(self, filename: str) -> Dict[str, Any]:
        """Load a JSON dict from workspace/inputs/, fallback to empty dict."""
        data = self._load_json(filename)
        if data is None:
            return {}
        if isinstance(data, dict):
            return data
        return {}

    # ── Baselines (read from workspace, fallback to mock) ────────

    def get_all_baselines(self) -> List[Baseline]:
        data = self._load_json_list("baselines.json")
        if data:
            return [Baseline(**item) for item in data]
        # Fallback: try individual baseline files
        baselines = []
        for path in self.workspace.paths.inputs.glob("baseline_*.json"):
            with open(path, "r", encoding="utf-8") as f:
                baselines.append(Baseline(**json.load(f)))
        if baselines:
            return baselines
        return self._mock.get_all_baselines()

    def get_baseline_by_id(self, baseline_id: str) -> Optional[Baseline]:
        path = self.workspace.paths.inputs / f"baseline_{baseline_id}.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return Baseline(**json.load(f))
        # Try baselines.json
        data = self._load_json_list("baselines.json")
        for item in data:
            if item.get("id") == baseline_id:
                return Baseline(**item)
        return self._mock.get_baseline_by_id(baseline_id)

    def get_baseline_profile_map(self, baseline_id: str) -> Optional[Dict]:
        data = self._load_json_dict("baseline_profile_map.json")
        if baseline_id in data:
            return data[baseline_id]
        return self._mock.get_baseline_profile_map(baseline_id)

    def get_baseline_version_snapshot(self, baseline_id: str) -> Optional[Dict]:
        data = self._load_json_dict("baseline_version_snapshots.json")
        if baseline_id in data:
            return data[baseline_id]
        return self._mock.get_baseline_version_snapshot(baseline_id)

    # ── Rulesets (read from workspace, fallback to mock) ─────────

    def get_all_rulesets(self) -> List[RuleSet]:
        data = self._load_json_list("rulesets.json")
        if data:
            return [RuleSet(**item) for item in data]
        return self._mock.get_all_rulesets()

    def get_rulesets_by_ids(self, ruleset_ids: List[str]) -> List[RuleSet]:
        all_rulesets = self.get_all_rulesets()
        return [rs for rs in all_rulesets if rs.ruleset_id in ruleset_ids]

    # ── Rules (read from workspace, fallback to mock) ────────────

    def get_all_rules(self) -> List[RuleDefinition]:
        data = self._load_json_list("rules.json")
        if data:
            return [RuleDefinition(**item) for item in data]
        return self._mock.get_all_rules()

    def get_rule_by_id(self, rule_id: str) -> Optional[RuleDefinition]:
        data = self._load_json_list("rules.json")
        for item in data:
            if item.get("id") == rule_id:
                return RuleDefinition(**item)
        return self._mock.get_rule_by_id(rule_id)

    # ── Profiles (read from workspace, fallback to mock) ─────────

    def get_all_parameter_profiles(self) -> List[ParameterProfile]:
        data = self._load_json_list("parameter_profiles.json")
        if data:
            return [ParameterProfile(**item) for item in data]
        return self._mock.get_all_parameter_profiles()

    def get_parameter_profile_by_id(self, profile_id: str) -> Optional[ParameterProfile]:
        data = self._load_json_list("parameter_profiles.json")
        for item in data:
            if item.get("profile_id") == profile_id:
                return ParameterProfile(**item)
        return self._mock.get_parameter_profile_by_id(profile_id)

    def get_all_threshold_profiles(self) -> List[ThresholdProfile]:
        data = self._load_json_list("threshold_profiles.json")
        if data:
            return [ThresholdProfile(**item) for item in data]
        return self._mock.get_all_threshold_profiles()

    def get_threshold_profile_by_id(self, profile_id: str) -> Optional[ThresholdProfile]:
        data = self._load_json_list("threshold_profiles.json")
        for item in data:
            if item.get("profile_id") == profile_id:
                return ThresholdProfile(**item)
        return self._mock.get_threshold_profile_by_id(profile_id)

    # ── Scope Selectors (read from workspace, fallback to mock) ──

    def get_all_scope_selectors(self) -> List[ScopeSelector]:
        data = self._load_json_list("scope_selectors.json")
        if data:
            return [ScopeSelector(**item) for item in data]
        return self._mock.get_all_scope_selectors()

    def get_scope_selector_by_id(self, scope_id: str) -> Optional[ScopeSelector]:
        data = self._load_json_list("scope_selectors.json")
        for item in data:
            if item.get("scope_id") == scope_id:
                return ScopeSelector(**item)
        return self._mock.get_scope_selector_by_id(scope_id)

    # ── Data Sources (read from workspace, fallback to mock) ─────

    def get_all_data_sources(self) -> List[DataSource]:
        data = self._load_json_list("data_sources.json")
        if data:
            return [DataSource(**item) for item in data]
        return self._mock.get_all_data_sources()

    # ── Execution Scopes (read from workspace, fallback to mock) ─

    def get_all_execution_scopes(self) -> List[ExecutionScope]:
        data = self._load_json_list("execution_scopes.json")
        if data:
            return [ExecutionScope(**item) for item in data]
        return self._mock.get_all_execution_scopes()

    # ── Versions (read from workspace, fallback to mock) ─────────

    def get_all_versions(self) -> List[VersionSnapshot]:
        snapshots = self.workspace.list_snapshots()
        if snapshots:
            return [VersionSnapshot(**s) for s in snapshots]
        return self._mock.get_all_versions()

    def get_versions_by_baseline_id(self, baseline_id: str) -> List[VersionSnapshot]:
        snapshots = self.workspace.list_snapshots()
        result = []
        for snap in snapshots:
            if snap.get("baseline_id") == baseline_id:
                result.append(VersionSnapshot(**snap))
        if result:
            return result
        return self._mock.get_versions_by_baseline_id(baseline_id)

    def get_version_by_id(self, version_id: str) -> Optional[VersionSnapshot]:
        snap = self.workspace.load_snapshot(version_id)
        if snap:
            return VersionSnapshot(**snap)
        return self._mock.get_version_by_id(version_id)

    def get_version_diff(self, diff_id: str) -> Optional[VersionDiffSnapshot]:
        data = self._load_json_dict("version_diffs.json")
        if diff_id in data:
            return VersionDiffSnapshot(**data[diff_id])
        return self._mock.get_version_diff(diff_id)

    def get_version_count(self) -> int:
        count = len(self.workspace.list_snapshots())
        if count > 0:
            return count
        return self._mock.get_version_count()

    # ── Runs (read from workspace, fallback to mock) ─────────────

    def get_all_runs(self) -> List[RunHistoryEntry]:
        ws_runs = self.workspace.list_runs()
        if ws_runs:
            return [RunHistoryEntry(**r) for r in ws_runs]
        return self._mock.get_all_runs()

    def get_run_by_id(self, run_id: str) -> Optional[RunHistoryEntry]:
        ws_run = self.workspace.load_run(run_id)
        if ws_run:
            return RunHistoryEntry(**ws_run)
        return self._mock.get_run_by_id(run_id)

    # ── Bundles (read from workspace, fallback to mock) ──────────

    def get_bundle_by_id(self, bundle_id: str) -> Optional[CheckResultBundle]:
        data = self._load_json_dict("bundles.json")
        if bundle_id in data:
            return CheckResultBundle(**data[bundle_id])
        return self._mock.get_bundle_by_id(bundle_id)

    # ── Issues (read from workspace, fallback to mock) ───────────

    def get_issue_by_id(self, issue_id: str) -> Optional[IssueItem]:
        data = self._load_json_dict("bundles.json")
        for bundle in data.values():
            for issue in bundle.get("issues", []):
                if issue.get("issue_id") == issue_id:
                    return IssueItem(**issue)
        return self._mock.get_issue_by_id(issue_id)

    # ── Recheck Diff (read from workspace, fallback to mock) ─────

    def get_recheck_diff(self, diff_id: str) -> Optional[RecheckDiffSnapshot]:
        data = self._load_json_dict("recheck_diffs.json")
        if diff_id in data:
            return RecheckDiffSnapshot(**data[diff_id])
        return self._mock.get_recheck_diff(diff_id)

    # ── Workspace-specific write methods ─────────────────────────

    def save_task(self, task: Dict[str, Any]) -> None:
        """Save a task to workspace."""
        self.workspace.save_task(task)

    def save_run(self, run: Dict[str, Any]) -> None:
        """Save a run to workspace."""
        self.workspace.save_run(run)

    def save_snapshot(self, snapshot: Dict[str, Any]) -> None:
        """Save a snapshot to workspace."""
        self.workspace.save_snapshot(snapshot)

    def save_report(self, report: Dict[str, Any], content: str) -> None:
        """Save a report to workspace."""
        self.workspace.save_report(report, content)
