from typing import List, Dict, Optional
from src.application.recognition_services.rule_definition_model import RuleDefinition
from src.application.recognition_services.rule_converter import RuleDefinitionConverter
from src.application.recognition_services.input_contract import RowConstraint

class RuleDefinitionRegistry:
    """
    Central registry for managing RuleDefinition objects.
    Maintains uniqueness by rule_id and supports batch compilation into runtime RowConstraints.
    """
    
    def __init__(self):
        self._definitions: Dict[str, RuleDefinition] = {}
        
    def register(self, definition: RuleDefinition) -> None:
        if definition.rule_id in self._definitions:
            raise ValueError(f"Rule ID '{definition.rule_id}' is already registered.")
        self._definitions[definition.rule_id] = definition
        
    def register_all(self, definitions: List[RuleDefinition]) -> None:
        for d in definitions:
            self.register(d)
            
    def get(self, rule_id: str) -> Optional[RuleDefinition]:
        return self._definitions.get(rule_id)
        
    def get_all(self, enabled_only: bool = False) -> List[RuleDefinition]:
        if enabled_only:
            return [d for d in self._definitions.values() if d.enabled]
        return list(self._definitions.values())
        
    def to_row_constraints(self, enabled_only: bool = True) -> List[RowConstraint]:
        """
        Compiles the registered definitions into executable runtime objects.
        """
        definitions = self.get_all(enabled_only=enabled_only)
        constraints = []
        for d in definitions:
            try:
                constraints.append(RuleDefinitionConverter.to_runtime(d))
            except Exception as e:
                # Provide context about which rule failed compilation
                raise RuntimeError(f"Failed to compile rule '{d.rule_id}' to runtime constraint: {e}") from e
        return constraints
