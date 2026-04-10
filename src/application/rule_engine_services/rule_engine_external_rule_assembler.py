import os
from typing import Dict, Any

from src.application.recognition_services.rule_definition_loader import RuleDefinitionLoader
from src.application.recognition_services.rule_definition_registry import RuleDefinitionRegistry
from src.application.rule_engine_services.single_fact_rule_compiler import SingleFactRuleCompiler

class RuleEngineExternalRuleAssembler:
    """
    Application-level assembler.
    Responsible for:
    1. Loading RuleDefinitions from an external JSON file.
    2. Registering and categorizing them in the RuleDefinitionRegistry.
    3. Extracting 'rule_engine_single_fact' scope rules.
    4. Compiling them into RuleEngine-consumable compiled_rules.
    """
    
    @staticmethod
    def assemble(rule_json_path: str) -> Dict[str, Dict[str, Any]]:
        """
        Loads rules from the given path and compiles external single_fact rules.
        Returns a dict mapping rule_id -> compiled_rule.
        Raises appropriate exceptions if the file is invalid or rules are malformed.
        """
        if not os.path.exists(rule_json_path):
            raise FileNotFoundError(f"External rule definition file not found: {rule_json_path}")
            
        # 1. Load external definitions
        definitions = RuleDefinitionLoader.load_from_json_file(rule_json_path)
        
        # 2. Register definitions
        registry = RuleDefinitionRegistry()
        registry.register_all(definitions)
        
        # 3. Extract target scope (single_fact)
        # Note: We only extract enabled rules by default
        single_fact_defs = registry.get_by_scope("rule_engine_single_fact", enabled_only=True)
        
        # 4. Compile to executable structure
        compiled_rules = {}
        for rule_def in single_fact_defs:
            try:
                compiled = SingleFactRuleCompiler.compile(rule_def)
                compiled_rules[rule_def.rule_id] = compiled
            except Exception as e:
                # We fail fast if a rule intended for this scope is invalid
                raise ValueError(f"Failed to compile external rule '{rule_def.rule_id}': {e}") from e
                
        return compiled_rules
