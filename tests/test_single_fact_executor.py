"""
A2-2: Single Fact Executor Unit Tests

Verifies that ALL single_fact executor subtypes execute correctly.
These tests prove the single_fact executor is NOT "伪执行" (fake execution).

Covers:
- field_equals: matches / doesn't match expected value
- regex_match: matches / doesn't match regex pattern
- missing_value: field is missing (None or empty) / field exists

Also covers:
- Edge cases: empty datasets, None attribute values
- Severity propagation
- Category is always "single_fact"
"""

import pytest
from src.domain.executors.single_fact_executor import SingleFactExecutor
from src.domain.compiled_rule_schema import CompiledRule, RuleTarget, RuleMessage

from src.domain.fact_model import DeviceFact, PortFact
from src.domain.result_model import IssueItem


def _make_compiled_rule(rule_id: str, subtype: str, field: str,
                        expected: str = None, target_type: str = "devices",
                        severity: str = "warning") -> CompiledRule:
    """Helper to create CompiledRule for single_fact executor tests."""
    params = {"type": subtype, "field": field}
    if expected is not None:
        params["expected"] = expected

    return CompiledRule(
        rule_id=rule_id,
        rule_type="template",
        executor="single_fact",
        target=RuleTarget(type=target_type),
        message=RuleMessage(template=f"Rule {rule_id} single_fact check", severity=severity),
        params=params,
    )


def _make_context(runtime_flags=None):
    return {"runtime_flags": runtime_flags or {}}


# ==========================================
# field_equals Tests
# ==========================================

class TestFieldEquals:
    """field_equals subtype: checks if field value equals expected value."""

    def test_no_issue_when_values_match(self):
        executor = SingleFactExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Switch", status="up", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("eq_rule", "field_equals", "device_type", expected="Switch")
        result = executor.execute("eq_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 0

    def test_issue_when_values_differ(self):
        executor = SingleFactExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Switch", status="down", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("eq_rule", "field_equals", "status", expected="up")
        result = executor.execute("eq_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1
        assert result[0].category == "single_fact"
        assert result[0].actual == "down"
        assert result[0].expected == "up"

    def test_multiple_mismatches_reported(self):
        executor = SingleFactExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Switch", status="down", _source_sheet="s1"),
            DeviceFact(device_name="SW2", device_type="Switch", status="down", _source_sheet="s1"),
            DeviceFact(device_name="SW3", device_type="Switch", status="up", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("eq_rule", "field_equals", "status", expected="up")
        result = executor.execute("eq_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 2

    def test_field_equals_on_port_facts(self):
        executor = SingleFactExecutor()
        ports = [
            PortFact(device_name="SW1", port_name="Gi0/1", port_status="up", _source_sheet="s1"),
            PortFact(device_name="SW1", port_name="Gi0/2", port_status="down", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("port_rule", "field_equals", "port_status", 
                                       expected="up", target_type="ports")
        result = executor.execute("port_rule", compiled, {"ports": ports}, _make_context())
        assert len(result) == 1
        assert "Gi0/2" in str(result[0].evidence)

    def test_none_expected_vs_none_actual(self):
        """If both expected and actual are None, it should NOT be a mismatch."""
        executor = SingleFactExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type=None, status="up", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("none_rule", "field_equals", "device_type", expected=None)
        result = executor.execute("none_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 0


# ==========================================
# regex_match Tests
# ==========================================

class TestRegexMatch:
    """regex_match subtype: checks if field value matches regex pattern."""

    def test_no_issue_when_regex_matches(self):
        executor = SingleFactExecutor()
        devices = [
            DeviceFact(device_name="SW-001", device_type="Switch", status="up", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("regex_rule", "regex_match", "device_name", expected=r"SW-\d+")
        result = executor.execute("regex_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 0

    def test_issue_when_regex_fails(self):
        executor = SingleFactExecutor()
        devices = [
            DeviceFact(device_name="INVALID", device_type="Switch", status="up", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("regex_rule", "regex_match", "device_name", expected=r"SW-\d+")
        result = executor.execute("regex_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1
        assert result[0].category == "single_fact"
        assert "INVALID" in result[0].message

    def test_regex_match_none_value_fails(self):
        """If the field value is None, regex should fail."""
        executor = SingleFactExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type=None, status="up", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("regex_rule", "regex_match", "device_type", expected=r"Switch")
        result = executor.execute("regex_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1

    def test_regex_partial_match(self):
        """re.match matches from the beginning of the string."""
        executor = SingleFactExecutor()
        devices = [
            DeviceFact(device_name="prefix-SW1", device_type="Switch", status="up", _source_sheet="s1"),
        ]
        # re.match only matches at the start of the string
        compiled = _make_compiled_rule("regex_rule", "regex_match", "device_name", expected=r"SW\d+")
        result = executor.execute("regex_rule", compiled, {"devices": devices}, _make_context())
        # "prefix-SW1" does not start with "SW", so re.match fails
        assert len(result) == 1

    def test_regex_multiple_failures(self):
        executor = SingleFactExecutor()
        devices = [
            DeviceFact(device_name="SW-001", device_type="Switch", status="up", _source_sheet="s1"),
            DeviceFact(device_name="BAD", device_type="Switch", status="up", _source_sheet="s1"),
            DeviceFact(device_name="WRONG", device_type="Switch", status="up", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("regex_rule", "regex_match", "device_name", expected=r"SW-\d+")
        result = executor.execute("regex_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 2


# ==========================================
# missing_value Tests
# ==========================================

class TestMissingValue:
    """missing_value subtype: checks if field is None or empty string."""

    def test_no_issue_when_value_exists(self):
        executor = SingleFactExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Switch", status="up", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("missing_rule", "missing_value", "device_type")
        result = executor.execute("missing_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 0

    def test_issue_when_value_is_none(self):
        executor = SingleFactExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type=None, status="up", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("missing_rule", "missing_value", "device_type")
        result = executor.execute("missing_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1
        assert result[0].category == "single_fact"
        assert "missing" in result[0].message.lower() or "empty" in result[0].message.lower()

    def test_issue_when_value_is_empty_string(self):
        executor = SingleFactExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="", status="up", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("missing_rule", "missing_value", "device_type")
        result = executor.execute("missing_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1

    def test_issue_when_value_is_whitespace_only(self):
        executor = SingleFactExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="   ", status="up", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("missing_rule", "missing_value", "device_type")
        result = executor.execute("missing_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1

    def test_multiple_missing_values(self):
        executor = SingleFactExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Switch", status=None, _source_sheet="s1"),
            DeviceFact(device_name="SW2", device_type=None, status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW3", device_type="Router", status="down", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("missing_rule", "missing_value", "device_type")
        result = executor.execute("missing_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1  # Only SW2 has missing device_type


# ==========================================
# Edge Cases
# ==========================================

class TestSingleFactEdgeCases:
    """Edge cases for single_fact executor."""

    def test_empty_dataset_returns_no_issues(self):
        executor = SingleFactExecutor()
        compiled = _make_compiled_rule("empty_rule", "field_equals", "status", expected="up")
        result = executor.execute("empty_rule", compiled, {"devices": []}, _make_context())
        assert result == []

    def test_severity_propagated_to_issue(self):
        executor = SingleFactExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Switch", status="down", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("sev_rule", "field_equals", "status", expected="up", severity="critical")
        result = executor.execute("sev_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1
        assert result[0].severity == "critical"

    def test_evidence_contains_item_data(self):
        executor = SingleFactExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Switch", status="down", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("evidence_rule", "field_equals", "status", expected="up")
        result = executor.execute("evidence_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1
        assert "item_data" in result[0].evidence
        assert result[0].evidence["item_data"]["device_name"] == "SW1"

    def test_nonexistent_field_returns_none_value(self):
        """If the field doesn't exist on the fact, getattr returns None."""
        executor = SingleFactExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Switch", status="up", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("missing_field_rule", "missing_value", "nonexistent_field")
        result = executor.execute("missing_field_rule", compiled, {"devices": devices}, _make_context())
        assert len(result) == 1  # nonexistent field → None → missing

    def test_details_contains_target_type(self):
        executor = SingleFactExecutor()
        devices = [
            DeviceFact(device_name="SW1", device_type="Switch", status="down", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("detail_rule", "field_equals", "status", expected="up")
        result = executor.execute("detail_rule", compiled, {"devices": devices}, _make_context())
        assert result[0].details["target_type"] == "devices"
