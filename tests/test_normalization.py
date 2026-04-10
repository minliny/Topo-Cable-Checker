import pytest
from src.application.normalization_services.normalization_service import NormalizationService
from src.domain.fact_model import NormalizedDataset
from src.application.recognition_services.input_contract import InputContractConfig, SheetConfig, HeaderMapping, RowConstraint

def test_normalization_valid_data():
    svc = NormalizationService()
    
    raw_data = {
        "device": [
            {"device_name": "FW-01", "device_type": "Firewall", "status": "Active", "_source_sheet": "devices_tab", "_source_row": 2}
        ],
        "port": [
            {"device_name": "FW-01", "port_name": "eth0", "port_status": "Up", "_source_sheet": "ports_tab", "_source_row": 2}
        ],
        "link": [
            {"src_device": "FW-01", "src_port": "eth0", "dst_device": "SW-01", "dst_port": "g0/1", "_source_sheet": "links_tab", "_source_row": 2}
        ]
    }
    
    dataset, issues = svc.normalize(raw_data)
    
    assert len(issues) == 0
    assert len(dataset.devices) == 1
    assert dataset.devices[0].device_name == "FW-01"
    assert len(dataset.ports) == 1
    assert len(dataset.links) == 1

def test_normalization_missing_fields_issues():
    svc = NormalizationService()
    
    raw_data = {
        "device": [
            {"device_name": "  ", "device_type": "Firewall", "_source_sheet": "devices_tab", "_source_row": 2} # Empty device name
        ],
        "link": [
            {"src_device": "FW-01", "src_port": "eth0", "dst_device": "", "dst_port": "g0/1", "_source_sheet": "links_tab", "_source_row": 2} # Missing dst_device
        ]
    }
    
    dataset, issues = svc.normalize(raw_data)
    
    # devices missing device_name should be skipped and issue recorded
    assert len(dataset.devices) == 0
    assert len(dataset.links) == 0
    assert len(issues) == 2
    assert issues[0].stage == "normalization"
    assert "Empty" in issues[0].actual
    assert issues[1].stage == "normalization"
    assert "Incomplete" in issues[1].actual

def test_normalization_row_constraints():
    svc = NormalizationService()
    
    svc.contract = InputContractConfig(
        version="v1.1",
        sheets=[
            SheetConfig(
                sheet_type="device",
                keywords=["device"],
                headers=[
                    HeaderMapping("device_name", [], required=True),
                    HeaderMapping("device_type", [], required=False),
                    HeaderMapping("status", [], required=False)
                ],
                row_constraints=[
                    RowConstraint(
                        condition=lambda row: not (row.get("device_type") == "Firewall" and row.get("status") == "Inactive"),
                        error_message="Firewalls cannot be Inactive"
                    )
                ]
            )
        ]
    )
    
    raw_data = {
        "device": [
            {"device_name": "FW-01", "device_type": "Firewall", "status": "Active", "_source_sheet": "devices", "_source_row": 2},
            {"device_name": "FW-02", "device_type": "Firewall", "status": "Inactive", "_source_sheet": "devices", "_source_row": 3}, # violation
            {"device_name": "SW-01", "device_type": "Switch", "status": "Inactive", "_source_sheet": "devices", "_source_row": 4}
        ]
    }
    
    dataset, issues = svc.normalize(raw_data)
    
    assert len(dataset.devices) == 2
    assert dataset.devices[0].device_name == "FW-01"
    assert dataset.devices[1].device_name == "SW-01"
    
    assert len(issues) == 1
    assert issues[0].category == "constraint_violation"
    assert issues[0].stage == "normalization"
def test_normalization_enum_type_issues():
    svc = NormalizationService()
    # Overwrite contract for testing
    svc.contract = InputContractConfig(
        version="v2",
        sheets=[
            SheetConfig(
                sheet_type="device",
                keywords=["device"],
                headers=[
                    HeaderMapping("device_name", [], required=True, type="str"),
                    HeaderMapping("status", [], required=False, type="enum", allowed_values=["Active", "Inactive"]),
                    HeaderMapping("rack_id", [], required=False, type="int")
                ]
            )
        ]
    )
    
    raw_data = {
        "device": [
            # valid row
            {"device_name": "FW-01", "status": "Active", "rack_id": "10", "_source_sheet": "devices", "_source_row": 2},
            # invalid enum
            {"device_name": "FW-02", "status": "Up", "rack_id": "11", "_source_sheet": "devices", "_source_row": 3},
            # invalid type
            {"device_name": "FW-03", "status": "Inactive", "rack_id": "A12", "_source_sheet": "devices", "_source_row": 4}
        ]
    }
    
    dataset, issues = svc.normalize(raw_data)
    
    assert len(dataset.devices) == 1
    assert dataset.devices[0].device_name == "FW-01"
    
    assert len(issues) == 2
    assert issues[0].category == "normalization_error"
    assert "Expected one of ['Active', 'Inactive']" in issues[0].message
    assert issues[1].category == "normalization_error"
    assert "Expected int" in issues[1].message
