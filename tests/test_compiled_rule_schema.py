import pytest
from src.domain.compiled_rule_schema import CompiledRule, RuleTarget, RuleMessage
from src.domain.rule_compiler import RuleCompiler, RuleCompileError
from src.application.rule_engine_services.single_fact_rule_compiler import SingleFactRuleCompiler
from src.application.rule_engine_services.threshold_rule_compiler import ThresholdRuleCompiler
from src.application.recognition_services.rule_definition_model import RuleDefinition

def test_compiled_rule_schema_consistency():
    # 1. Test Domain RuleCompiler (baseline rule)
    baseline_rule_def = {
        "rule_type": "dsl",
        "target_type": "devices",
        "expression": {
            "assert": "status == \"Online\""
        },
        "severity": "high",
        "message_template": "Device must be online."
    }
    
    compiled1 = RuleCompiler.compile("B_01", baseline_rule_def)
    assert isinstance(compiled1, CompiledRule)
    assert compiled1.rule_id == "B_01"
    assert compiled1.rule_type == "field_equals"
    assert compiled1.target.type == "devices"
    assert compiled1.executor == "single_fact"
    assert compiled1.params == {"field": "status", "expected": "Online"}
    assert compiled1.message.template == "Device must be online."
    assert compiled1.message.severity == "high"

    # 2. Test Application SingleFactRuleCompiler
    app_rule_def1 = RuleDefinition(
        rule_id="A_01",
        name="Test",
        description="",
        rule_type="field_not_equals",
        parameters={"target_field": "status", "expected_value": "Offline"},
        error_message="Cannot be offline.",
        severity="critical",
        engine_scope="rule_engine_single_fact",
        applies_to=["DeviceFact"]
    )
    
    compiled2 = SingleFactRuleCompiler.compile(app_rule_def1)
    assert isinstance(compiled2, CompiledRule)
    assert compiled2.rule_id == "A_01"
    assert compiled2.rule_type == "field_not_equals"
    assert compiled2.target.type == "devices"
    assert compiled2.executor == "single_fact"
    assert compiled2.params == {"field": "status", "expected": "Offline"}
    assert compiled2.message.template == "Cannot be offline."
    assert compiled2.message.severity == "critical"

    # 3. Test Application ThresholdRuleCompiler
    app_rule_def2 = RuleDefinition(
        rule_id="A_02",
        name="Test",
        description="",
        rule_type="threshold",
        parameters={"metric_type": "count", "operator": "lt", "expected_value": 5},
        error_message="Too many.",
        severity="low",
        engine_scope="rule_engine_threshold",
        applies_to=["LinkFact"]
    )
    
    compiled3 = ThresholdRuleCompiler.compile(app_rule_def2)
    assert isinstance(compiled3, CompiledRule)
    assert compiled3.rule_id == "A_02"
    assert compiled3.rule_type == "threshold"
    assert compiled3.target.type == "links"
    assert compiled3.executor == "threshold"
    assert compiled3.params == {"metric_type": "count", "operator": "lt", "expected_value": 5}
    assert compiled3.message.template == "Too many."
    assert compiled3.message.severity == "low"
