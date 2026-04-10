import pytest
from dataclasses import dataclass
from src.domain.compiled_rule_schema import CompiledRule, RuleTarget, RuleMessage
from src.domain.executors.single_fact_executor import SingleFactExecutor
from src.domain.executors.threshold_executor import ThresholdExecutor
from src.domain.executors.group_consistency_executor import GroupConsistencyExecutor
from src.domain.executors.topology_executor import TopologyExecutor
from src.domain.fact_model import DeviceFact, PortFact, LinkFact

def test_executor_contract_compliance():
    # 1. Test SingleFactExecutor
    compiled_rule1 = CompiledRule(
        rule_id="E_01",
        rule_type="field_equals",
        target=RuleTarget(type="devices"),
        executor="single_fact",
        params={"field": "status", "expected": "Online"},
        message=RuleMessage(template="Device is offline", severity="high")
    )
    dataset = {
        "devices": [
            DeviceFact(device_name="D1", device_type=None, status="Online", _source_sheet=""),
            DeviceFact(device_name="D2", device_type=None, status="Offline", _source_sheet=""),
        ]
    }
    
    issues1 = SingleFactExecutor().execute(compiled_rule1, dataset, {})
    assert len(issues1) == 1
    assert issues1[0].evidence["rule_id"] == "E_01"
    assert issues1[0].message == "Device is offline"
    
    # 2. Test ThresholdExecutor
    compiled_rule2 = CompiledRule(
        rule_id="E_02",
        rule_type="threshold",
        target=RuleTarget(type="ports"),
        executor="threshold",
        params={"metric_type": "count", "operator": "lt", "expected_value": 2},
        message=RuleMessage(template="Too many ports", severity="medium")
    )
    dataset2 = {
        "ports": [
            PortFact(device_name="D1", port_name="P1", port_status=None, _source_sheet=""),
            PortFact(device_name="D1", port_name="P2", port_status=None, _source_sheet=""),
        ]
    }
    
    issues2 = ThresholdExecutor().execute(compiled_rule2, dataset2, {})
    assert len(issues2) == 1
    assert issues2[0].evidence["rule_id"] == "E_02"
    assert issues2[0].message == "Too many ports"
    
    # 3. Test GroupConsistencyExecutor
    compiled_rule3 = CompiledRule(
        rule_id="E_03",
        rule_type="group_consistency",
        target=RuleTarget(type="devices"),
        executor="group_consistency",
        params={"group_key": "rack_id", "comparison_field": "device_type"},
        message=RuleMessage(template="Rack inconsistency", severity="high")
    )
    
    @dataclass
    class ExtDeviceFact(DeviceFact):
        rack_id: str = None
        
    dataset3 = {
        "devices": [
            ExtDeviceFact(device_name="D1", device_type="Switch", status=None, _source_sheet="", rack_id="R1"),
            ExtDeviceFact(device_name="D2", device_type="Firewall", status=None, _source_sheet="", rack_id="R1"),
        ]
    }
    
    issues3 = GroupConsistencyExecutor().execute(compiled_rule3, dataset3, {})
    assert len(issues3) == 1 # only one dominant val => one issue
    assert issues3[0].evidence["rule_id"] == "E_03"
    assert issues3[0].message == "Rack inconsistency"
    
    # 4. Test TopologyExecutor
    compiled_rule4 = CompiledRule(
        rule_id="E_04",
        rule_type="topology_assertion",
        target=RuleTarget(type="links"),
        executor="topology",
        params={"assertion_type": "self_loop"},
        message=RuleMessage(template="Self loop found", severity="high")
    )
    dataset4 = {
        "links": [
            LinkFact(src_device="D1", src_port="P1", dst_device="D1", dst_port="P2", _source_sheet="")
        ]
    }
    
    issues4 = TopologyExecutor().execute(compiled_rule4, dataset4, {})
    assert len(issues4) == 1
    assert issues4[0].evidence["rule_id"] == "E_04"
    assert issues4[0].message == "Self loop found"
