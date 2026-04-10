from typing import List, Optional
from src.application.recognition_services.input_contract import InputContractConfig
from src.application.recognition_services.rule_definition_loader import RuleDefinitionLoader
from src.application.recognition_services.rule_definition_registry import RuleDefinitionRegistry

class ContractBuilder:
    """
    Helper utility to assemble a full InputContractConfig with external rules.
    This encapsulates the 'Formal Loading Pipeline'.
    """
    
    @staticmethod
    def build_from_base_with_external_rules(
        base_contract: InputContractConfig, 
        rule_json_path: str,
        target_sheet_type: str = "device"
    ) -> InputContractConfig:
        """
        Loads rules from a JSON file, registers them, compiles them to RowConstraints,
        and injects them into a specific sheet of the given base contract.
        Returns a new modified InputContractConfig instance.
        """
        # 1. Load external definitions
        definitions = RuleDefinitionLoader.load_from_json_file(rule_json_path)
        
        # 2. Register definitions (ensures uniqueness and provides central management)
        registry = RuleDefinitionRegistry()
        registry.register_all(definitions)
        
        # 3. Compile to runtime constraints (filtering out disabled ones by default)
        runtime_constraints = registry.to_row_constraints(enabled_only=True)
        
        # 4. Create a shallow copy of the contract structure to avoid modifying the original DEFAULT_CONTRACT
        new_sheets = []
        for sheet in base_contract.sheets:
            if sheet.sheet_type == target_sheet_type:
                # Create a new sheet config with appended constraints
                # Note: For a fully immutable setup, we would deepcopy, but this suffices for the minimal pipeline.
                import copy
                new_sheet = copy.copy(sheet)
                # Keep existing constraints (if any) and add the new external ones
                new_sheet.row_constraints = list(sheet.row_constraints) + runtime_constraints
                new_sheets.append(new_sheet)
            else:
                new_sheets.append(sheet)
                
        # 5. Return new Contract marked as external
        return InputContractConfig(
            version=base_contract.version,
            source_type="external",
            source_name=f"extended_from_{base_contract.source_name}_via_{rule_json_path}",
            sheets=new_sheets
        )
