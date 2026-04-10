import pytest
from src.application.normalization_services.normalization_service import NormalizationService

def test_normalization_success_path():
    svc = NormalizationService()
    raw_data = {
        "Devices": [
            {"Device Name": "  SW-1  ", "Device Type": "Switch", "Status": "Active"}
        ],
        "Ports": [
            {"Device Name": "SW-1", "Port Name": "Eth1/1", "Port Status": "Up"}
        ],
        "Links": [
            {"Source Device": "SW-1", "Source Port": "Eth1/1", "Dest Device": "SW-2", "Dest Port": "Eth1/2"}
        ]
    }
    
    dataset, issues = svc.normalize(raw_data)
    
    assert len(issues) == 0
    assert len(dataset.devices) == 1
    assert dataset.devices[0].device_name == "SW-1"
    assert len(dataset.ports) == 1
    assert len(dataset.links) == 1

def test_normalization_missing_fields_blocked():
    svc = NormalizationService()
    raw_data = {
        "Devices": [
            {"Device Type": "Switch", "Status": "Active"}, # missing name
            {"Device Name": "SW-2"} # missing type and status
        ],
        "Ports": [
            {"Port Name": "Eth1/1"} # missing device name
        ],
        "Links": [
            {"Source Device": "SW-1"} # missing ports and dest
        ]
    }
    
    dataset, issues = svc.normalize(raw_data)
    
    # Missing names should block creation and create an issue
    assert len(dataset.devices) == 1
    assert dataset.devices[0].device_name == "SW-2"
    assert dataset.devices[0].device_type == "Unknown" # defaulted
    
    assert len(dataset.ports) == 0
    assert len(dataset.links) == 0
    
    assert len(issues) == 3
    assert issues[0].details["entity_type"] == "Device"
    assert issues[1].details["entity_type"] == "Port"
    assert issues[2].details["entity_type"] == "Link"
