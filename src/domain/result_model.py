from dataclasses import dataclass
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
    stats: Dict[str, Any]

@dataclass
class IssueItem:
    issue_id: str
    message: str
    evidence: Dict[str, Any]
    expected: Any
    actual: Any
    details: Dict[str, Any]
    source_row: int

@dataclass
class IssueAggregateSnapshot:
    run_id: str
    issues: List[IssueItem]

@dataclass
class ReviewContext:
    run_id: str
    device_name: str
    context_data: Dict[str, Any]

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
