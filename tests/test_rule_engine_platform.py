import pytest
from src.domain.rule_compiler import RuleCompiler, RuleCompileError
from src.domain.rule_engine.compiled_rule import CompiledRule, RuleValidationError
from src.domain.rule_engine.parameter_schema_registry import ParameterSchemaRegistry
from src.domain.rule_engine.engine import RuleEngine
from src.domain.baseline_model import BaselineProfile
from src.domain.fact_model import NormalizedDataset

def test_compiled_rule_validation():
    # 1. Valid rule
    rule = CompiledRule(
        rule_id="r1",
        rule_type="dsl",
        executor={"type": "single_fact"},
        target={"type": "devices", "filter": {"device_type": "Switch"}},
        message={"template": "Error occurred"}
    )
    rule.validate()  # Should not raise
    
    # 2. Missing rule_id
    with pytest.raises(RuleValidationError, match="rule_id is required"):
        rule_invalid = CompiledRule(
            rule_id="", rule_type="dsl", executor={"type": "single_fact"},
            target={"type": "devices"}, message={"template": "Error"}
        )
        rule_invalid.validate()
        
    # 3. Invalid executor type
    with pytest.raises(RuleValidationError, match="Invalid executor.type: unknown"):
        rule_invalid = CompiledRule(
            rule_id="r1", rule_type="dsl", executor={"type": "unknown"},
            target={"type": "devices"}, message={"template": "Error"}
        )
        rule_invalid.validate()

    # 4. Invalid target type
    with pytest.raises(RuleValidationError, match="Invalid target.type: people"):
        rule_invalid = CompiledRule(
            rule_id="r1", rule_type="dsl", executor={"type": "single_fact"},
            target={"type": "people"}, message={"template": "Error"}
        )
        rule_invalid.validate()
        
    # 5. Invalid target.filter (function)
    with pytest.raises(RuleValidationError, match="target.filter cannot be a function"):
        rule_invalid = CompiledRule(
            rule_id="r1", rule_type="dsl", executor={"type": "single_fact"},
            target={"type": "devices", "filter": lambda x: x}, message={"template": "Error"}
        )
        rule_invalid.validate()

def test_parameter_schema_validation():
    # Valid threshold params
    assert ParameterSchemaRegistry.validate("threshold", {"metric_type": "count"}) is None
    
    # Missing required param
    err = ParameterSchemaRegistry.validate("threshold", {"operator": "gt"})
    assert err == "Missing required parameter: metric_type"
    
    # Valid single_fact params
    assert ParameterSchemaRegistry.validate("single_fact", {"field": "status", "type": "field_equals"}) is None
    
    # Missing required param for single_fact
    err = ParameterSchemaRegistry.validate("single_fact", {"field": "status"})
    assert err == "Missing required parameter: type"

def test_invalid_rule_rejected():
    engine = RuleEngine()
    dataset = NormalizedDataset(devices=[], ports=[], links=[])
    
    # We will pass an invalid rule def that gets compiled but fails schema validation
    # Actually, schema validation happens in RuleCompiler now, so let's test RuleCompiler
    
    baseline = BaselineProfile(
        baseline_id="b1",
        baseline_version="v1",
        recognition_profile={},
        naming_profile={},
        baseline_version_snapshot={},
        rule_set={
            "invalid_rule": {
                "rule_type": "template",
                "template": "threshold_check",
                "target_type": "devices",
                # missing metric_type which is required by threshold_check schema
                "params": {} 
            }
        },
        parameter_profile={},
        threshold_profile={}
    )
    
    # The rule will fail compilation due to ParameterSchemaRegistry in RuleCompiler
    # The execute loop should catch this and skip the rule, returning no issues
    issues = engine.execute(dataset, baseline)
    assert len(issues) == 0

    # Let's directly verify RuleCompiler throws RuleCompileError for invalid schema
    with pytest.raises(RuleCompileError, match="missing_required_param"):
        RuleCompiler.compile("invalid_rule", {
            "rule_type": "template",
            "template": "threshold_check",
            "target_type": "devices",
            "params": {}
        })
