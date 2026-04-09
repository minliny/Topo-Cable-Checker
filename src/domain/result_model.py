from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class RecognitionResultSnapshot:
    task_id: str
    recognized_data: Dict[str, Any]

@dataclass
class RunExecutionSnapshot:
    run_id: str
    task_id: str
    status: str

@dataclass
class RunSummaryOverview:
    run_id: str
    summary: str

@dataclass
class RunStatisticsSnapshot:
    run_id: str
    total_devices: int
    total_ports: int
    total_links: int
    device_type_distribution: Dict[str, int]

@dataclass
class IssueItem:
    issue_id: str
    message: str
    evidence: Dict[str, Any]
    expected: Any
    actual: Any
    details: Dict[str, Any]
    source_row: int
    severity: str = "medium"

@dataclass
class IssueAggregateSnapshot:
    run_id: str
    issues: List[IssueItem]
    by_device: Dict[str, int] = field(default_factory=dict)
    by_rule: Dict[str, int] = field(default_factory=dict)
    by_severity: Dict[str, int] = field(default_factory=dict)

@dataclass
class ReviewContext:
    run_id: str
    device_name: str
    context_data: Dict[str, Any]

@dataclass
class DeviceReviewContext:
    run_id: str
    device_name: str
    related_ports: List[Dict[str, Any]]
    connected_devices: List[str]
    related_links: List[Dict[str, Any]]
    related_issues: List[IssueItem]

@dataclass
class RecheckDiffSnapshot:
    task_id: str
    prev_run_id: str
    curr_run_id: str
    diff_data: Dict[str, Any]

@dataclass
class ExportArtifact:
    run_id: str
    format: str
    data: bytes
