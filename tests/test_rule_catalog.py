import pytest
from src.domain.rule_engine.rule_catalog import RuleCatalogService, RuleCatalogError
from src.domain.rule_engine.rule_meta_registry import RuleMetaRegistry, RuleMeta
from src.domain.rule_engine.parameter_schema_registry import ParameterSchemaRegistry
from src.domain.rule_engine.rule_capability_registry import RuleCapabilityRegistry

def test_rule_catalog_descriptor_build():
    # It should successfully build the catalog from existing registries
    descriptors = RuleCatalogService.list_rule_descriptors()
    assert len(descriptors) > 0
    
    threshold_desc = RuleCatalogService.get_rule_descriptor("threshold")
    assert threshold_desc is not None
    assert threshold_desc.rule_type == "threshold"
    assert threshold_desc.display_name == "Threshold"
    assert threshold_desc.rule_meta.category == "quantitative"
    assert "metric_type" in threshold_desc.parameter_schema["required"]
    assert len(threshold_desc.capabilities) > 0
    assert len(threshold_desc.supported_targets) > 0
    assert len(threshold_desc.default_examples) > 0

def test_rule_catalog_lookup():
    types = RuleCatalogService.list_supported_rule_types()
    assert "single_fact" in types
    assert "threshold" in types
    assert "group_consistency" in types
    assert "topology" in types
    
    caps = RuleCatalogService.list_capabilities("single_fact")
    assert len(caps) > 0
    assert caps[0].rule_type == "single_fact"
    
    assert RuleCatalogService.get_rule_descriptor("unknown_rule") is None

def test_rule_catalog_consistency():
    # Temporarily register a broken rule type
    RuleMetaRegistry.register(RuleMeta(
        rule_type="broken_rule",
        category="logical",
        supported_targets=["devices"],
        supports_grouping=False,
        supports_topology=False
    ))
    
    # Since it has no schema and no capability, the catalog build should fail
    with pytest.raises(RuleCatalogError, match="Consistency Check Failed.*parameter schema"):
        RuleCatalogService.force_rebuild()
        
    # Provide a schema
    ParameterSchemaRegistry._schemas["broken_rule"] = {"required": [], "optional": []}
    
    # Still no capability, should fail
    with pytest.raises(RuleCatalogError, match="Consistency Check Failed.*capabilities"):
        RuleCatalogService.force_rebuild()
        
    # Cleanup to not affect other tests
    del RuleMetaRegistry._registry["broken_rule"]
    del ParameterSchemaRegistry._schemas["broken_rule"]
    RuleCatalogService.force_rebuild()
