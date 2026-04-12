from typing import Dict, Any, List, Tuple
from src.domain.fact_model import DeviceFact, PortFact, LinkFact, NormalizedDataset
from src.domain.result_model import IssueItem
from src.crosscutting.ids.generator import generate_id
from src.application.recognition_services.input_contract import DEFAULT_CONTRACT

class NormalizationService:
    """
    Converts recognized row data (with standard keys) into normalized Domain Facts:
    DeviceFact, PortFact, LinkFact.
    Also produces normalization issues (e.g. data type issues, business logic checks).
    """
    def __init__(self):
        self.contract = DEFAULT_CONTRACT
        
    def _validate_and_normalize_row(self, row: Dict[str, Any], sheet_config: Any, source_sheet: str, source_row: int) -> tuple[Dict[str, Any], List[IssueItem]]:
        header_configs = {h.standard_name: h for h in sheet_config.headers} if sheet_config else {}
        normalized_row = dict(row)
        issues = []
        
        # Phase 1: HeaderMapping Validation
        for field_name, value in row.items():
            if field_name.startswith("_") or field_name not in header_configs:
                continue
                
            config = header_configs[field_name]
            
            # skip None values if not required (required check is already done in recognition)
            if value is None or str(value).strip() == "":
                continue
                
            # 1. Type validation/conversion
            if config.type == "str":
                value = str(value).strip()
            elif config.type == "int":
                try:
                    value = int(value)
                except ValueError:
                    issues.append(IssueItem(
                        issue_id=generate_id(),
                        message=f"Invalid type for {field_name} in sheet '{source_sheet}' row {source_row}. Expected int.",
                        evidence={"sheet": source_sheet, "row": source_row, "field": field_name, "value": value},
                        expected="int",
                        actual=str(type(value).__name__),
                        details={"row_data": row},
                        source_row=source_row,
                        severity="high",
                        category="normalization_error",
                        stage="normalization"
                    ))
                    continue
            elif config.type == "enum":
                value = str(value).strip()
                
            # 2. Allowed values validation
            if config.allowed_values is not None:
                # case-insensitive check
                allowed_lower = [str(a).lower() for a in config.allowed_values]
                if str(value).lower() not in allowed_lower:
                    issues.append(IssueItem(
                        issue_id=generate_id(),
                        message=f"Invalid value '{value}' for {field_name} in sheet '{source_sheet}' row {source_row}. Expected one of {config.allowed_values}.",
                        evidence={"sheet": source_sheet, "row": source_row, "field": field_name, "value": value},
                        expected=f"One of {config.allowed_values}",
                        actual=value,
                        details={"row_data": row},
                        source_row=source_row,
                        severity="high",
                        category="normalization_error",
                        stage="normalization"
                    ))
                    continue
                    
            # 3. Custom normalize function
            if config.normalize_fn is not None:
                try:
                    value = config.normalize_fn(value)
                except Exception as e:
                    issues.append(IssueItem(
                        issue_id=generate_id(),
                        message=f"Normalization function failed for {field_name} in sheet '{source_sheet}' row {source_row}: {str(e)}",
                        evidence={"sheet": source_sheet, "row": source_row, "field": field_name, "value": value},
                        expected="Valid value",
                        actual="Exception",
                        details={"row_data": row, "error": str(e)},
                        source_row=source_row,
                        severity="high",
                        category="normalization_error",
                        stage="normalization"
                    ))
                    continue
                    
            normalized_row[field_name] = value

        # Phase 2: RowConstraint Validation (Cross-field validation)
        if sheet_config and hasattr(sheet_config, "row_constraints"):
            for constraint in sheet_config.row_constraints:
                if not constraint.enabled:
                    continue
                    
                try:
                    is_valid = constraint.condition(normalized_row)
                    if not is_valid:
                        issues.append(IssueItem(
                            issue_id=generate_id(),
                            message=f"Constraint violation in sheet '{source_sheet}' row {source_row}: {constraint.error_message}",
                            evidence={"sheet": source_sheet, "row": source_row, "rule_id": constraint.id, "rule_name": constraint.name},
                            expected="Constraint satisfied",
                            actual="Constraint violated",
                            details={"row_data": normalized_row, "error_message": constraint.error_message, "rule_id": constraint.id},
                            source_row=source_row,
                            severity=constraint.severity,
                            category="constraint_violation",
                            stage="normalization"
                        ))
                except Exception as e:
                    issues.append(IssueItem(
                        issue_id=generate_id(),
                        message=f"Error evaluating constraint in sheet '{source_sheet}' row {source_row}: {str(e)}",
                        evidence={"sheet": source_sheet, "row": source_row, "rule_id": constraint.id},
                        expected="Evaluation success",
                        actual="Exception",
                        details={"row_data": normalized_row, "error": str(e), "rule_id": constraint.id},
                        source_row=source_row,
                        severity="high",
                        category="constraint_violation",
                        stage="normalization"
                    ))
            
        return normalized_row, issues
        
    def normalize(self, raw_data: Dict[str, Any]) -> tuple[NormalizedDataset, List[IssueItem]]:
        devices = []
        ports = []
        links = []
        issues = []
        
        for sheet_type, rows in raw_data.items():
            # Get sheet config
            sheet_config = next((s for s in self.contract.sheets if s.sheet_type == sheet_type), None)
            
            if sheet_type == "device":
                for r in rows:
                    source_sheet = r.get("_source_sheet", "unknown")
                    source_row = r.get("_source_row", 0)
                    
                    # Contract Validation
                    norm_row, row_issues = self._validate_and_normalize_row(r, sheet_config, source_sheet, source_row)
                    if row_issues:
                        issues.extend(row_issues)
                        continue
                        
                    device_name = norm_row.get("device_name")
                    
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
                        device_type=norm_row.get("device_type"),
                        status=norm_row.get("status"),
                        _source_sheet=source_sheet
                    ))
            elif sheet_type == "port":
                for r in rows:
                    source_sheet = r.get("_source_sheet", "unknown")
                    source_row = r.get("_source_row", 0)
                    
                    # Contract Validation
                    norm_row, row_issues = self._validate_and_normalize_row(r, sheet_config, source_sheet, source_row)
                    if row_issues:
                        issues.extend(row_issues)
                        continue
                        
                    device_name = norm_row.get("device_name")
                    port_name = norm_row.get("port_name")
                    
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
                        port_status=norm_row.get("port_status"),
                        _source_sheet=source_sheet
                    ))
            elif sheet_type == "link":
                for r in rows:
                    source_sheet = r.get("_source_sheet", "unknown")
                    source_row = r.get("_source_row", 0)
                    
                    # Contract Validation
                    norm_row, row_issues = self._validate_and_normalize_row(r, sheet_config, source_sheet, source_row)
                    if row_issues:
                        issues.extend(row_issues)
                        continue
                        
                    src_device = norm_row.get("src_device")
                    src_port = norm_row.get("src_port")
                    dst_device = norm_row.get("dst_device")
                    dst_port = norm_row.get("dst_port")
                    
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
