"""
A2-3: Group Consistency Executor Unit Tests

Verifies that the group_consistency executor executes correctly.
These tests prove the group_consistency executor is NOT "伪执行" (fake execution).

Covers:
- Dominant value detection: items that differ from the group's dominant value
- Parameter resolution: parameter_profile vs inline params
- Edge grouping cases: single-element groups, empty groups, all-consistent groups
- Empty/degenerate inputs: empty dataset, all None group keys
"""

import pytest
from src.domain.executors.group_consistency_executor import GroupConsistencyExecutor
from src.domain.rule_engine.compiled_rule import CompiledRule
from src.domain.rule_engine.execution_context import ExecutionContext
from src.domain.fact_model import DeviceFact, PortFact
from src.domain.result_model import IssueItem


def _make_compiled_rule(rule_id: str, group_key: str, comparison_field: str,
                        parameter_key: str = None,
                        target_type: str = "devices", severity: str = "warning") -> CompiledRule:
    """Helper to create CompiledRule for group_consistency executor tests."""
    params = {}
    if parameter_key:
        params["parameter_key"] = parameter_key
    else:
        params["group_key"] = group_key
        params["comparison_field"] = comparison_field

    kwargs = {}
    if parameter_key:
        kwargs["parameter_key"] = parameter_key
    else:
        kwargs["group_key"] = group_key
        kwargs["comparison_field"] = comparison_field

    return CompiledRule(
        rule_id=rule_id,
        rule_type="template",
        executor={"type": "group_consistency"},
        target={"type": target_type, "filter": None},
        message={"template": f"Rule {rule_id} group_consistency check"},
        severity=severity,
        params=params,
        **kwargs,
    )


def _make_context(parameter_profile=None, threshold_profile=None) -> ExecutionContext:
    return ExecutionContext(
        parameter_profile=parameter_profile or {},
        threshold_profile=threshold_profile or {},
        runtime_flags={},
    )


# ==========================================
# Dominant Value Detection
# ==========================================

class TestDominantValueDetection:
    """Detects items that differ from the group's dominant value."""

    def test_detects_inconsistent_value_in_group(self):
        executor = GroupConsistencyExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Building-A", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW2", device_type="Building-A", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW3", device_type="Building-A", status="down", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("gc_rule", "device_type", "status")
        result = executor.execute("gc_rule", compiled, {"devices": devices}, _make_context())
        # Building-A: 2x "up", 1x "down" → dominant="up", SW3 is inconsistent
        assert len(result) == 1
        assert result[0].actual == "down"
        assert result[0].expected == "up"

    def test_no_issue_when_all_consistent(self):
        executor = GroupConsistencyExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Building-A", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW2", device_type="Building-A", status="up", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("gc_rule", "device_type", "status")
        result = executor.execute("gc_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 0

    def test_multiple_groups_with_inconsistencies(self):
        executor = GroupConsistencyExecutor()
        devices = [
            # Building-A: 2 up, 1 down → 1 issue
            DeviceFact(device_name="SW1", device_type="Building-A", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW2", device_type="Building-A", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW3", device_type="Building-A", status="down", _source_sheet="s1"),
            # Building-B: 1 up, 2 down → 1 issue (up is minority)
            DeviceFact(device_name="SW4", device_type="Building-B", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW5", device_type="Building-B", status="down", _source_sheet="s1"),
            DeviceFact(device_name="SW6", device_type="Building-B", status="down", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("gc_rule", "device_type", "status")
        result = executor.execute("gc_rule", compiled, {"devices": devices}, _make_context())
        # Building-A: 1 issue (SW3), Building-B: 1 issue (SW4)
        assert len(result) == 2

    def test_dominant_is_most_frequent(self):
        """When there's a clear dominant value, only the minority is flagged."""
        executor = GroupConsistencyExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Building-A", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW2", device_type="Building-A", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW3", device_type="Building-A", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW4", device_type="Building-A", status="down", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("gc_rule", "device_type", "status")
        result = executor.execute("gc_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1
        assert result[0].actual == "down"

    def test_tie_in_values(self):
        """When two values have equal frequency, the first encountered is dominant."""
        executor = GroupConsistencyExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Building-A", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW2", device_type="Building-A", status="down", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("gc_rule", "device_type", "status")
        result = executor.execute("gc_rule", compiled, {"devices": devices}, _make_context())
        # With 2 items and different values, len(val_counts)=2 > 1, so one will be flagged
        assert len(result) == 1


# ==========================================
# Parameter Resolution
# ==========================================

class TestParameterResolution:
    """Tests parameter_profile vs inline params resolution."""

    def test_uses_parameter_profile_when_key_exists(self):
        executor = GroupConsistencyExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Building-A", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW2", device_type="Building-A", status="down", _source_sheet="s1"),
        ]
        ctx = _make_context(parameter_profile={
            "P1": {"group_key": "device_type", "comparison_field": "status"}
        })
        compiled = _make_compiled_rule("profile_rule", "unused_key", "unused_field", parameter_key="P1")
        result = executor.execute("profile_rule", compiled, {"devices": devices}, ctx)
        assert len(result) == 1

    def test_uses_inline_when_no_parameter_key(self):
        executor = GroupConsistencyExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Building-A", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW2", device_type="Building-A", status="down", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("inline_rule", "device_type", "status")
        result = executor.execute("inline_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1

    def test_evidence_shows_parameter_source(self):
        executor = GroupConsistencyExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Building-A", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW2", device_type="Building-A", status="down", _source_sheet="s1"),
        ]
        # Test with parameter_profile
        ctx = _make_context(parameter_profile={
            "P1": {"group_key": "device_type", "comparison_field": "status"}
        })
        compiled = _make_compiled_rule("source_rule", "unused", "unused", parameter_key="P1")
        result = executor.execute("source_rule", compiled, {"devices": devices}, ctx)
        assert len(result) == 1
        assert result[0].evidence["parameter_source"] == "parameter_profile"

    def test_evidence_shows_inline_source(self):
        executor = GroupConsistencyExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Building-A", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW2", device_type="Building-A", status="down", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("inline_rule", "device_type", "status")
        result = executor.execute("inline_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1
        assert result[0].evidence["parameter_source"] == "inline"


# ==========================================
# Edge Grouping Cases
# ==========================================

class TestEdgeGroupingCases:
    """Edge cases for grouping logic."""

    def test_single_element_group_no_issue(self):
        """A group with only 1 item has no consistency to check."""
        executor = GroupConsistencyExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Building-A", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW2", device_type="Building-B", status="down", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("single_rule", "device_type", "status")
        result = executor.execute("single_rule", compiled, {"devices": devices}, _make_context())
        # Each group has only 1 member → skip (len(items) <= 1)
        assert len(result) == 0

    def test_all_same_values_no_issue(self):
        """Group where all items have the same comparison value."""
        executor = GroupConsistencyExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Building-A", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW2", device_type="Building-A", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW3", device_type="Building-A", status="up", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("consistent_rule", "device_type", "status")
        result = executor.execute("consistent_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 0

    def test_items_with_none_group_key_are_skipped(self):
        """Items with None group_key should be skipped (not grouped)."""
        executor = GroupConsistencyExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type=None, status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW2", device_type=None, status="down", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("none_key_rule", "device_type", "status")
        result = executor.execute("none_key_rule", compiled, {"devices": devices}, _make_context())
        # Both have None group key → skipped → no issues
        assert len(result) == 0

    def test_port_facts_grouping(self):
        """Group consistency works on port facts too."""
        executor = GroupConsistencyExecutor()
        ports = [
            PortFact(device_name="SW1", port_name="Gi0/1", port_status="up", _source_sheet="s1"),
            PortFact(device_name="SW1", port_name="Gi0/2", port_status="up", _source_sheet="s1"),
            PortFact(device_name="SW1", port_name="Gi0/3", port_status="down", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("port_gc_rule", "device_name", "port_status", target_type="ports")
        result = executor.execute("port_gc_rule", compiled, {"ports": ports}, _make_context())
        assert len(result) == 1
        assert result[0].actual == "down"
        assert result[0].expected == "up"


# ==========================================
# Empty / Degenerate Inputs
# ==========================================

class TestEmptyAndDegenerateInputs:
    """Empty datasets and degenerate inputs."""

    def test_empty_dataset_returns_no_issues(self):
        executor = GroupConsistencyExecutor()
        compiled = _make_compiled_rule("empty_rule", "device_type", "status")
        result = executor.execute("empty_rule", compiled, {"devices": []}, _make_context())
        assert result == []

    def test_missing_target_type_returns_no_issues(self):
        """If target_type doesn't exist in dataset, empty list is returned."""
        executor = GroupConsistencyExecutor()
        compiled = _make_compiled_rule("missing_type_rule", "device_type", "status")
        result = executor.execute("missing_type_rule", compiled, {"links": []}, _make_context())
        assert result == []

    def test_severity_propagated_to_issues(self):
        executor = GroupConsistencyExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Building-A", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW2", device_type="Building-A", status="down", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("sev_rule", "device_type", "status", severity="critical")
        result = executor.execute("sev_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1
        assert result[0].severity == "critical"

    def test_issue_message_contains_group_key(self):
        executor = GroupConsistencyExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Building-A", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW2", device_type="Building-A", status="down", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("msg_rule", "device_type", "status")
        result = executor.execute("msg_rule", compiled, {"devices": devices}, _make_context())
        assert "Building-A" in result[0].message
        assert "inconsistent" in result[0].message.lower()

    def test_category_is_group_consistency(self):
        executor = GroupConsistencyExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Building-A", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW2", device_type="Building-A", status="down", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("cat_rule", "device_type", "status")
        result = executor.execute("cat_rule", compiled, {"devices": devices}, _make_context())
        assert result[0].category == "group_consistency"

    def test_parameter_key_not_found_falls_back_to_inline(self):
        """If parameter_key is specified but not in profile, falls back to compiled_rule params.
        
        When parameter_key="P_MISSING" is not in profile, the executor falls back to
        compiled_rule.get("group_key") and compiled_rule.get("comparison_field").
        Since we provided parameter_key instead of inline group_key/comparison_field,
        both will be None, causing getattr to raise TypeError.
        
        This is a known edge case in the executor — it does not gracefully handle
        missing parameter resolution. The test documents this behavior.
        """
        executor = GroupConsistencyExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Building-A", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW2", device_type="Building-A", status="down", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("fallback_rule", "device_type", "status", parameter_key="P_MISSING")
        # Known behavior: parameter_key not found → fallback returns None for group_key
        # → getattr(item, None) raises TypeError
        with pytest.raises(TypeError):
            executor.execute("fallback_rule", compiled, {"devices": devices}, _make_context())
