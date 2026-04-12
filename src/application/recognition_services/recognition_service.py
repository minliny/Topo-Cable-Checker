from src.domain.interfaces import ITaskRepository, IResultRepository, IExcelReader
from src.domain.task_model import TaskStatus
from src.domain.result_model import RecognitionResultSnapshot, IssueItem
from src.crosscutting.errors.exceptions import TaskError
from src.crosscutting.ids.generator import generate_id
from src.application.recognition_services.input_contract import DEFAULT_CONTRACT
from typing import Dict, Any, List
import dataclasses

class RecognitionService:
    def __init__(self, task_repo: ITaskRepository = None, result_repo: IResultRepository = None, excel_reader: IExcelReader = None):
        if task_repo is None or result_repo is None or excel_reader is None:
            from src.infrastructure.repository import TaskRepository, ResultRepository
            from src.infrastructure.excel_reader import ExcelReader
            self.task_repo = task_repo or TaskRepository()
            self.result_repo = result_repo or ResultRepository()
            self.excel_reader = excel_reader or ExcelReader()
        else:
            self.task_repo = task_repo
            self.result_repo = result_repo
            self.excel_reader = excel_reader
        self.contract = DEFAULT_CONTRACT
        
    def recognize_data(self, task_id: str) -> Dict[str, Any]:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskError(f"Task {task_id} not found.")
        
        if task.task_status != TaskStatus.data_attached:
            raise TaskError("Task must be in data_attached state.")
            
        # 1. Read real Excel file
        file_path = task.source_file_ref
        try:
            excel_data = self.excel_reader.read(file_path)
        except Exception as e:
            raise TaskError(f"Failed to read excel file {file_path}: {e}")

        # Apply Input Contract
        contract_result = self._apply_contract(excel_data)

        # 2. Build snapshot
        snapshot = RecognitionResultSnapshot(
            task_id=task_id,
            recognized_data={
                "recognized_sheets": excel_data["sheets"],
                "header_mapping": excel_data["header_mapping"],
                "row_data": contract_result["row_data"],
                "issues": [dataclasses.asdict(iss) for iss in contract_result["issues"]],
                "warnings": []
            }
        )
        self.result_repo.save_recognition(snapshot)
        
        # 3. Transition state
        task.task_status = TaskStatus.recognized
        self.task_repo.save(task)
        
        return {
            "status": "recognized", 
            "task_id": task_id, 
            "sheets_found": len(excel_data["sheets"]),
            "issues_count": len(contract_result["issues"])
        }

    def _apply_contract(self, excel_data: Dict[str, Any]) -> Dict[str, Any]:
        result_row_data = {}
        issues = []
        
        found_sheet_types = {} # type -> list of sheet names
        
        for sheet_name, rows in excel_data["row_data"].items():
            s_name_lower = sheet_name.lower()
            
            # Identify sheet type
            matched_config = None
            for sheet_config in self.contract.sheets:
                if any(kw in s_name_lower for kw in sheet_config.keywords):
                    matched_config = sheet_config
                    break
                    
            if not matched_config:
                continue
                
            sheet_type = matched_config.sheet_type
            if sheet_type not in found_sheet_types:
                found_sheet_types[sheet_type] = []
            found_sheet_types[sheet_type].append(sheet_name)
            
        # Check sheet conflicts
        valid_sheet_types = set()
        for sheet_type, sheet_names in found_sheet_types.items():
            if len(sheet_names) > 1:
                # Find the config for this sheet type to check conflict_strategy
                matched_config = next((c for c in self.contract.sheets if c.sheet_type == sheet_type), None)
                strategy = matched_config.conflict_strategy if matched_config else "reject"
                
                if strategy == "reject":
                    issues.append(IssueItem(
                        issue_id=generate_id(),
                        message=f"Multiple sheets mapped to the same type '{sheet_type}': {sheet_names}",
                        evidence={"sheet_type": sheet_type, "conflicting_sheets": sheet_names},
                        expected="1 sheet per type",
                        actual=f"{len(sheet_names)} sheets",
                        details={"sheet_names": sheet_names},
                        source_row=0,
                        severity="critical",
                        category="sheet_conflict",
                        stage="recognition"
                    ))
                else:
                    # e.g., append strategy, allow multiple sheets
                    valid_sheet_types.add(sheet_type)
            else:
                valid_sheet_types.add(sheet_type)

        for sheet_name, rows in excel_data["row_data"].items():
            s_name_lower = sheet_name.lower()
            
            # Identify sheet type
            matched_config = None
            for sheet_config in self.contract.sheets:
                if any(kw in s_name_lower for kw in sheet_config.keywords):
                    matched_config = sheet_config
                    break
                    
            if not matched_config:
                continue
                
            sheet_type = matched_config.sheet_type
            if sheet_type not in valid_sheet_types:
                continue
            
            # Header mapping
            original_headers = excel_data["header_mapping"].get(sheet_name, [])
            header_map = {} # original_header -> standard_name
            unmapped_headers = []
            
            for orig_h in original_headers:
                orig_h_lower = orig_h.lower().strip()
                mapped = False
                for h_config in matched_config.headers:
                    aliases_lower = [a.lower().strip() for a in h_config.aliases]
                    if orig_h_lower == h_config.standard_name.lower().strip() or orig_h_lower in aliases_lower:
                        header_map[orig_h] = h_config.standard_name
                        mapped = True
                        break
                if not mapped:
                    unmapped_headers.append(orig_h)
            
            if unmapped_headers:
                issues.append(IssueItem(
                    issue_id=generate_id(),
                    message=f"Unmapped headers found in sheet '{sheet_name}': {unmapped_headers}",
                    evidence={"sheet": sheet_name, "unmapped_headers": unmapped_headers},
                    expected="All headers mapped",
                    actual=f"{len(unmapped_headers)} unmapped headers",
                    details={"unmapped_headers": unmapped_headers},
                    source_row=0,
                    severity="warning",
                    category="unmapped_header",
                    stage="recognition"
                ))
            
            # Check missing required headers
            found_standard_headers = set(header_map.values())
            for h_config in matched_config.headers:
                if h_config.required and h_config.standard_name not in found_standard_headers:
                    issues.append(IssueItem(
                        issue_id=generate_id(),
                        message=f"Missing required header '{h_config.standard_name}' in sheet '{sheet_name}'.",
                        evidence={"sheet": sheet_name, "missing_header": h_config.standard_name},
                        expected=h_config.standard_name,
                        actual=None,
                        details={"aliases": h_config.aliases},
                        source_row=0,
                        severity="high",
                        category="missing_header",
                        stage="recognition"
                    ))
            
            # Map rows
            mapped_rows = []
            for idx, row_dict in enumerate(rows):
                row_idx = idx + 2 # Excel 1-based, +1 for header
                mapped_row = {"_source_sheet": sheet_name, "_source_row": row_idx}
                
                for orig_k, v in row_dict.items():
                    if orig_k in header_map:
                        mapped_row[header_map[orig_k]] = v
                        
                # Check missing required values
                missing_fields = []
                for h_config in matched_config.headers:
                    if h_config.required:
                        val = mapped_row.get(h_config.standard_name)
                        if val is None or str(val).strip() == "":
                            missing_fields.append(h_config.standard_name)
                    elif h_config.standard_name not in mapped_row:
                        mapped_row[h_config.standard_name] = h_config.default_value
                        
                if missing_fields:
                    issues.append(IssueItem(
                        issue_id=generate_id(),
                        message=f"Missing required fields {missing_fields} in sheet '{sheet_name}' at row {row_idx}.",
                        evidence={"sheet": sheet_name, "row": row_idx, "missing_fields": missing_fields},
                        expected="Value present",
                        actual="Empty",
                        details={"row_data": row_dict},
                        source_row=row_idx,
                        severity="high",
                        category="missing_field",
                        stage="recognition"
                    ))
                
                mapped_rows.append(mapped_row)
                
            result_row_data[sheet_type] = mapped_rows

        # Check missing sheets
        for sheet_config in self.contract.sheets:
            if sheet_config.sheet_type not in found_sheet_types:
                issues.append(IssueItem(
                    issue_id=generate_id(),
                    message=f"Missing required sheet type '{sheet_config.sheet_type}'.",
                    evidence={"missing_sheet": sheet_config.sheet_type},
                    expected=f"Sheet matching {sheet_config.keywords}",
                    actual=None,
                    details={},
                    source_row=0,
                    severity="high",
                    category="missing_sheet",
                    stage="recognition"
                ))

        return {
            "row_data": result_row_data,
            "issues": issues
        }

    def confirm_recognition(self, task_id: str) -> Dict[str, Any]:
        task = self.task_repo.get_by_id(task_id)
        if task.task_status != TaskStatus.recognized:
            raise TaskError("Task must be in recognized state.")
            
        task.task_status = TaskStatus.pending_confirmation
        self.task_repo.save(task)
        
        # Normally wait for user, but we'll assume it's confirmed
        task.task_status = TaskStatus.ready_to_check
        self.task_repo.save(task)
        return {"status": "confirmed and ready_to_check", "task_id": task_id}
