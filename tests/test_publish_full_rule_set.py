import pytest
from src.application.rule_editor_services.rule_publish_workflow_service import RulePublishWorkflowService
from src.application.rule_editor_services.rule_editor_governance_bridge_service import RuleEditorGovernanceBridgeService
from src.domain.baseline_model import BaselineProfile
from src.infrastructure.repository import BaselineRepository

class FakeRepo(BaselineRepository):
    def __init__(self):
        self._store = {}
    def get_by_id(self, id): return self._store.get(id)
    def save(self, b):
        if isinstance(b, dict): self._store[b["baseline_id"]] = b
        else: self._store[b.baseline_id] = b

def test_publish_accepts_rule_set_payload():
    repo = FakeRepo()
    repo.save(BaselineProfile(
        baseline_id="B001", baseline_version="v1.0",
        recognition_profile={}, naming_profile={}, rule_set={}
    ))
    bridge = RuleEditorGovernanceBridgeService()
    svc = RulePublishWorkflowService(repo, bridge)
    
    # Publish payload is now a full rule_set (the user wants "发布请求体rule_set")
    draft_rule_set = {
        "R1": {"rule_type": "template", "template": "threshold_check", "target_type": "devices", "params": {"metric_type": "count"}, "severity": "warning"},
        "R2": {"rule_type": "template", "template": "group_consistency", "target_type": "devices", "params": {"parameter_key": "P1"}, "severity": "info"}
    }
    
    # We pass the full rule_set as `draft`
    res = svc.publish_draft("B001", draft_rule_set, "Multi-rule publish")
    
    assert res.publish_success is True
    
    b = repo.get_by_id("B001")
    assert "R1" in b.rule_set
    assert "R2" in b.rule_set
    assert b.working_draft is None
