from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

# --- Persistence Payload Boundaries ---
# These type aliases make it explicit that these are raw persistence shapes,
# NOT stable domain contracts. Services should avoid assuming their internal structure
# wherever possible.
RuleSetPayload = Dict[str, Any]
WorkingDraftPayload = Dict[str, Any]
VersionSnapshotPayload = Dict[str, RuleSetPayload]
VersionMetaPayload = Dict[str, Dict[str, Any]]

@dataclass
class BaselineProfile:
    baseline_id: str
    baseline_version: str
    
    # Core Domain Profiles (Currently stored as raw payloads)
    recognition_profile: Dict[str, Any]
    naming_profile: Dict[str, Any]
    parameter_profile: Dict[str, Any] = field(default_factory=dict)
    threshold_profile: Dict[str, Any] = field(default_factory=dict)
    
    # Rule Lifecycle Payloads
    rule_set: RuleSetPayload = field(default_factory=dict)
    baseline_version_snapshot: VersionSnapshotPayload = field(default_factory=dict)
    version_history_meta: VersionMetaPayload = field(default_factory=dict)
    
    # A1-1: Working draft storage — None means no draft, dict means draft exists
    working_draft: Optional[WorkingDraftPayload] = None
    
    revision: int = 1
