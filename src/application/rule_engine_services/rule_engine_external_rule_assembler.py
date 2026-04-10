import os
from typing import Dict, Any

from src.application.recognition_services.rule_definition_loader import RuleDefinitionLoader
from src.application.recognition_services.rule_definition_registry import RuleDefinitionRegistry
from src.application.rule_engine_services.single_fact_rule_compiler import SingleFactRuleCompiler
from src.application.rule_engine_services.threshold_rule_compiler import ThresholdRuleCompiler
from src.domain.compiled_rule_schema import CompiledRule

class RuleEngineExternalRuleAssembler:
    """
    Application-level assembler.
    Responsible for:
    1. Loading RuleDefinitions from an external JSON file.
    2. Registering and categorizing them in the RuleDefinitionRegistry.
    3. Extracting 'rule_engine_single_fact' scope rules.
    4. Compiling them into RuleEngine-consumable compiled_rules.
    """
    
    COMPILER_REGISTRY = {
        "rule_engine_single_fact": SingleFactRuleCompiler,
        "rule_engine_threshold": ThresholdRuleCompiler
    }
    
    @staticmethod
    def assemble(rule_json_path: str) -> Dict[str, CompiledRule]:
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
        
        # 3. Extract target scopes
        all_defs = registry.get_all(enabled_only=True)
        supported_scopes = set(RuleEngineExternalRuleAssembler.COMPILER_REGISTRY.keys()) | {"normalization"}
        unsupported_defs = [d for d in all_defs if d.engine_scope not in supported_scopes]
        
        if unsupported_defs:
            unsupported_info = [{"rule_id": d.rule_id, "scope": d.engine_scope} for d in unsupported_defs]
            raise ValueError(f"Found rules with unsupported engine_scope: {unsupported_info}")
        
        # 4. Compile to executable structure
        compiled_rules = {}
        
        for rule_def in all_defs:
            if rule_def.engine_scope == "normalization":
                continue
                
            compiler = RuleEngineExternalRuleAssembler.COMPILER_REGISTRY.get(rule_def.engine_scope)
            if compiler:
                try:
                    compiled = compiler.compile(rule_def)
                    compiled_rules[rule_def.rule_id] = compiled
                except Exception as e:
                    raise ValueError(f"Failed to compile external {rule_def.engine_scope} rule '{rule_def.rule_id}': {e}") from e
                
        return compiled_rules
