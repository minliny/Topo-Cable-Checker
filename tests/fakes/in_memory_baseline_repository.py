from typing import List, Optional, Union, Dict, Any
from src.domain.baseline_model import BaselineProfile
from src.crosscutting.errors.exceptions import ConcurrencyError
import dataclasses

class InMemoryBaselineRepository:
    def __init__(self, initial_data: List[BaselineProfile] = None):
        self._data: Dict[str, dict] = {}
        if initial_data:
            for b in initial_data:
                self._data[b.baseline_id] = dataclasses.asdict(b)

    def get_all(self) -> List[BaselineProfile]:
        return [BaselineProfile(**v) for v in self._data.values()]

    def get_by_id(self, baseline_id: str) -> Optional[BaselineProfile]:
        data = self._data.get(baseline_id)
        if data:
            return BaselineProfile(**data)
        return None

    def save(self, profile: Union[BaselineProfile, Dict[str, Any]], expected_revision: Optional[int] = None):
        baseline_id = profile.get("baseline_id") if isinstance(profile, dict) else profile.baseline_id
        
        db_record = self._data.get(baseline_id)
        current_db_revision = db_record.get("revision", 1) if db_record else 0
        
        if expected_revision is not None:
            if current_db_revision != expected_revision:
                raise ConcurrencyError(
                    f"Baseline {baseline_id} has been modified by another process. "
                    f"Expected revision: {expected_revision}, got: {current_db_revision}"
                )
                
        new_revision = current_db_revision + 1
        
        if isinstance(profile, dict):
            profile["revision"] = new_revision
            self._data[baseline_id] = profile
        else:
            profile.revision = new_revision
            self._data[baseline_id] = dataclasses.asdict(profile)
