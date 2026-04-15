# Rule Engine Mapping Concept (Non-Runtime Note)

This note was previously stored under `src/domain/` as a Python file, but it is not part of the runtime.
It documents a possible future mapping between `RuleDefinition` and RuleEngine rules.

## Context

Currently, the RuleEngine relies on `BaselineProfile.rule_set` containing dicts.
A possible future direction is to read from a `RuleDefinitionRegistry` using something like `get_by_scope("rule_engine_single_fact")`.

## Example mapping: Single Fact

Existing hardcoded dict in `BaselineProfile` (conceptual):

```python
{
    "type": "single_fact",
    "target": "DeviceFact",
    "condition": lambda device: device.status != "Offline",
    "issue_message": "Device is offline in baseline.",
    "severity": "high"
}
```

Mapped unified `RuleDefinition` (conceptual):

```python
from src.application.recognition_services.rule_definition_model import RuleDefinition

EXAMPLE_SINGLE_FACT_RULE = RuleDefinition(
    rule_id="RE_SF_001",
    name="Device Online Check",
    description="Ensures all devices in the baseline are not marked as Offline.",
    rule_type="field_not_equals",
    parameters={
        "target_field": "status",
        "expected_value": "Offline"
    },
    error_message="Device is offline in baseline.",
    severity="high",
    enabled=True,
    group="availability",
    engine_scope="rule_engine_single_fact",
    applies_to=["DeviceFact"],
    schema_version="1.0",
    message_template="Device {{device_name}} is offline."
)
```

## Example mapping: Topology

Existing hardcoded dict in `BaselineProfile` (conceptual):

```python
{
    "type": "topology",
    "sub_type": "bidirectional_link",
    "issue_message": "Link is unidirectional or missing reverse path.",
    "severity": "high"
}
```

Mapped unified `RuleDefinition` (conceptual):

```python
from src.application.recognition_services.rule_definition_model import RuleDefinition

EXAMPLE_TOPOLOGY_RULE = RuleDefinition(
    rule_id="RE_TOPO_001",
    name="Bidirectional Link Check",
    description="Ensures all links have a corresponding reverse link.",
    rule_type="bidirectional_link",
    parameters={},
    error_message="Link is unidirectional or missing reverse path.",
    severity="high",
    enabled=True,
    group="topology_integrity",
    engine_scope="rule_engine_topology",
    applies_to=["LinkFact"],
    schema_version="1.0"
)
```

