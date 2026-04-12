from src.application.recognition_services.rule_definition_model import RuleDefinition

"""
This file serves as documentation and a structural proof-of-concept for how macroscopic 
RuleEngine rules can be modeled using the unified RuleDefinition model.

Currently, the RuleEngine relies on hardcoded BaselineProfile.rule_set containing dicts.
In the future, RuleEngine will read from the RuleDefinitionRegistry using `get_by_scope("rule_engine_single_fact")`.

Example mapping of a RuleEngine "single_fact" rule to RuleDefinition:

Existing hardcoded dict in BaselineProfile:
{
    "type": "single_fact",
    "target": "DeviceFact",
    "condition": lambda device: device.status != "Offline",
    "issue_message": "Device is offline in baseline.",
    "severity": "high"
}

Mapped Unified RuleDefinition:
"""

EXAMPLE_SINGLE_FACT_RULE = RuleDefinition(
    rule_id="RE_SF_001",
    name="Device Online Check",
    description="Ensures all devices in the baseline are not marked as Offline.",
    rule_type="field_not_equals",  # Reuses the same basic operator types where applicable
    parameters={
        "target_field": "status",
        "expected_value": "Offline"
    },
    error_message="Device is offline in baseline.",
    severity="high",
    enabled=True,
    group="availability",
    
    # --- The critical new boundary fields ---
    engine_scope="rule_engine_single_fact", # Directs this rule to the RuleEngine's SingleFactExecutor
    applies_to=["DeviceFact"],              # Tells the executor which domain model to iterate over
    
    schema_version="1.0",
    message_template="Device {{device_name}} is offline."
)

"""
Example mapping of a RuleEngine "topology" rule to RuleDefinition:

Existing hardcoded dict in BaselineProfile:
{
    "type": "topology",
    "sub_type": "bidirectional_link",
    "issue_message": "Link is unidirectional or missing reverse path.",
    "severity": "high"
}

Mapped Unified RuleDefinition:
"""

EXAMPLE_TOPOLOGY_RULE = RuleDefinition(
    rule_id="RE_TOPO_001",
    name="Bidirectional Link Check",
    description="Ensures all links have a corresponding reverse link.",
    rule_type="bidirectional_link", # A complex rule_type specific to the topology executor
    parameters={}, # Topology rules might not need parameters, or might need specific tolerance params
    error_message="Link is unidirectional or missing reverse path.",
    severity="high",
    enabled=True,
    group="topology_integrity",
    
    engine_scope="rule_engine_topology",
    applies_to=["LinkFact"],
    
    schema_version="1.0"
)
