from src.infrastructure.repository import BaselineRepository
from src.domain.baseline_model import BaselineProfile
from typing import List

class BaselineService:
    def __init__(self):
        self.repo = BaselineRepository()
        
    def list_baselines(self) -> List[BaselineProfile]:
        baselines = self.repo.get_all()
        if not baselines:
            # Create a default dummy baseline for demonstration
            profile = BaselineProfile(
                baseline_id="B001",
                baseline_version="v1.0",
                recognition_profile={"strategy": "excel_basic"},
                naming_profile={"strategy": "snake_case"},
                parameter_profile={
                    "P1": {
                        "group_key": "device_type",
                        "comparison_field": "status"
                    }
                },
                threshold_profile={
                    "T1": {
                        "operator": "between",
                        "min_value": 2,
                        "max_value": 10
                    },
                    "T2": {
                        "operator": "gte",
                        "value": 2
                    }
                },
                rule_set={
                    "R1_scoped": {
                        "executor": "group_consistency",
                        "scope_selector": {
                            "target_type": "devices",
                            "device_type": "Switch"
                        },
                        "parameter_key": "P1",
                        "severity": "warning"
                    },
                    "R2_threshold_count": {
                        "executor": "threshold",
                        "scope_selector": {
                            "target_type": "devices"
                        },
                        "metric_type": "count",
                        "threshold_key": "T1",
                        "severity": "error"
                    },
                    "R3_threshold_distinct": {
                        "executor": "threshold",
                        "scope_selector": {
                            "target_type": "devices"
                        },
                        "metric_type": "distinct_count",
                        "metric_field": "device_type",
                        "threshold_key": "T2",
                        "severity": "error"
                    }
                },
                baseline_version_snapshot={"B001": "v1.0"}
            )
            self.repo.save(profile)
            return [profile]
        return baselines
        
    def get_baseline(self, baseline_id: str) -> BaselineProfile:
        return self.repo.get_by_id(baseline_id)
