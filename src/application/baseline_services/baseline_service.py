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
                rule_set={"R1": {"field": "status", "expected": "active"}},
                parameter_profile={},
                threshold_profile={},
                baseline_version_snapshot={"B001": "v1.0"}
            )
            self.repo.save(profile)
            return [profile]
        return baselines
        
    def get_baseline(self, baseline_id: str) -> BaselineProfile:
        return self.repo.get_by_id(baseline_id)
