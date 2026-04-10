import pytest
import json
import os
import tempfile
from src.application.check_run_services.check_run_service import CheckRunService
from src.application.task_services.task_service import TaskService
from src.application.baseline_services.baseline_service import BaselineService
from src.application.recognition_services.recognition_service import RecognitionService
from src.infrastructure.repository import ResultRepository
from src.crosscutting.errors.exceptions import TaskError

def create_mock_excel(data, filename="mock_data.xlsx"):
    import openpyxl
    filepath = os.path.join(tempfile.gettempdir(), filename)
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    
    for sheet_name, rows in data.items():
        ws = wb.create_sheet(title=sheet_name)
        for r in rows:
            ws.append(r)
    
    wb.save(filepath)
    return filepath

def _create_temp_json(content: dict) -> str:
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        json.dump(content, f)
    return path

@pytest.fixture
def setup_task_and_data():
    # Setup test data
    data = {
        "device": [
            ["Device Name", "Device Type", "Status"],
            ["FW-01", "Firewall", "Offline"], # Will violate external rule
            ["SW-01", "Switch", "Online"]
        ],
        "ports": [
            ["设备名称", "端口名称", "端口状态"],
            ["FW-01", "eth0", "Up"]
        ]
    }
    
    filepath = create_mock_excel(data)
    
    baseline_svc = BaselineService()
    task_svc = TaskService()
    rec_svc = RecognitionService()
    
    baselines = baseline_svc.list_baselines()
    baseline_id = baselines[0].baseline_id
    task_id = task_svc.create_task(baseline_id, filepath)
    
    rec_svc.recognize_data(task_id)
    rec_svc.confirm_recognition(task_id)
    
    yield task_id
    
    if os.path.exists(filepath):
        os.remove(filepath)

def test_check_run_service_executes_external_rule(setup_task_and_data):
    task_id = setup_task_and_data
    
    # 1. Create external rule file
    rule_data = [
        {
            "rule_id": "RE_SF_EXT_01",
            "name": "No Offline Devices",
            "description": "Devices cannot be offline",
            "rule_type": "field_not_equals",
            "parameters": {"target_field": "status", "expected_value": "Offline"},
            "error_message": "Device is offline!",
            "severity": "high",
            "engine_scope": "rule_engine_single_fact",
            "applies_to": ["DeviceFact"]
        }
    ]
    rule_path = _create_temp_json(rule_data)
    
    try:
        run_svc = CheckRunService()
        result_repo = ResultRepository()
        
        # 2. Run checks WITH external rule path
        run_id = run_svc.run_checks(task_id, external_rule_file_path=rule_path)
        
        # 3. Assert external rule was executed and found issue
        agg = result_repo.get_issue_aggregate(run_id)
        issues = agg.issues
        
        ext_issues = [i for i in issues if i.evidence.get("rule_id") == "RE_SF_EXT_01"]
        assert len(ext_issues) == 1
        assert ext_issues[0].evidence["item_data"]["device_name"] == "FW-01"
        assert "Device is offline!" in ext_issues[0].message
        
    finally:
        os.remove(rule_path)

def test_check_run_service_preserves_old_behavior(setup_task_and_data):
    task_id = setup_task_and_data
    run_svc = CheckRunService()
    result_repo = ResultRepository()
    
    # Run checks WITHOUT external rule path
    run_id = run_svc.run_checks(task_id)
    
    agg = result_repo.get_issue_aggregate(run_id)
    issues = agg.issues
    
    # FW-01 should NOT have the external rule violation
    ext_issues = [i for i in issues if i.evidence.get("rule_id") == "RE_SF_EXT_01"]
    assert len(ext_issues) == 0

def test_check_run_service_fails_fast_on_invalid_external_rules(setup_task_and_data):
    task_id = setup_task_and_data
    run_svc = CheckRunService()
    
    # Create invalid rule file (missing parameters)
    rule_data = [
        {
            "rule_id": "RE_SF_EXT_BAD",
            "name": "Bad",
            "description": "Bad",
            "rule_type": "field_equals",
            "parameters": {},
            "error_message": "Bad",
            "engine_scope": "rule_engine_single_fact"
        }
    ]
    rule_path = _create_temp_json(rule_data)
    
    try:
        # Should raise TaskError failing the run
        with pytest.raises(TaskError, match="Failed to assemble external rules"):
            run_svc.run_checks(task_id, external_rule_file_path=rule_path)
    finally:
        os.remove(rule_path)

def test_check_run_service_executes_external_threshold_rule(setup_task_and_data):
    task_id = setup_task_and_data
    
    # 1. Create external threshold rule file
    rule_data = [
        {
            "rule_id": "RE_TH_EXT_01",
            "name": "Too Many Firewalls",
            "description": "Cannot have more than 0 firewalls in this test",
            "rule_type": "threshold",
            "parameters": {
                "metric_type": "count",
                "operator": "lte",
                "expected_value": 0
            },
            "error_message": "Too many firewalls!",
            "severity": "high",
            "engine_scope": "rule_engine_threshold",
            "applies_to": ["DeviceFact"]
        }
    ]
    rule_path = _create_temp_json(rule_data)
    
    try:
        run_svc = CheckRunService()
        result_repo = ResultRepository()
        
        # 2. Run checks WITH external rule path
        run_id = run_svc.run_checks(task_id, external_rule_file_path=rule_path)
        
        # 3. Assert external rule was executed and found issue
        agg = result_repo.get_issue_aggregate(run_id)
        issues = agg.issues
        
        ext_issues = [i for i in issues if i.evidence.get("rule_id") == "RE_TH_EXT_01"]
        assert len(ext_issues) == 1
        assert "Rule RE_TH_EXT_01 (threshold) failed" in ext_issues[0].message
        
    finally:
        os.remove(rule_path)

def test_check_run_service_fails_fast_on_unsupported_scope(setup_task_and_data):
    task_id = setup_task_and_data
    run_svc = CheckRunService()
    
    rule_data = [
        {
            "rule_id": "RE_UNSUPPORTED_01",
            "name": "Unsupported",
            "description": "Unsupported",
            "rule_type": "field_equals",
            "parameters": {},
            "error_message": "Unsupported",
            "engine_scope": "rule_engine_topology",
            "applies_to": ["DeviceFact"]
        }
    ]
    rule_path = _create_temp_json(rule_data)
    
    try:
        with pytest.raises(TaskError, match="Found rules with unsupported engine_scope"):
            run_svc.run_checks(task_id, external_rule_file_path=rule_path)
    finally:
        os.remove(rule_path)
