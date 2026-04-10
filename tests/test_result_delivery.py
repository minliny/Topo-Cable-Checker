# [OPTIONAL_MODULE]
# This module provides optional external-environment integration.
# It is not part of the core port-checking flow.
# Behavior may depend on OS / desktop / local environment setup.

import pytest
import os
from unittest.mock import patch
from src.presentation.result_delivery import ResultDeliveryService

class MockSummary:
    def __init__(self, text):
        self.summary = text

class MockStats:
    def __init__(self, devices, ports):
        self.total_devices = devices
        self.total_ports = ports

class MockIssue:
    def __init__(self, rule_id, severity, device_name, actual_value):
        self.rule_id = rule_id
        self.severity = severity
        self.device_name = device_name
        self.actual_value = actual_value

class MockIssues:
    def __init__(self, issues_list):
        self.issues = issues_list
        self.total_issues = len(issues_list)
        self.by_severity = {}
        for issue in issues_list:
            self.by_severity[issue.severity] = self.by_severity.get(issue.severity, 0) + 1

@pytest.fixture
def delivery_service():
    return ResultDeliveryService()

def test_format_output_markdown(delivery_service):
    issues = MockIssues([
        MockIssue("rule1", "error", "DeviceA", "val1"),
        MockIssue("rule2", "warning", "DeviceB", "val2")
    ])
    
    res = delivery_service.format_output(
        task_id="task-123", 
        run_id="run-456", 
        summary=MockSummary("Test summary"), 
        stats=MockStats(2, 4), 
        issues=issues, 
        max_issues=10, 
        fmt="markdown"
    )
    
    assert "# 检查执行结果" in res
    assert "**任务ID**: task-123" in res
    assert "error: 1" in res
    assert "Test summary" in res
    assert "### 1. [error] rule1" in res
    assert "**设备名称**: DeviceA" in res

def test_format_output_text(delivery_service):
    issues = MockIssues([
        MockIssue("rule1", "error", "DeviceA", "val1")
    ])
    res = delivery_service.format_output(
        task_id="t1", run_id="r1", summary=MockSummary("Sum"), stats=None, issues=issues, fmt="text"
    )
    
    assert "检查执行结果" in res
    assert "# 检查执行结果" not in res
    assert "**任务ID**" not in res
    assert "- 任务ID: t1" in res

def test_format_output_edge_cases(delivery_service):
    # Empty issues, None stats, None summary
    res = delivery_service.format_output("t1", "r1", None, None, None)
    assert "无总览信息" in res
    assert "没有发现问题" in res
    
    # max_issues = 0
    issues = MockIssues([MockIssue("rule1", "error", "DeviceA", "val1")])
    res2 = delivery_service.format_output("t1", "r1", None, None, issues, max_issues=0)
    assert "问题显示被禁用" in res2
    assert "DeviceA" not in res2

    # max_issues < 0
    res3 = delivery_service.format_output("t1", "r1", None, None, issues, max_issues=-5)
    assert "问题显示被禁用" in res3

@patch('src.presentation.result_delivery.copy_to_clipboard')
@patch('src.presentation.result_delivery.open_in_ide')
@patch('src.presentation.result_delivery.create_temp_result_file')
def test_deliver_result_success(mock_create_temp, mock_open_ide, mock_copy, delivery_service):
    mock_copy.return_value = True
    mock_create_temp.return_value = "/tmp/fake.md"
    mock_open_ide.return_value = True
    
    delivery_service.deliver_result("content", copy=True, open_ide=True, fmt="markdown")
    
    mock_copy.assert_called_once_with("content")
    mock_create_temp.assert_called_once_with("content", "md")
    mock_open_ide.assert_called_once_with("/tmp/fake.md")

@patch('src.presentation.result_delivery.copy_to_clipboard')
@patch('src.presentation.result_delivery.open_in_ide')
@patch('src.presentation.result_delivery.create_temp_result_file')
def test_deliver_result_fallback_failures(mock_create_temp, mock_open_ide, mock_copy, delivery_service):
    mock_copy.return_value = False
    mock_create_temp.return_value = "/tmp/fake.txt"
    mock_open_ide.return_value = False
    
    # Should not raise exception
    delivery_service.deliver_result("content", copy=True, open_ide=True, fmt="text")
    
    mock_copy.assert_called_once_with("content")
    mock_create_temp.assert_called_once_with("content", "txt")
    mock_open_ide.assert_called_once_with("/tmp/fake.txt")

@patch('src.presentation.result_delivery.copy_to_clipboard')
@patch('src.presentation.result_delivery.open_in_ide')
@patch('src.presentation.result_delivery.create_temp_result_file')
def test_deliver_result_disabled(mock_create_temp, mock_open_ide, mock_copy, delivery_service):
    delivery_service.deliver_result("content", copy=False, open_ide=False)
    
    mock_copy.assert_not_called()
    mock_create_temp.assert_not_called()
    mock_open_ide.assert_not_called()

def test_temp_file_creation():
    from src.crosscutting.temp_files import create_temp_result_file
    path = create_temp_result_file("hello world", "md")
    assert path != ""
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        assert f.read() == "hello world"
    os.remove(path)
