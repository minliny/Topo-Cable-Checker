from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class BaselineProfile:
    baseline_id: str
    baseline_version: str
    recognition_profile: Dict[str, Any]
    naming_profile: Dict[str, Any]
    rule_set: Dict[str, Any]
    parameter_profile: Dict[str, Any]
    threshold_profile: Dict[str, Any]
    baseline_version_snapshot: Dict[str, Any]
