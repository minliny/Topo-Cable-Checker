from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class RuleDefinition:
    """
    A serializable model representing a data contract rule.
    This model can be easily converted to and from JSON/YAML, and does not contain any Python code/lambdas.
    """
    rule_id: str
    name: str
    description: str
    
    # "field_equals", "field_not_equals", "if_field_equals_then_required"
    rule_type: str
    
    # Flexible container for rule parameters (e.g., target_field, expected_value, dependent_field)
    parameters: Dict[str, Any]
    
    error_message: str
    severity: str = "warning"
    enabled: bool = True
    group: str = "validation"
    
    # Governance metadata
    schema_version: str = "1.0"
    message_template: Optional[str] = None
