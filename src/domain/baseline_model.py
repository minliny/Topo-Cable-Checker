from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class BaselineProfile:
    baseline_id: str
    baseline_version: str
    recognition_profile: Dict[str, Any]
    naming_profile: Dict[str, Any]
    parameter_profile: Dict[str, Any] = field(default_factory=dict)
    threshold_profile: Dict[str, Any] = field(default_factory=dict)
    rule_set: Dict[str, Any] = field(default_factory=dict)
    baseline_version_snapshot: Dict[str, Any] = field(default_factory=dict)
    
    # Extensions for API integration (UI History & Auditing)
    version_history_meta: Dict[str, Dict[str, Any]] = field(default_factory=dict) 
    # e.g. {"v1.0": {"published_at": "...", "publisher": "admin", "summary": "...", "parent_version": "v0.9"}}
