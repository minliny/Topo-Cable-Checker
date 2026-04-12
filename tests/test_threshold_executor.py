"""
A2-1: Threshold Executor Unit Tests

Verifies that ALL threshold executor operators execute correctly.
These tests prove the threshold executor is NOT "伪执行" (fake execution).

Covers:
- gt (greater than)
- gte (greater than or equal)
- lt (less than)
- lte (less than or equal)
- between (inclusive range)
- outside (outside range)
- eq (equals)

Also covers:
- metric_type: count vs distinct_count
- threshold_profile vs inline params
- Edge cases: empty datasets, zero values
"""

import pytest
from src.domain.executors.threshold_executor import ThresholdExecutor
from src.domain.rule_engine.compiled_rule import CompiledRule
from src.domain.rule_engine.execution_context import ExecutionContext
from src.domain.fact_model import DeviceFact
from src.domain.result_model import IssueItem


def _make_compiled_rule(rule_id: str, operator: str, expected_value=None,
                        min_value=None, max_value=None,
                        metric_type: str = "count", metric_field: str = None,
                        threshold_key: str = None,
                        target_type: str = "devices", severity: str = "warning") -> CompiledRule:
    """Helper to create CompiledRule for threshold executor tests."""
    params = {"metric_type": metric_type, "operator": operator}
    if metric_field:
        params["metric_field"] = metric_field
    if threshold_key:
        params["threshold_key"] = threshold_key
    if expected_value is not None:
        params["expected_value"] = expected_value
    if min_value is not None:
        params["min_value"] = min_value
    if max_value is not None:
        params["max_value"] = max_value

    return CompiledRule(
        rule_id=rule_id,
        rule_type="template",
        executor={"type": "threshold"},
        target={"type": target_type, "filter": None},
        message={"template": f"Rule {rule_id} threshold check"},
        severity=severity,
        params=params,
        operator=operator,
        metric_type=metric_type,
        **({"expected_value": expected_value} if expected_value is not None else {}),
        **({"min_value": min_value} if min_value is not None else {}),
        **({"max_value": max_value} if max_value is not None else {}),
        **({"metric_field": metric_field} if metric_field else {}),
        **({"threshold_key": threshold_key} if threshold_key else {}),
    )


def _make_context(threshold_profile=None, parameter_profile=None) -> ExecutionContext:
    return ExecutionContext(
        parameter_profile=parameter_profile or {},
        threshold_profile=threshold_profile or {},
        runtime_flags={},
    )


def _make_devices(count: int, device_type: str = "Switch") -> list:
    """Create N DeviceFact objects for testing."""
    return [
        DeviceFact(device_name=f"SW{i+1}", device_type=device_type, status="up", _source_sheet="s1")
        for i in range(count)
    ]


# ==========================================
# Operator Tests
# ==========================================

class TestThresholdGt:
    """gt operator: actual > expected_value"""

    def test_gt_fails_when_equal(self):
        executor = ThresholdExecutor()
        devices = _make_devices(5)
        compiled = _make_compiled_rule("gt_rule", "gt", expected_value=5)
        result = executor.execute("gt_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1
        assert result[0].category == "threshold_check"
        assert result[0].severity == "warning"

    def test_gt_fails_when_below(self):
        executor = ThresholdExecutor()
        devices = _make_devices(3)
        compiled = _make_compiled_rule("gt_rule", "gt", expected_value=5)
        result = executor.execute("gt_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1

    def test_gt_passes_when_above(self):
        executor = ThresholdExecutor()
        devices = _make_devices(10)
        compiled = _make_compiled_rule("gt_rule", "gt", expected_value=5)
        result = executor.execute("gt_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 0

    def test_gt_evidence_contains_actual_value(self):
        executor = ThresholdExecutor()
        devices = _make_devices(3)
        compiled = _make_compiled_rule("gt_rule", "gt", expected_value=5)
        result = executor.execute("gt_rule", compiled, {"devices": devices}, _make_context())
        assert result[0].evidence["actual_value"] == 3
        assert result[0].actual == 3


class TestThresholdGte:
    """gte operator: actual >= expected_value"""

    def test_gte_passes_when_equal(self):
        executor = ThresholdExecutor()
        devices = _make_devices(5)
        compiled = _make_compiled_rule("gte_rule", "gte", expected_value=5)
        result = executor.execute("gte_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 0

    def test_gte_passes_when_above(self):
        executor = ThresholdExecutor()
        devices = _make_devices(10)
        compiled = _make_compiled_rule("gte_rule", "gte", expected_value=5)
        result = executor.execute("gte_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 0

    def test_gte_fails_when_below(self):
        executor = ThresholdExecutor()
        devices = _make_devices(3)
        compiled = _make_compiled_rule("gte_rule", "gte", expected_value=5)
        result = executor.execute("gte_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1


class TestThresholdLt:
    """lt operator: actual < expected_value"""

    def test_lt_passes_when_below(self):
        executor = ThresholdExecutor()
        devices = _make_devices(3)
        compiled = _make_compiled_rule("lt_rule", "lt", expected_value=5)
        result = executor.execute("lt_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 0

    def test_lt_fails_when_equal(self):
        executor = ThresholdExecutor()
        devices = _make_devices(5)
        compiled = _make_compiled_rule("lt_rule", "lt", expected_value=5)
        result = executor.execute("lt_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1

    def test_lt_fails_when_above(self):
        executor = ThresholdExecutor()
        devices = _make_devices(10)
        compiled = _make_compiled_rule("lt_rule", "lt", expected_value=5)
        result = executor.execute("lt_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1


class TestThresholdLte:
    """lte operator: actual <= expected_value"""

    def test_lte_passes_when_equal(self):
        executor = ThresholdExecutor()
        devices = _make_devices(5)
        compiled = _make_compiled_rule("lte_rule", "lte", expected_value=5)
        result = executor.execute("lte_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 0

    def test_lte_passes_when_below(self):
        executor = ThresholdExecutor()
        devices = _make_devices(3)
        compiled = _make_compiled_rule("lte_rule", "lte", expected_value=5)
        result = executor.execute("lte_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 0

    def test_lte_fails_when_above(self):
        executor = ThresholdExecutor()
        devices = _make_devices(10)
        compiled = _make_compiled_rule("lte_rule", "lte", expected_value=5)
        result = executor.execute("lte_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1


class TestThresholdBetween:
    """between operator: min_value <= actual <= max_value"""

    def test_between_passes_when_in_range(self):
        executor = ThresholdExecutor()
        devices = _make_devices(5)
        compiled = _make_compiled_rule("between_rule", "between", min_value=3, max_value=10)
        result = executor.execute("between_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 0

    def test_between_passes_at_lower_bound(self):
        executor = ThresholdExecutor()
        devices = _make_devices(3)
        compiled = _make_compiled_rule("between_rule", "between", min_value=3, max_value=10)
        result = executor.execute("between_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 0

    def test_between_passes_at_upper_bound(self):
        executor = ThresholdExecutor()
        devices = _make_devices(10)
        compiled = _make_compiled_rule("between_rule", "between", min_value=3, max_value=10)
        result = executor.execute("between_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 0

    def test_between_fails_when_below(self):
        executor = ThresholdExecutor()
        devices = _make_devices(2)
        compiled = _make_compiled_rule("between_rule", "between", min_value=3, max_value=10)
        result = executor.execute("between_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1

    def test_between_fails_when_above(self):
        executor = ThresholdExecutor()
        devices = _make_devices(15)
        compiled = _make_compiled_rule("between_rule", "between", min_value=3, max_value=10)
        result = executor.execute("between_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1


class TestThresholdOutside:
    """outside operator: actual NOT in [min_value, max_value]"""

    def test_outside_passes_when_below_range(self):
        executor = ThresholdExecutor()
        devices = _make_devices(2)
        compiled = _make_compiled_rule("outside_rule", "outside", min_value=5, max_value=10)
        result = executor.execute("outside_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 0

    def test_outside_passes_when_above_range(self):
        executor = ThresholdExecutor()
        devices = _make_devices(15)
        compiled = _make_compiled_rule("outside_rule", "outside", min_value=5, max_value=10)
        result = executor.execute("outside_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 0

    def test_outside_fails_when_in_range(self):
        executor = ThresholdExecutor()
        devices = _make_devices(7)
        compiled = _make_compiled_rule("outside_rule", "outside", min_value=5, max_value=10)
        result = executor.execute("outside_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1

    def test_outside_fails_at_lower_bound(self):
        executor = ThresholdExecutor()
        devices = _make_devices(5)
        compiled = _make_compiled_rule("outside_rule", "outside", min_value=5, max_value=10)
        result = executor.execute("outside_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1

    def test_outside_fails_at_upper_bound(self):
        executor = ThresholdExecutor()
        devices = _make_devices(10)
        compiled = _make_compiled_rule("outside_rule", "outside", min_value=5, max_value=10)
        result = executor.execute("outside_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1


class TestThresholdEq:
    """eq operator (default): actual == expected_value"""

    def test_eq_passes_when_equal(self):
        executor = ThresholdExecutor()
        devices = _make_devices(5)
        compiled = _make_compiled_rule("eq_rule", "eq", expected_value=5)
        result = executor.execute("eq_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 0

    def test_eq_fails_when_not_equal(self):
        executor = ThresholdExecutor()
        devices = _make_devices(3)
        compiled = _make_compiled_rule("eq_rule", "eq", expected_value=5)
        result = executor.execute("eq_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1

    def test_eq_default_operator(self):
        """When no operator is specified, default is 'eq'."""
        executor = ThresholdExecutor()
        devices = _make_devices(5)
        # Create rule without explicit operator — defaults to eq
        compiled = CompiledRule(
            rule_id="default_eq_rule",
            rule_type="template",
            executor={"type": "threshold"},
            target={"type": "devices", "filter": None},
            message={"template": "Default eq test"},
            severity="warning",
            params={"metric_type": "count", "expected_value": 5},
            expected_value=5,
        )
        result = executor.execute("default_eq_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 0


# ==========================================
# Metric Type Tests
# ==========================================

class TestThresholdDistinctCount:
    """distinct_count metric: counts unique values of a field."""

    def test_distinct_count_gt(self):
        executor = ThresholdExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Switch", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW2", device_type="Switch", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW3", device_type="Router", status="up", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule(
            "distinct_rule", "gt", expected_value=1,
            metric_type="distinct_count", metric_field="device_type"
        )
        result = executor.execute("distinct_rule", compiled, {"devices": devices}, _make_context())
        # 2 distinct types (Switch, Router) > 1 → passes (no issue)
        assert len(result) == 0

    def test_distinct_count_fails_when_below(self):
        executor = ThresholdExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Switch", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW2", device_type="Switch", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW3", device_type="Switch", status="up", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule(
            "distinct_rule", "gt", expected_value=1,
            metric_type="distinct_count", metric_field="device_type"
        )
        result = executor.execute("distinct_rule", compiled, {"devices": devices}, _make_context())
        # 1 distinct type, which is NOT > 1
        assert len(result) == 1


# ==========================================
# Threshold Profile vs Inline Params
# ==========================================

class TestThresholdProfile:
    """Threshold values from threshold_profile (context) vs inline params."""

    def test_uses_threshold_profile_when_key_exists(self):
        executor = ThresholdExecutor()
        devices = _make_devices(3)
        ctx = _make_context(threshold_profile={
            "T1": {"operator": "gt", "expected_value": 2}
        })
        compiled = _make_compiled_rule(
            "profile_rule", "eq", expected_value=999,  # inline values should be overridden
            threshold_key="T1"
        )
        result = executor.execute("profile_rule", compiled, {"devices": devices}, ctx)
        # With threshold_profile: gt 2, actual=3 → passes (no issue)
        assert len(result) == 0

    def test_uses_inline_when_no_threshold_key(self):
        executor = ThresholdExecutor()
        devices = _make_devices(3)
        compiled = _make_compiled_rule("inline_rule", "gt", expected_value=5)
        result = executor.execute("inline_rule", compiled, {"devices": devices}, _make_context())
        # inline: gt 5, actual=3 → fails
        assert len(result) == 1

    def test_evidence_shows_threshold_source(self):
        executor = ThresholdExecutor()
        devices = _make_devices(3)
        ctx = _make_context(threshold_profile={
            "T1": {"operator": "gt", "expected_value": 10}
        })
        compiled = _make_compiled_rule(
            "source_rule", "eq", expected_value=5,
            threshold_key="T1"
        )
        result = executor.execute("source_rule", compiled, {"devices": devices}, ctx)
        assert len(result) == 1
        assert result[0].evidence["threshold_source"] == "threshold_profile"


# ==========================================
# Edge Cases
# ==========================================

class TestThresholdEdgeCases:
    """Edge cases for threshold executor."""

    def test_empty_dataset_count_is_zero(self):
        executor = ThresholdExecutor()
        compiled = _make_compiled_rule("empty_rule", "gt", expected_value=0)
        result = executor.execute("empty_rule", compiled, {"devices": []}, _make_context())
        # 0 is NOT > 0, so this should fail
        assert len(result) == 1
        assert result[0].actual == 0

    def test_zero_expected_value(self):
        executor = ThresholdExecutor()
        devices = _make_devices(3)
        compiled = _make_compiled_rule("zero_rule", "eq", expected_value=0)
        result = executor.execute("zero_rule", compiled, {"devices": devices}, _make_context())
        # 3 != 0, so eq fails
        assert len(result) == 1

    def test_severity_propagated_to_issue(self):
        executor = ThresholdExecutor()
        devices = _make_devices(3)
        compiled = _make_compiled_rule("sev_rule", "gt", expected_value=5, severity="error")
        result = executor.execute("sev_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1
        assert result[0].severity == "error"

    def test_message_contains_rule_id(self):
        executor = ThresholdExecutor()
        devices = _make_devices(3)
        compiled = _make_compiled_rule("msg_test_rule", "gt", expected_value=5)
        result = executor.execute("msg_test_rule", compiled, {"devices": devices}, _make_context())
        assert "msg_test_rule" in result[0].message
