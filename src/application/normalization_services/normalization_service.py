from typing import Dict, Any, List
from src.domain.fact_model import DeviceFact, PortFact, LinkFact, NormalizedDataset

class NormalizationService:
    """
    Converts raw excel row data into normalized Domain Facts:
    DeviceFact, PortFact, LinkFact
    
    TODO: Currently this service only performs basic field mapping.
    Future enhancements required:
    - Type validation for all fields
    - Handling of missing or null values
    - Exception blocking for malformed row data
    - Application of domain-specific cleaning rules
    """
    def normalize(self, raw_data: Dict[str, Any]) -> NormalizedDataset:
        devices = []
        ports = []
        links = []
        
        for sheet_name, rows in raw_data.items():
            s_name = sheet_name.lower()
            if "device" in s_name:
                for r in rows:
                    devices.append(DeviceFact(
                        device_name=r.get("Device Name", r.get("name")),
                        device_type=r.get("Device Type", r.get("type")),
                        status=r.get("Status", r.get("status")),
                        _source_sheet=sheet_name
                    ))
            elif "port" in s_name:
                for r in rows:
                    ports.append(PortFact(
                        device_name=r.get("Device Name"),
                        port_name=r.get("Port Name"),
                        port_status=r.get("Port Status"),
                        _source_sheet=sheet_name
                    ))
            elif "link" in s_name:
                for r in rows:
                    links.append(LinkFact(
                        src_device=r.get("Source Device"),
                        src_port=r.get("Source Port"),
                        dst_device=r.get("Dest Device"),
                        dst_port=r.get("Dest Port"),
                        _source_sheet=sheet_name
                    ))
        
        return NormalizedDataset(devices=devices, ports=ports, links=links)
