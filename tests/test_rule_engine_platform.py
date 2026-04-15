import pytest
from src.domain.rule_compiler import RuleCompiler, RuleCompileError
from src.domain.compiled_rule_schema import CompiledRule, RuleValidationError, RuleTarget, RuleMessage
from src.domain.rule_engine.parameter_schema_registry import ParameterSchemaRegistry
from src.domain.rule_engine.rule_meta_registry import RuleMetaRegistry, RuleMeta
from src.domain.rule_engine.rule_capability_registry import RuleCapabilityRegistry, RuleCapability
from src.domain.rule_engine.engine import RuleEngine
from src.domain.baseline_model import BaselineProfile
from src.domain.fact_model import NormalizedDataset

def test_compiled_rule_validation():
    # 1. Valid rule
    rule = CompiledRule(
        rule_id="r1",
        rule_type="dsl",
        executor="single_fact",
        target=RuleTarget(type="devices", filter={"device_type": "Switch"}),
        message=RuleMessage(template="Error occurred", severity="medium")
    )
    rule.validate()  # Should not raise
    
    # 2. Missing rule_id
    with pytest.raises(RuleValidationError, match="rule_id is required"):
        rule_invalid = CompiledRule(
            rule_id="", rule_type="dsl", executor="single_fact",
            target=RuleTarget(type="devices"), message=RuleMessage(template="Error", severity="medium")
        )
        rule_invalid.validate()
        
    # 3. Invalid executor type
    with pytest.raises(RuleValidationError, match="Invalid executor: unknown"):
        rule_invalid = CompiledRule(
            rule_id="r1", rule_type="dsl", executor="unknown",
            target=RuleTarget(type="devices"), message=RuleMessage(template="Error", severity="medium")
        )
        rule_invalid.validate()

    # 4. Invalid target type
    with pytest.raises(RuleValidationError, match="Invalid target type: people"):
        rule_invalid = CompiledRule(
            rule_id="r1", rule_type="dsl", executor="single_fact",
            target=RuleTarget(type="people"), message=RuleMessage(template="Error", severity="medium")
        )
        rule_invalid.validate()
        
    # 5. Invalid target.filter (not dict)
    with pytest.raises(RuleValidationError, match="target.filter must be a dict"):
        rule_invalid = CompiledRule(
            rule_id="r1", rule_type="dsl", executor="single_fact",
            target=RuleTarget(type="devices", filter=lambda x: x), message=RuleMessage(template="Error", severity="medium")
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

def test_rule_meta_registry():
    # Check threshold meta
    threshold_meta = RuleMetaRegistry.get_meta("threshold")
    assert threshold_meta is not None
    assert threshold_meta.category == "quantitative"
    assert threshold_meta.supports_grouping is True

    # Check topology meta
    topology_meta = RuleMetaRegistry.get_meta("topology")
    assert topology_meta is not None
    assert topology_meta.category == "topology"
    assert topology_meta.supports_topology is True
    
def test_rule_type_validation():
    # Unregistered meta throws an error in compiler
    with pytest.raises(RuleCompileError, match="unknown_rule_meta"):
        # Force a template that produces an unknown executor
        # We need to temporarily add a bad template
        from src.domain.rule_compiler import TemplateRegistry
        TemplateRegistry._templates["bad_template"] = {
            "target_executor": "unknown_executor",
            "supported_params": [],
            "validation_rules": []
        }
        
        RuleCompiler.compile("r1", {
            "rule_type": "template",
            "template": "bad_template",
            "target_type": "devices",
            "params": {}
        })
        
        # Cleanup
        del TemplateRegistry._templates["bad_template"]

def test_meta_and_schema_consistency():
    # All schemas in ParameterSchemaRegistry should have a corresponding RuleMeta
    for rule_type in ParameterSchemaRegistry._schemas:
        meta = RuleMetaRegistry.get_meta(rule_type)
        assert meta is not None, f"No RuleMeta found for rule_type: {rule_type}"
        
    # Registering a schema for an unknown rule_type should fail
    with pytest.raises(ValueError, match="Cannot register schema for unknown rule_type"):
        ParameterSchemaRegistry.register("fake_rule", required=[], optional=[])
