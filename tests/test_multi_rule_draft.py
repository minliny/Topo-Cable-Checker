import pytest
from src.application.rule_editor_services.rule_draft_save_service import RuleDraftSaveService
from src.domain.baseline_model import BaselineProfile
from src.infrastructure.repository import BaselineRepository

class FakeRepo(BaselineRepository):
    def __init__(self):
        self._store = {}
    def get_by_id(self, id): return self._store.get(id)
    def save(self, b):
        if isinstance(b, dict): self._store[b["baseline_id"]] = b
        else: self._store[b.baseline_id] = b

def test_save_multi_rule_draft():
    repo = FakeRepo()
    repo.save(BaselineProfile(baseline_id="B001", baseline_version="v1.0", recognition_profile={}, naming_profile={}, rule_set={}))
    svc = RuleDraftSaveService(repo)
    
    # Save a draft with rule_set wrapper
    draft_payload = {
        "rule_set": {
            "R1": {"rule_type": "template", "template": "threshold_check", "params": {"metric_type": "count"}},
            "R2": {"rule_type": "template", "template": "group_consistency", "params": {"parameter_key": "P1"}}
        },
        "active_rule_id": "R2"
    }
    
    svc.save_draft("B001", draft_payload)
    
    b = repo.get_by_id("B001")
    assert b.working_draft is not None
    assert "rule_set" in b.working_draft
    assert "R1" in b.working_draft["rule_set"]
    assert "R2" in b.working_draft["rule_set"]
    assert b.working_draft["active_rule_id"] == "R2"
    assert "saved_at" in b.working_draft

def test_clear_draft_sets_none():
    repo = FakeRepo()
    b = BaselineProfile(baseline_id="B001", baseline_version="v1.0", recognition_profile={}, naming_profile={}, rule_set={})
    b.working_draft = {"rule_set": {"R1": {}}}
    repo.save(b)
    
    svc = RuleDraftSaveService(repo)
    svc.clear_draft("B001")
    
    saved_b = repo.get_by_id("B001")
    assert saved_b.working_draft is None

def test_load_draft_returns_wrapper():
    repo = FakeRepo()
    b = BaselineProfile(baseline_id="B001", baseline_version="v1.0", recognition_profile={}, naming_profile={}, rule_set={})
    b.working_draft = {"rule_set": {"R1": {}}, "active_rule_id": "R1", "saved_at": "now"}
    repo.save(b)
    
    svc = RuleDraftSaveService(repo)
    res = svc.load_draft("B001")
    
    assert res.has_draft is True
    assert "rule_set" in res.draft_data
    assert "active_rule_id" in res.draft_data
