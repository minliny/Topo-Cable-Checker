import pytest
import json
import os
import tempfile
from src.application.recognition_services.rule_definition_loader import RuleDefinitionLoader
from src.application.recognition_services.rule_definition_registry import RuleDefinitionRegistry
from src.application.recognition_services.rule_definition_model import RuleDefinition
from src.application.recognition_services.contract_builder import ContractBuilder
from src.application.recognition_services.input_contract import DEFAULT_CONTRACT
from src.application.normalization_services.normalization_service import NormalizationService

def _create_temp_json(content: dict) -> str:
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        json.dump(content, f)
    return path

def test_load_rule_definitions_from_json_file():
    data = {
        "rules": [
            {
                "rule_id": "TEST_01",
                "name": "Test Rule",
                "description": "Test Desc",
                "rule_type": "field_equals",
                "parameters": {"target_field": "status", "expected_value": "Active"},
                "error_message": "Must be Active"
            }
        ]
    }
    path = _create_temp_json(data)
    
    try:
        definitions = RuleDefinitionLoader.load_from_json_file(path)
        assert len(definitions) == 1
        assert definitions[0].rule_id == "TEST_01"
        assert definitions[0].rule_type == "field_equals"
    finally:
        os.remove(path)

def test_loader_rejects_unknown_rule_type():
    data = [
        {
            "rule_id": "TEST_02",
            "name": "Bad Type Rule",
            "description": "Test Desc",
            "rule_type": "invalid_magic_type",
            "parameters": {},
            "error_message": "Bad type"
        }
    ]
    path = _create_temp_json(data)
    
    try:
        with pytest.raises(ValueError, match="unsupported rule_type"):
            RuleDefinitionLoader.load_from_json_file(path)
    finally:
        os.remove(path)

def test_loader_rejects_missing_fields():
    data = [
        {
            "rule_id": "TEST_03",
            # missing "name"
            "description": "Test Desc",
            "rule_type": "field_equals",
            "parameters": {},
            "error_message": "Bad"
        }
    ]
    path = _create_temp_json(data)
    
    try:
        with pytest.raises(ValueError, match="missing required fields"):
            RuleDefinitionLoader.load_from_json_file(path)
    finally:
        os.remove(path)

def test_registry_rejects_duplicate_rule_id():
    registry = RuleDefinitionRegistry()
    def1 = RuleDefinition("DUP_01", "Name", "Desc", "field_equals", {}, "Err")
    def2 = RuleDefinition("DUP_01", "Other Name", "Desc", "field_not_equals", {}, "Err")
    
    registry.register(def1)
    
    with pytest.raises(ValueError, match="already registered"):
        registry.register(def2)

def test_file_loaded_rules_can_run_in_normalization_pipeline():
    # This is the end-to-end test proving the formal loading pipeline
    
    data = [
        {
            "rule_id": "E2E_01",
            "name": "E2E File Rule",
            "description": "Device cannot be offline",
            "rule_type": "field_not_equals",
            "parameters": {"target_field": "status", "expected_value": "Offline"},
            "error_message": "Device is offline!",
            "severity": "critical",
            "enabled": True,
            "group": "e2e_testing",
            "schema_version": "1.1",
            "message_template": "Device {{device_name}} is offline!"
        }
    ]
    path = _create_temp_json(data)
    
    try:
        # Build the contract using the Builder utility (Formal Pipeline)
        contract = ContractBuilder.build_from_base_with_external_rules(
            base_contract=DEFAULT_CONTRACT,
            rule_json_path=path,
            target_sheet_type="device"
        )
        
        # Verify contract properties
        assert contract.source_type == "external"
        assert contract.source_name.startswith("extended_from_default_contract")
        
        # Run through NormalizationService
        svc = NormalizationService()
        svc.contract = contract
        
        raw_data = {
            "device": [
                {"device_name": "R-01", "status": "Online", "_source_sheet": "dev", "_source_row": 2}, # Valid
                {"device_name": "R-02", "status": "Offline", "_source_sheet": "dev", "_source_row": 3} # Violation
            ]
        }
        
        dataset, issues = svc.normalize(raw_data)
        
        # 1 valid device should be produced
        assert len(dataset.devices) == 1
        
        # 1 issue should be recorded
        assert len(issues) == 1
        
        issue = issues[0]
        assert issue.category == "constraint_violation"
        assert issue.severity == "critical"
        assert issue.evidence["rule_id"] == "E2E_01"
        assert "Device is offline!" in issue.message
        assert issue.source_row == 3
        
    finally:
        os.remove(path)
