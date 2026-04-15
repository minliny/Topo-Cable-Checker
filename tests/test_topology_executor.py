"""
P0-1: Topology Executor Unit Tests

Verifies that ALL topology executor subtypes actually execute correctly.
These tests prove the executor is NOT "伪执行" (fake execution).

Covers:
- duplicate_link: detects duplicate links
- missing_peer: detects links referencing missing devices
- topology_assertion/self_loop: detects self-loop links
- topology_assertion/isolated_device: detects devices with no links
- Edge cases: empty datasets, no issues found, unknown assertion_type
"""

import pytest
from src.domain.executors.topology_executor import TopologyExecutor
from src.domain.compiled_rule_schema import CompiledRule, RuleTarget, RuleMessage

from src.domain.fact_model import DeviceFact, LinkFact, NormalizedDataset
from src.domain.result_model import IssueItem


def _make_compiled_rule(rule_id: str, rule_subtype: str, params: dict = None, 
                        target_type: str = "links", severity: str = "high") -> CompiledRule:
    """Helper to create CompiledRule for topology executor tests."""
    extra_params = params or {}
    return CompiledRule(
        rule_id=rule_id,
        rule_type="template",
        executor="topology",
        target=RuleTarget(type=target_type),
        message=RuleMessage(template=f"Rule {rule_id} failed", severity=severity),
        params={"type": rule_subtype, **extra_params}
    )


def _make_context():
    return {}


class TestTopologyExecutorDuplicateLink:
    """duplicate_link subtype: detects two links with same src:src_port->dst:dst_port."""

    def test_detects_duplicate_link(self):
        executor = TopologyExecutor()
        links = [
            LinkFact(src_device="SW1", src_port="Gi0/1", dst_device="SW2", dst_port="Gi0/1", _source_sheet="s1"),
            LinkFact(src_device="SW1", src_port="Gi0/1", dst_device="SW2", dst_port="Gi0/1", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("dup_rule", "duplicate_link")
        result = executor.execute("dup_rule", compiled, {"links": links, "devices": []}, _make_context())

        assert len(result) == 1, f"Expected 1 issue, got {len(result)}"
        assert result[0].category == "duplicate_link"
        assert "SW1:Gi0/1->SW2:Gi0/1" in result[0].message
        assert result[0].severity == "high"

    def test_no_issue_when_all_unique(self):
        executor = TopologyExecutor()
        links = [
            LinkFact(src_device="SW1", src_port="Gi0/1", dst_device="SW2", dst_port="Gi0/1", _source_sheet="s1"),
            LinkFact(src_device="SW2", src_port="Gi0/2", dst_device="SW3", dst_port="Gi0/1", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("dup_rule", "duplicate_link")
        result = executor.execute("dup_rule", compiled, {"links": links, "devices": []}, _make_context())

        assert len(result) == 0, "No issues expected for unique links"

    def test_empty_links_no_crash(self):
        executor = TopologyExecutor()
        compiled = _make_compiled_rule("dup_rule", "duplicate_link")
        result = executor.execute("dup_rule", compiled, {"links": [], "devices": []}, _make_context())
        assert result == []


class TestTopologyExecutorMissingPeer:
    """missing_peer subtype: detects links where src or dst device doesn't exist in device list."""

    def test_detects_missing_source_device(self):
        executor = TopologyExecutor()
        links = [
            LinkFact(src_device="MISSING", src_port="Gi0/1", dst_device="SW2", dst_port="Gi0/1", _source_sheet="s1"),
        ]
        devices = [
            DeviceFact(device_name="SW2", device_type="Switch", status="up", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("peer_rule", "missing_peer")
        result = executor.execute("peer_rule", compiled, {"links": links, "devices": devices}, _make_context())

        assert len(result) == 1
        assert result[0].category == "missing_peer"
        assert "MISSING" in result[0].message

    def test_detects_missing_dest_device(self):
        executor = TopologyExecutor()
        links = [
            LinkFact(src_device="SW1", src_port="Gi0/1", dst_device="GONE", dst_port="Gi0/1", _source_sheet="s1"),
        ]
        devices = [
            DeviceFact(device_name="SW1", device_type="Switch", status="up", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("peer_rule", "missing_peer")
        result = executor.execute("peer_rule", compiled, {"links": links, "devices": devices}, _make_context())

        assert len(result) == 1
        assert "GONE" in result[0].message

    def test_no_issue_when_all_peers_exist(self):
        executor = TopologyExecutor()
        links = [
            LinkFact(src_device="SW1", src_port="Gi0/1", dst_device="SW2", dst_port="Gi0/1", _source_sheet="s1"),
        ]
        devices = [
            DeviceFact(device_name="SW1", device_type="Switch", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW2", device_type="Switch", status="up", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("peer_rule", "missing_peer")
        result = executor.execute("peer_rule", compiled, {"links": links, "devices": devices}, _make_context())

        assert len(result) == 0


class TestTopologyExecutorSelfLoop:
    """topology_assertion/self_loop: detects links where src_device == dst_device."""

    def test_detects_self_loop(self):
        """CRITICAL TEST: This was the broken path due to `rule_def` NameError."""
        executor = TopologyExecutor()
        links = [
            LinkFact(src_device="SW1", src_port="Gi0/1", dst_device="SW1", dst_port="Gi0/1", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("loop_rule", "topology_assertion", 
                                        params={"assertion_type": "self_loop"})
        result = executor.execute("loop_rule", compiled, {"links": links, "devices": []}, _make_context())

        assert len(result) == 1, f"Expected 1 self-loop issue, got {len(result)}"
        assert result[0].category == "topology_assertion"
        assert "Self-loop" in result[0].message
        assert "SW1" in result[0].message
        assert result[0].severity == "high"

    def test_no_issue_when_no_self_loops(self):
        executor = TopologyExecutor()
        links = [
            LinkFact(src_device="SW1", src_port="Gi0/1", dst_device="SW2", dst_port="Gi0/1", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("loop_rule", "topology_assertion",
                                        params={"assertion_type": "self_loop"})
        result = executor.execute("loop_rule", compiled, {"links": links, "devices": []}, _make_context())

        assert len(result) == 0

    def test_multiple_self_loops_detected(self):
        executor = TopologyExecutor()
        links = [
            LinkFact(src_device="SW1", src_port="Gi0/1", dst_device="SW1", dst_port="Gi0/2", _source_sheet="s1"),
            LinkFact(src_device="SW2", src_port="Gi0/1", dst_device="SW2", dst_port="Gi0/1", _source_sheet="s1"),
            LinkFact(src_device="SW1", src_port="Gi0/3", dst_device="SW3", dst_port="Gi0/1", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("loop_rule", "topology_assertion",
                                        params={"assertion_type": "self_loop"})
        result = executor.execute("loop_rule", compiled, {"links": links, "devices": []}, _make_context())

        assert len(result) == 2, f"Expected 2 self-loop issues, got {len(result)}"


class TestTopologyExecutorIsolatedDevice:
    """topology_assertion/isolated_device: detects devices with no links."""

    def test_detects_isolated_device(self):
        """CRITICAL TEST: This was also broken due to `rule_def` NameError."""
        executor = TopologyExecutor()
        links = [
            LinkFact(src_device="SW1", src_port="Gi0/1", dst_device="SW2", dst_port="Gi0/1", _source_sheet="s1"),
        ]
        devices = [
            DeviceFact(device_name="SW1", device_type="Switch", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW2", device_type="Switch", status="up", _source_sheet="s1"),
            DeviceFact(device_name="LONELY", device_type="Router", status="up", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("iso_rule", "topology_assertion",
                                        params={"assertion_type": "isolated_device"},
                                        target_type="devices")
        result = executor.execute("iso_rule", compiled, {"links": links, "devices": devices}, _make_context())

        assert len(result) == 1, f"Expected 1 isolated device issue, got {len(result)}"
        assert result[0].category == "topology_assertion"
        assert "LONELY" in result[0].message
        assert "isolated" in result[0].message.lower()

    def test_no_issue_when_all_connected(self):
        executor = TopologyExecutor()
        links = [
            LinkFact(src_device="SW1", src_port="Gi0/1", dst_device="SW2", dst_port="Gi0/1", _source_sheet="s1"),
        ]
        devices = [
            DeviceFact(device_name="SW1", device_type="Switch", status="up", _source_sheet="s1"),
            DeviceFact(device_name="SW2", device_type="Switch", status="up", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("iso_rule", "topology_assertion",
                                        params={"assertion_type": "isolated_device"},
                                        target_type="devices")
        result = executor.execute("iso_rule", compiled, {"links": links, "devices": devices}, _make_context())

        assert len(result) == 0

    def test_device_with_empty_name_not_flagged(self):
        """Devices with empty/None device_name should be skipped."""
        executor = TopologyExecutor()
        links = []
        devices = [
            DeviceFact(device_name="", device_type="Switch", status="up", _source_sheet="s1"),
        ]
        compiled = _make_compiled_rule("iso_rule", "topology_assertion",
                                        params={"assertion_type": "isolated_device"},
                                        target_type="devices")
        result = executor.execute("iso_rule", compiled, {"links": links, "devices": devices}, _make_context())

        assert len(result) == 0, "Empty device_name should not be flagged as isolated"


class TestTopologyExecutorUnknownSubtype:
    """Unknown subtypes should return empty issues list, not crash."""

    def test_unknown_subtype_returns_empty(self):
        executor = TopologyExecutor()
        compiled = _make_compiled_rule("unknown_rule", "unknown_subtype")
        result = executor.execute("unknown_rule", compiled, {"links": [], "devices": []}, _make_context())
        assert result == []

    def test_unknown_assertion_type_returns_empty(self):
        executor = TopologyExecutor()
        compiled = _make_compiled_rule("unknown_assert", "topology_assertion",
                                        params={"assertion_type": "nonexistent"})
        result = executor.execute("unknown_assert", compiled, {"links": [], "devices": []}, _make_context())
        assert result == []
