import pytest
from src.application.recognition_services.rule_definition_model import RuleDefinition
from src.application.recognition_services.rule_definition_registry import RuleDefinitionRegistry

def test_registry_filters_by_engine_scope():
    registry = RuleDefinitionRegistry()
    
    # 1. Normalization Rule
    norm_rule = RuleDefinition(
        rule_id="N_01",
        name="Norm Rule",
        description="",
        rule_type="field_equals",
        parameters={"target_field": "x", "expected_value": "y"},
        error_message="Err",
        engine_scope="normalization"
    )
    
    # 2. RuleEngine Single Fact Rule
    sf_rule = RuleDefinition(
        rule_id="RE_SF_01",
        name="Single Fact Rule",
        description="",
        rule_type="field_not_equals",
        parameters={"target_field": "status", "expected_value": "Offline"},
        error_message="Err",
        engine_scope="rule_engine_single_fact",
        applies_to=["DeviceFact"]
    )
    
    registry.register_all([norm_rule, sf_rule])
    
    # Verify scope filtering
    norm_rules = registry.get_by_scope("normalization")
    assert len(norm_rules) == 1
    assert norm_rules[0].rule_id == "N_01"
    
    sf_rules = registry.get_by_scope("rule_engine_single_fact")
    assert len(sf_rules) == 1
    assert sf_rules[0].rule_id == "RE_SF_01"
    
    # Verify that 'to_row_constraints' ONLY compiles normalization rules
    constraints = registry.to_row_constraints()
    assert len(constraints) == 1
    assert constraints[0].id == "N_01"

def test_registry_filters_by_applies_to():
    registry = RuleDefinitionRegistry()
    
    device_rule = RuleDefinition(
        rule_id="R_DEV_01",
        name="Device Check",
        description="",
        rule_type="field_equals",
        parameters={},
        error_message="",
        applies_to=["DeviceFact", "PortFact"]
    )
    
    link_rule = RuleDefinition(
        rule_id="R_LNK_01",
        name="Link Check",
        description="",
        rule_type="field_equals",
        parameters={},
        error_message="",
        applies_to=["LinkFact"]
    )
    
    registry.register_all([device_rule, link_rule])
    
    device_rules = registry.get_by_target("DeviceFact")
    assert len(device_rules) == 1
    assert device_rules[0].rule_id == "R_DEV_01"
    
    port_rules = registry.get_by_target("PortFact")
    assert len(port_rules) == 1
    assert port_rules[0].rule_id == "R_DEV_01"
    
    link_rules = registry.get_by_target("LinkFact")
    assert len(link_rules) == 1
    assert link_rules[0].rule_id == "R_LNK_01"
