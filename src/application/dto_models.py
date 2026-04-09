from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class TaskSummaryDTO:
    task_id: str
    task_name: str
    task_status: str
    baseline_version: str
    latest_run_id: Optional[str]
    created_at: str

@dataclass
class RecognitionSummaryDTO:
    recognition_id: str
    recognized_sheets: List[str]
    header_mapping_summary: Dict[str, List[str]]
    warnings: List[str]
    errors: List[str]
    confirmation_status: str

@dataclass
class RunOverviewDTO:
    run_id: str
    overall_passed: bool
    overall_risk_level: str
    total_issue_count: int
    error_count: int
    warning_count: int
    info_count: int
    affected_device_count: int
    summary_message: str

@dataclass
class IssueListItemDTO:
    issue_id: str
    severity: str
    rule_id: str
    rule_name: str
    device_name: str
    port_name: str
    message: str
    issue_status: str
    category: str

@dataclass
class IssueListResultDTO:
    items: List[IssueListItemDTO]
    before_count: int
    after_count: int

@dataclass
class DeviceReviewDTO:
    device_name: str
    related_ports: List[Dict[str, Any]]
    connected_devices: List[str]
    related_links: List[Dict[str, Any]]
    related_issues: List[IssueListItemDTO]

@dataclass
class RecheckDiffDTO:
    diff_id: str
    new_issue_count: int
    resolved_issue_count: int
    persistent_issue_count: int
    changed_issue_count: int
    risk_trend_summary: Dict[str, Any]

@dataclass
class ExportArtifactDTO:
    run_id: str
    format: str
    filename: str
    download_url: str

@dataclass
class RuleDefinitionDTO:
    rule_id: str
    rule_type: str
    language_version: str
    target_type: str
    source_form: str
    severity: str
    enabled: bool
    baseline_version: str
    raw_definition: Dict[str, Any]

@dataclass
class CompiledRuleDTO:
    rule_id: str
    compiled_executor: str
    compiled_type: str
    scope_selector: Dict[str, Any]
    parameter_source: str
    threshold_source: str
    compiled_config: Dict[str, Any]

@dataclass
class CompileErrorDTO:
    rule_id: str
    error_type: str
    message: str
    language_version: str

@dataclass
class TemplateRegistryDTO:
    template_name: str
    target_executor: str
    supported_params: List[str]
    validation_rules: List[str]
