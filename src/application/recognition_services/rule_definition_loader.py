import json
from typing import List, Dict, Any
from src.application.recognition_services.rule_definition_model import RuleDefinition
import os

class RuleDefinitionLoader:
    """
    Responsible for loading RuleDefinitions from external JSON files.
    """
    
    SUPPORTED_RULE_TYPES = {
        "field_equals",
        "field_not_equals",
        "if_field_equals_then_required"
    }

    @staticmethod
    def load_from_json_file(file_path: str) -> List[RuleDefinition]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Rule definition file not found: {file_path}")
            
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse JSON file {file_path}: {e}")
                
        if not isinstance(data, list):
            # Allow for a dict wrapper if it has a 'rules' key, otherwise assume it's just a single object or invalid
            if isinstance(data, dict) and "rules" in data and isinstance(data["rules"], list):
                data = data["rules"]
            else:
                raise ValueError(f"JSON file {file_path} must contain a list of rules or an object with a 'rules' list.")
                
        definitions = []
        for index, item in enumerate(data):
            if not isinstance(item, dict):
                raise ValueError(f"Rule at index {index} is not a JSON object.")
                
            # Basic validation
            missing_fields = []
            for required_field in ["rule_id", "name", "rule_type", "parameters", "error_message"]:
                if required_field not in item:
                    missing_fields.append(required_field)
            if missing_fields:
                raise ValueError(f"Rule at index {index} is missing required fields: {missing_fields}")
                
            if item["rule_type"] not in RuleDefinitionLoader.SUPPORTED_RULE_TYPES:
                raise ValueError(f"Rule '{item['rule_id']}' uses an unsupported rule_type: {item['rule_type']}")
                
            definitions.append(RuleDefinition(**item))
            
        return definitions
