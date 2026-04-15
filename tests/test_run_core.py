import pytest
import uuid
import os
import tempfile
import openpyxl
from src.application.task_services.task_service import TaskService
from src.application.baseline_services.baseline_service import BaselineService
from src.application.recognition_services.recognition_service import RecognitionService
from src.application.check_run_services.check_run_service import CheckRunService
from src.infrastructure.repository import ResultRepository

def create_mock_excel(data, filename="mock_data.xlsx"):
    filepath = os.path.join(tempfile.gettempdir(), filename)
    wb = openpyxl.Workbook()
    # remove default sheet
    wb.remove(wb.active)
    
    for sheet_name, rows in data.items():
        ws = wb.create_sheet(title=sheet_name)
        for r in rows:
            ws.append(r)
    
    wb.save(filepath)
    return filepath

def test_run_core_recognition_and_normalization_issues():
    # Setup test data
    data = {
        "device": [
            ["Device Name", "Device Type"],
            ["FW-01", "Firewall"],
            ["", "Switch"] # missing device name (recognition issue)
        ],
        "device_dup": [ # Sheet conflict
            ["Device Name", "Device Type"],
            ["FW-02", "Firewall"]
        ],
        "ports": [
            ["设备名称", "端口名称", "端口状态", "Extra Column"], # alias mapping, unmapped header
            ["FW-01", "eth0", "Up", "xyz"]
        ]
        # missing link sheet (recognition issue)
    }
    
    filepath = create_mock_excel(data)
    
    baseline_svc = BaselineService()
    task_svc = TaskService()
    rec_svc = RecognitionService()
    run_svc = CheckRunService()
    result_repo = ResultRepository()
    
    baseline_id = baseline_svc.bootstrap_default_baseline().baseline_id
    task_id = task_svc.create_task(baseline_id, filepath)
    
    rec_svc.recognize_data(task_id)
    rec_svc.confirm_recognition(task_id)
    
    run_id = run_svc.run_checks(task_id)
    
    agg = result_repo.get_issue_aggregate(run_id)
    
    issues = agg.issues
    
    # Assert missing link sheet issue
    missing_sheet_issues = [i for i in issues if i.category == "missing_sheet" and i.stage == "recognition"]
    assert len(missing_sheet_issues) == 1
    assert missing_sheet_issues[0].evidence["missing_sheet"] == "link"
    
    # Assert sheet conflict issue
    conflict_issues = [i for i in issues if i.category == "sheet_conflict" and i.stage == "recognition"]
    assert len(conflict_issues) == 1
    assert "device" in conflict_issues[0].evidence["sheet_type"]
    
    # Assert unmapped header issue
    unmapped_issues = [i for i in issues if i.category == "unmapped_header" and i.stage == "recognition"]
    assert len(unmapped_issues) == 1
    assert "Extra Column" in unmapped_issues[0].evidence["unmapped_headers"]
    
    # Check that devices are skipped because of conflict, ports are still normalized
    stats = result_repo.get_statistics(run_id)
    assert stats.total_devices == 0  # blocked by sheet conflict
    assert stats.total_ports == 1
    
    os.remove(filepath)
