from typing import Dict, Any, List, Tuple
from src.domain.fact_model import DeviceFact, PortFact, LinkFact, NormalizedDataset
from src.domain.result_model import IssueItem
from src.crosscutting.ids.generator import generate_id

class NormalizationService:
    """
    Converts raw excel row data into normalized Domain Facts:
    DeviceFact, PortFact, LinkFact
    
    Enhanced with basic type validation, whitespace trimming,
    default values, and missing critical field blocking.
    """
    def _clean_str(self, val: Any) -> str:
        if val is None:
            return ""
        return str(val).strip()

    def normalize(self, raw_data: Dict[str, Any]) -> Tuple[NormalizedDataset, List[IssueItem]]:
        devices = []
        ports = []
        links = []
        issues = []

        for sheet_name, rows in raw_data.items():
            s_name = sheet_name.lower()
            if "device" in s_name:
                for i, r in enumerate(rows):
                    dev_name = self._clean_str(r.get("Device Name", r.get("name")))
                    dev_type = self._clean_str(r.get("Device Type", r.get("type")))
                    status = self._clean_str(r.get("Status", r.get("status")))
                    
                    if not dev_name:
                        issues.append(self._create_issue("Device", i, "device_name", "Missing required field: device_name", r))
                        continue
                        
                    devices.append(DeviceFact(
                        device_name=dev_name,
                        device_type=dev_type or "Unknown",
                        status=status or "Unknown",
                        _source_sheet=sheet_name
                    ))
            elif "port" in s_name:
                for i, r in enumerate(rows):
                    dev_name = self._clean_str(r.get("Device Name"))
                    port_name = self._clean_str(r.get("Port Name"))
                    port_status = self._clean_str(r.get("Port Status"))
                    
                    if not dev_name or not port_name:
                        issues.append(self._create_issue("Port", i, "device_name/port_name", "Missing required fields: device_name and/or port_name", r))
                        continue
                        
                    ports.append(PortFact(
                        device_name=dev_name,
                        port_name=port_name,
                        port_status=port_status or "Unknown",
                        _source_sheet=sheet_name
                    ))
            elif "link" in s_name:
                for i, r in enumerate(rows):
                    src_dev = self._clean_str(r.get("Source Device"))
                    src_port = self._clean_str(r.get("Source Port"))
                    dst_dev = self._clean_str(r.get("Dest Device"))
                    dst_port = self._clean_str(r.get("Dest Port"))
                    
                    if not src_dev or not src_port or not dst_dev or not dst_port:
                        issues.append(self._create_issue("Link", i, "link_endpoints", "Missing required link endpoints (src/dst device/port)", r))
                        continue
                        
                    links.append(LinkFact(
                        src_device=src_dev,
                        src_port=src_port,
                        dst_device=dst_dev,
                        dst_port=dst_port,
                        _source_sheet=sheet_name
                    ))

        return NormalizedDataset(devices=devices, ports=ports, links=links), issues

    def _create_issue(self, entity_type: str, row_idx: int, field: str, message: str, row_data: Dict) -> IssueItem:
        return IssueItem(
            issue_id=generate_id(),
            message=message,
            evidence={"rule_id": "NORM_001", "item_data": row_data},
            expected="Valid non-empty value",
            actual="Empty or invalid",
            details={"target_field": field, "entity_type": entity_type},
            source_row=row_idx + 1,
            severity="error",
            category="normalization"
        )
