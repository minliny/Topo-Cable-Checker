import pytest
import json
import dataclasses
from src.application.recognition_services.rule_definition_model import RuleDefinition
from src.application.recognition_services.rule_converter import RuleDefinitionConverter
from src.application.recognition_services.input_contract import InputContractConfig, SheetConfig, HeaderMapping
from src.application.normalization_services.normalization_service import NormalizationService

def test_rule_definition_serialization():
    # 1. Create a RuleDefinition
    rule_def = RuleDefinition(
        rule_id="R_EXT_01",
        name="External Rule Test",
        description="If status is active, rack_id must be provided",
        rule_type="if_field_equals_then_required",
        parameters={
            "target_field": "status",
            "expected_value": "Active",
            "dependent_field": "rack_id"
        },
        error_message="Active devices must have a rack_id",
        severity="error",
        enabled=True,
        group="compliance"
    )
    
    # 2. Convert to dictionary (which proves JSON/YAML serializability)
    rule_dict = dataclasses.asdict(rule_def)
    json_str = json.dumps(rule_dict)
    
    # 3. Deserialize back
    loaded_dict = json.loads(json_str)
    loaded_rule_def = RuleDefinition(**loaded_dict)
    
    assert loaded_rule_def.rule_id == "R_EXT_01"
    assert loaded_rule_def.parameters["target_field"] == "status"

def test_rule_definition_to_runtime_conversion():
    rule_def = RuleDefinition(
        rule_id="R_EXT_02",
        name="Not Inactive Test",
        description="Device cannot be inactive",
        rule_type="field_not_equals",
        parameters={
            "target_field": "status",
            "expected_value": "Inactive"
        },
        error_message="Device cannot be Inactive",
        severity="warning"
    )
    
    # Convert
    runtime_constraint = RuleDefinitionConverter.to_runtime(rule_def)
    
    # Verify metadata
    assert runtime_constraint.id == "R_EXT_02"
    assert runtime_constraint.severity == "warning"
    
    # Verify condition execution
    assert runtime_constraint.condition({"status": "Active"}) is True
    assert runtime_constraint.condition({"status": "Inactive"}) is False

def test_external_rule_in_normalization():
    # 1. Create an external rule definition
    rule_def = RuleDefinition(
        rule_id="R_EXT_03",
        name="Require Rack for Active",
        description="Active devices must have a rack_id",
        rule_type="if_field_equals_then_required",
        parameters={
            "target_field": "status",
            "expected_value": "Active",
            "dependent_field": "rack_id"
        },
        error_message="Active devices must have a rack_id",
        severity="error"
    )
    
    # 2. Convert to runtime constraint
    constraint = RuleDefinitionConverter.to_runtime(rule_def)
    
    # 3. Build a contract using the external rule
    contract = InputContractConfig(
        version="v2",
        source_type="external",
        source_name="json_loaded_contract",
        sheets=[
            SheetConfig(
                sheet_type="device",
                keywords=["device"],
                headers=[
                    HeaderMapping("device_name", [], required=True),
                    HeaderMapping("status", [], required=False),
                    HeaderMapping("rack_id", [], required=False)
                ],
                row_constraints=[constraint]
            )
        ]
    )
    
    # 4. Run Normalization
    svc = NormalizationService()
    svc.contract = contract
    
    raw_data = {
        "device": [
            # valid row
            {"device_name": "FW-01", "status": "Active", "rack_id": "10", "_source_sheet": "devices", "_source_row": 2},
            # violation: Active but no rack_id
            {"device_name": "FW-02", "status": "Active", "rack_id": "", "_source_sheet": "devices", "_source_row": 3},
            # valid: Inactive, rack_id not required
            {"device_name": "FW-03", "status": "Inactive", "rack_id": "", "_source_sheet": "devices", "_source_row": 4}
        ]
    }
    
    dataset, issues = svc.normalize(raw_data)
    
    # Check execution result
    assert len(issues) == 1
    
    issue = issues[0]
    assert issue.category == "constraint_violation"
    assert issue.severity == "error"
    assert issue.evidence["rule_id"] == "R_EXT_03"
    assert "Active devices must have a rack_id" in issue.message
    assert issue.source_row == 3
