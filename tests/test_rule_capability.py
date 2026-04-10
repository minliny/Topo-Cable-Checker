import pytest
from src.domain.rule_compiler import RuleCompiler, RuleCompileError
from src.domain.rule_engine.rule_capability_registry import RuleCapabilityRegistry

def test_rule_capability_registry():
    cap = RuleCapabilityRegistry.infer_capability("threshold", {"metric_type": "count"})
    assert cap is not None
    assert cap.capability_id == "threshold.count_limit"
    
    cap2 = RuleCapabilityRegistry.infer_capability("single_fact", {"type": "field_equals", "field": "status"})
    assert cap2 is not None
    assert cap2.capability_id == "single_fact.equality_check"

def test_capability_inference():
    # Should correctly identify distinct_count as range_check
    cap = RuleCapabilityRegistry.infer_capability("threshold", {"metric_type": "distinct_count", "metric_field": "type"})
    assert cap is not None
    assert cap.capability_id == "threshold.range_check"
    
    # Should identify missing_value as existence_check
    cap2 = RuleCapabilityRegistry.infer_capability("single_fact", {"type": "missing_value", "field": "ip"})
    assert cap2 is not None
    assert cap2.capability_id == "single_fact.existence_check"
    
def test_invalid_capability_rejected():
    # Provide params that don't match any registered capability for threshold
    # The required metric_type is not "count" and not in ["distinct_count", "sum", "average"]
    with pytest.raises(RuleCompileError, match="unknown_rule_capability"):
        RuleCompiler.compile("invalid_cap_rule", {
            "rule_type": "template",
            "template": "threshold_check",
            "target_type": "devices",
            "params": {"metric_type": "unknown_metric"}
        })
