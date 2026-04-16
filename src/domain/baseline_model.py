from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

RuleSetPayload = Dict[str, Any]
WorkingDraftPayload = Dict[str, Any]
VersionSnapshotPayload = Dict[str, RuleSetPayload]
VersionMetaPayload = Dict[str, Dict[str, Any]]

@dataclass
class BaselineProfile:
    baseline_id: str
    baseline_version: str
    recognition_profile: Dict[str, Any]
    naming_profile: Dict[str, Any]
    parameter_profile: Dict[str, Any] = field(default_factory=dict)
    threshold_profile: Dict[str, Any] = field(default_factory=dict)
    rule_set: RuleSetPayload = field(default_factory=dict)
    baseline_version_snapshot: VersionSnapshotPayload = field(default_factory=dict)
    version_history_meta: VersionMetaPayload = field(default_factory=dict)
    working_draft: Optional[WorkingDraftPayload] = None
    revision: int = 1
