import pytest

from src.application.recognition_services.rule_definition_registry import RuleDefinitionRegistry
from src.application.recognition_services.rule_definition_model import RuleDefinition
from src.domain.fact_model import NormalizedDataset, DeviceFact
from src.domain.baseline_model import BaselineProfile
from src.domain.rule_engine import RuleEngine


def test_single_fact_external_rules_from_registry_produce_issues():
    registry = RuleDefinitionRegistry()
    registry.register(
        RuleDefinition(
            rule_id="RE_SF_EXT_01",
            name="Device Must Be Online",
            description="All devices must have status Online",
            rule_type="field_equals",
            parameters={"target_field": "status", "expected_value": "Online"},
            error_message="Device status must be Online",
            severity="high",
            enabled=True,
            group="availability",
            engine_scope="rule_engine_single_fact",
            applies_to=["DeviceFact"],
        )
    )

    from src.application.rule_engine_services.single_fact_rule_compiler import (
        SingleFactRuleCompiler,
    )

    external_rules = SingleFactRuleCompiler.compile_registry(registry)

    dataset = NormalizedDataset(
        devices=[
            DeviceFact(device_name="R1", device_type="Router", status="Online", _source_sheet="dev"),
            DeviceFact(device_name="R2", device_type="Router", status="Offline", _source_sheet="dev"),
        ],
        ports=[],
        links=[],
    )

    baseline = BaselineProfile(
        baseline_id="B1",
        baseline_version="1",
        recognition_profile={},
        naming_profile={},
        rule_set={},
        parameter_profile={},
        threshold_profile={},
        baseline_version_snapshot={},
    )

    engine = RuleEngine()
    issues = engine.execute(dataset, baseline, external_compiled_rules=external_rules)

    assert len(issues) == 1
    assert issues[0].category == "single_fact"
    assert issues[0].evidence["rule_id"] == "RE_SF_EXT_01"


def test_single_fact_external_rule_rejects_unsupported_rule_type():
    registry = RuleDefinitionRegistry()
    registry.register(
        RuleDefinition(
            rule_id="RE_SF_EXT_BAD",
            name="Bad",
            description="",
            rule_type="unsupported_magic",
            parameters={},
            error_message="",
            engine_scope="rule_engine_single_fact",
            applies_to=["DeviceFact"],
        )
    )

    from src.application.rule_engine_services.single_fact_rule_compiler import (
        SingleFactRuleCompiler,
    )

    with pytest.raises(ValueError, match="Unsupported rule_type"):
        SingleFactRuleCompiler.compile_registry(registry)

