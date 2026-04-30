# backend/data/mock_data.py
# Mock data for the API skeleton
# This data is compatible with frontend/src/api/contracts.ts
# NOT connected to real database or check engine

from typing import Optional
from ..models.baseline import (
    Baseline,
    RuleSet,
    RuleDefinition,
    ParameterProfile,
    ThresholdProfile,
    ScopeSelector,
    ParameterDefinition,
    ConditionExpression,
)
from ..models.execution import (
    DataSource,
    ExecutionScope,
    RecognitionResult,
    RunHistoryEntry,
    CheckResultBundle,
    IssueItem,
    SeveritySummary,
)
from ..models.version import VersionSnapshot, VersionDiffSnapshot, VersionChangeSummary
from ..models.diff import RecheckDiffSnapshot, IssueCountChange

MOCK_BASELINES: list[Baseline] = [
    Baseline(
        id="baseline-001",
        name="Production Baseline v1",
        description="Main production baseline for network topology validation",
        version="v1.0.0",
        status="published",
        identification_strategy={"strategy": "topology_match"},
    ),
    Baseline(
        id="baseline-002",
        name="Staging Baseline v1",
        description="Staging baseline for testing",
        version="v1.0.0",
        status="draft",
        identification_strategy={"strategy": "topology_match"},
    ),
]

MOCK_RULESETS: list[RuleSet] = [
    RuleSet(
        ruleset_id="rs-001",
        name="Duplicate Entity Rules",
        description="Rules for detecting duplicate entities",
        rule_ids=["rule-001", "rule-002"],
    ),
    RuleSet(
        ruleset_id="rs-002",
        name="Link Consistency Rules",
        description="Rules for link consistency validation",
        rule_ids=["rule-003", "rule-004"],
    ),
    RuleSet(
        ruleset_id="rs-003",
        name="Threshold Rules",
        description="Rules based on threshold checks",
        rule_ids=["rule-005", "rule-006"],
    ),
    RuleSet(
        ruleset_id="rs-004",
        name="Topology Rules",
        description="Rules for topology validation",
        rule_ids=["rule-007", "rule-008"],
    ),
]

MOCK_RULES: list[RuleDefinition] = [
    RuleDefinition(
        id="rule-001",
        name="Duplicate Device Name Check",
        enabled=True,
        category="duplicate",
        severity="high",
        condition=ConditionExpression(expression="entity.device_name == other.device_name"),
        parameters=[],
        description="Checks for duplicate device names",
    ),
]

MOCK_PARAMETER_PROFILES: list[ParameterProfile] = [
    ParameterProfile(
        profile_id="pp-001",
        name="Default Parameters",
        description="Default parameter profile",
        parameters={"tolerance": 0.01, "timeout": 30},
    ),
]

MOCK_THRESHOLD_PROFILES: list[ThresholdProfile] = [
    ThresholdProfile(
        profile_id="tp-001",
        name="Default Thresholds",
        description="Default threshold profile",
        thresholds={"max_duplicates": 0, "min_confidence": 0.9},
    ),
]

MOCK_SCOPE_SELECTORS: list[ScopeSelector] = [
    ScopeSelector(
        scope_id="sc-001",
        name="Full Topology",
        description="Full network topology scope",
        selector_type="topology",
    ),
]

MOCK_DATA_SOURCES: list[DataSource] = [
    DataSource(
        dataset_id="ds-001",
        name="Production Network Export",
        device_count=150,
        description="Production network topology export",
    ),
    DataSource(
        dataset_id="ds-002",
        name="Staging Network Export",
        device_count=50,
        description="Staging network topology export",
    ),
]

MOCK_EXECUTION_SCOPES: list[ExecutionScope] = [
    ExecutionScope(
        scope_id="scope-full",
        method="full_topology",
        description="Full topology check",
    ),
    ExecutionScope(
        scope_id="scope-diff",
        method="diff_only",
        description="Diff only check",
    ),
]

MOCK_VERSION_SNAPSHOTS: dict[str, VersionSnapshot] = {
    "baseline-001::v1.0.0": VersionSnapshot(
        version_id="baseline-001::v1.0.0",
        baseline_id="baseline-001",
        version="v1.0.0",
        description="Initial version",
        status="published",
        rule_count=8,
    ),
    "baseline-001::v1.1.0": VersionSnapshot(
        version_id="baseline-001::v1.1.0",
        baseline_id="baseline-001",
        version="v1.1.0",
        description="Added new rules",
        status="published",
        rule_count=10,
    ),
}

MOCK_VERSION_DIFF_SNAPSHOTS: dict[str, VersionDiffSnapshot] = {
    "baseline-001::v1.0.0->baseline-001::v1.1.0": VersionDiffSnapshot(
        diff_id="baseline-001::v1.0.0->baseline-001::v1.1.0",
        from_version="baseline-001::v1.0.0",
        to_version="baseline-001::v1.1.0",
        summary={"added": 2, "removed": 0, "modified": 1},
        rule_changes=[],
        field_changes=[],
    ),
}

MOCK_RUNS: list[RunHistoryEntry] = [
    RunHistoryEntry(
        run_id="run-001",
        baseline_id="baseline-001",
        baseline_name="Production Baseline v1",
        scenario_id="scenario-001",
        status="completed",
        severity_summary=SeveritySummary(critical=0, high=2, medium=5, low=3, info=0),
        device_count=150,
        issue_count=10,
        data_source_id="ds-001",
        scope_id="scope-full",
        bundle_id="bundle-001",
    ),
    RunHistoryEntry(
        run_id="run-002",
        baseline_id="baseline-001",
        baseline_name="Production Baseline v1",
        scenario_id="scenario-002",
        status="completed",
        severity_summary=SeveritySummary(critical=1, high=3, medium=4, low=2, info=0),
        device_count=150,
        issue_count=10,
        data_source_id="ds-001",
        scope_id="scope-full",
        bundle_id="bundle-002",
    ),
]

MOCK_BUNDLES: dict[str, CheckResultBundle] = {
    "bundle-001": CheckResultBundle(
        bundle_id="bundle-001",
        run_id="run-001",
        baseline_id="baseline-001",
        severity_summary=SeveritySummary(critical=0, high=2, medium=5, low=3, info=0),
        issue_count=10,
        issues=[
            IssueItem(
                issue_id="issue-001",
                run_id="run-001",
                rule_id="rule-001",
                rule_name="Duplicate Device Name",
                severity="high",
                entity_type="device",
                entity_id="dev-001",
                entity_name="Router-A",
                message="Duplicate device name found",
            ),
        ],
    ),
}

MOCK_RECHECK_DIFF_SNAPSHOTS: dict[str, RecheckDiffSnapshot] = {
    "run-001->run-002": RecheckDiffSnapshot(
        diff_id="run-001->run-002",
        base_run_id="run-001",
        target_run_id="run-002",
        summary={"status": "generated"},
        issue_count_change=IssueCountChange(added=1, removed=0, unchanged=9),
        severity_change={"high": 1},
        added_issues=[
            IssueItem(
                issue_id="issue-new-001",
                run_id="run-002",
                rule_id="rule-002",
                rule_name="Link Inconsistency",
                severity="high",
                entity_type="link",
                entity_id="link-001",
                entity_name="Link-A-B",
                message="Link inconsistency detected",
            ),
        ],
        removed_issues=[],
        changed_issues=[],
        unchanged_issues=[],
    ),
}

BASELINE_PROFILE_MAP: dict[str, dict] = {
    "baseline-001": {
        "parameter_profile_id": "pp-001",
        "threshold_profile_id": "tp-001",
        "scope_selector_id": "sc-001",
        "ruleset_ids": ["rs-001", "rs-002", "rs-003", "rs-004"],
    },
    "baseline-002": {
        "parameter_profile_id": "pp-001",
        "threshold_profile_id": "tp-001",
        "scope_selector_id": "sc-001",
        "ruleset_ids": ["rs-001", "rs-002"],
    },
}

BASELINE_VERSION_SNAPSHOTS: dict[str, dict] = {
    "baseline-001": {
        "baseline_id": "baseline-001",
        "current_version": "v1.1.0",
        "previous_version": "v1.0.0",
        "rule_added_count": 2,
        "rule_removed_count": 0,
        "parameter_changed_count": 1,
        "threshold_changed_count": 0,
    },
}