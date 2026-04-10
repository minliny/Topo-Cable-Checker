from typing import Dict, Any, Optional

class ExecutionContext:
    def __init__(
        self,
        parameter_profile: Optional[Dict[str, Any]] = None,
        threshold_profile: Optional[Dict[str, Any]] = None,
        runtime_flags: Optional[Dict[str, Any]] = None
    ):
        self.parameter_profile = parameter_profile or {}
        self.threshold_profile = threshold_profile or {}
        self.runtime_flags = runtime_flags or {}
