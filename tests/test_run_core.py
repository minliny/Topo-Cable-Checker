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
        "ports": [
            ["设备名称", "端口名称", "端口状态"], # alias mapping
            ["FW-01", "eth0", "Up"]
        ]
        # missing link sheet (recognition issue)
    }
    
    filepath = create_mock_excel(data)
    
    baseline_svc = BaselineService()
    task_svc = TaskService()
    rec_svc = RecognitionService()
    run_svc = CheckRunService()
    result_repo = ResultRepository()
    
    baselines = baseline_svc.list_baselines()
    baseline_id = baselines[0].baseline_id
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
    
    # Assert missing required field issue (FW-01 device name empty)
    missing_field_issues = [i for i in issues if i.category == "missing_field" and i.stage == "recognition"]
    assert len(missing_field_issues) == 1
    assert "device_name" in missing_field_issues[0].evidence["missing_fields"]
    
    # Check that devices and ports are still normalized for valid rows
    stats = result_repo.get_statistics(run_id)
    assert stats.total_devices == 1
    assert stats.total_ports == 1
    
    os.remove(filepath)
