from typing import Dict, Any, List
from src.domain.fact_model import DeviceFact, PortFact, LinkFact, NormalizedDataset
from src.domain.result_model import IssueItem
from src.crosscutting.ids.generator import generate_id

class NormalizationService:
    """
    Converts recognized row data (with standard keys) into normalized Domain Facts:
    DeviceFact, PortFact, LinkFact.
    Also produces normalization issues (e.g. data type issues, business logic checks).
    """
    def normalize(self, raw_data: Dict[str, Any]) -> tuple[NormalizedDataset, List[IssueItem]]:
        devices = []
        ports = []
        links = []
        issues = []
        
        for sheet_type, rows in raw_data.items():
            if sheet_type == "device":
                for r in rows:
                    source_sheet = r.get("_source_sheet", "unknown")
                    source_row = r.get("_source_row", 0)
                    device_name = r.get("device_name")
                    
                    if not device_name or not str(device_name).strip():
                        issues.append(IssueItem(
                            issue_id=generate_id(),
                            message=f"Device name is empty in sheet '{source_sheet}' row {source_row}.",
                            evidence={"sheet": source_sheet, "row": source_row},
                            expected="Non-empty device name",
                            actual="Empty",
                            details={"row_data": r},
                            source_row=source_row,
                            severity="high",
                            category="normalization_error",
                            stage="normalization"
                        ))
                        continue
                        
                    devices.append(DeviceFact(
                        device_name=str(device_name).strip(),
                        device_type=str(r.get("device_type")).strip() if r.get("device_type") is not None else None,
                        status=str(r.get("status")).strip() if r.get("status") is not None else None,
                        _source_sheet=source_sheet
                    ))
            elif sheet_type == "port":
                for r in rows:
                    source_sheet = r.get("_source_sheet", "unknown")
                    source_row = r.get("_source_row", 0)
                    device_name = r.get("device_name")
                    port_name = r.get("port_name")
                    
                    if not device_name or not port_name or not str(device_name).strip() or not str(port_name).strip():
                        issues.append(IssueItem(
                            issue_id=generate_id(),
                            message=f"Missing device or port name in sheet '{source_sheet}' row {source_row}.",
                            evidence={"sheet": source_sheet, "row": source_row},
                            expected="Non-empty device and port names",
                            actual="Empty",
                            details={"row_data": r},
                            source_row=source_row,
                            severity="high",
                            category="normalization_error",
                            stage="normalization"
                        ))
                        continue
                        
                    ports.append(PortFact(
                        device_name=str(device_name).strip(),
                        port_name=str(port_name).strip(),
                        port_status=str(r.get("port_status")).strip() if r.get("port_status") is not None else None,
                        _source_sheet=source_sheet
                    ))
            elif sheet_type == "link":
                for r in rows:
                    source_sheet = r.get("_source_sheet", "unknown")
                    source_row = r.get("_source_row", 0)
                    src_device = r.get("src_device")
                    src_port = r.get("src_port")
                    dst_device = r.get("dst_device")
                    dst_port = r.get("dst_port")
                    
                    if not src_device or not src_port or not dst_device or not dst_port or not all(str(x).strip() for x in [src_device, src_port, dst_device, dst_port]):
                        issues.append(IssueItem(
                            issue_id=generate_id(),
                            message=f"Missing connection endpoint info in sheet '{source_sheet}' row {source_row}.",
                            evidence={"sheet": source_sheet, "row": source_row},
                            expected="Complete source and dest info",
                            actual="Incomplete",
                            details={"row_data": r},
                            source_row=source_row,
                            severity="high",
                            category="normalization_error",
                            stage="normalization"
                        ))
                        continue
                        
                    links.append(LinkFact(
                        src_device=str(src_device).strip(),
                        src_port=str(src_port).strip(),
                        dst_device=str(dst_device).strip(),
                        dst_port=str(dst_port).strip(),
                        _source_sheet=source_sheet
                    ))
        
        return NormalizedDataset(devices=devices, ports=ports, links=links), issues
