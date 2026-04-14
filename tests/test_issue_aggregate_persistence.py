import pytest
import json
import os
from src.domain.result_model import IssueAggregateSnapshot, IssueItem
from src.infrastructure.repository import ResultRepository, _write_json

@pytest.fixture(autouse=True)
def setup_repo():
    # Clean up before tests
    repo = ResultRepository()
    path = "data/issue_aggregates.json"
    if os.path.exists(path):
        os.remove(path)
    yield repo
    if os.path.exists(path):
        os.remove(path)

def test_save_and_read_single_aggregate(setup_repo):
    repo = setup_repo
    agg = IssueAggregateSnapshot(
        run_id="run-1",
        issues=[
            IssueItem(
                issue_id="issue-1",
                message="test issue",
                evidence={},
                expected="a",
                actual="b",
                details={},
                source_row=1
            )
        ]
    )
    repo.save_issue_aggregate(agg)
    
    loaded = repo.get_issue_aggregate("run-1")
    assert loaded is not None
    assert loaded.run_id == "run-1"
    assert len(loaded.issues) == 1
    assert loaded.issues[0].issue_id == "issue-1"

def test_multiple_runs_persistence(setup_repo):
    repo = setup_repo
    agg1 = IssueAggregateSnapshot(
        run_id="run-1", issues=[]
    )
    agg2 = IssueAggregateSnapshot(
        run_id="run-2", issues=[]
    )
    
    repo.save_issue_aggregate(agg1)
    repo.save_issue_aggregate(agg2)
    
    # Both should be present
    loaded1 = repo.get_issue_aggregate("run-1")
    loaded2 = repo.get_issue_aggregate("run-2")
    
    assert loaded1 is not None
    assert loaded1.run_id == "run-1"
    
    assert loaded2 is not None
    assert loaded2.run_id == "run-2"

def test_backward_compatibility_with_corrupted_data(setup_repo):
    repo = setup_repo
    # Simulate old corrupted data (single run at root)
    corrupted_data = {
        "run_id": "run-old",
        "issues": [],
        "by_device": {},
        "by_rule": {},
        "by_severity": {}
    }
    
    path = "data/issue_aggregates.json"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(corrupted_data, f)
        
    # Should read it properly
    loaded = repo.get_issue_aggregate("run-old")
    assert loaded is not None
    assert loaded.run_id == "run-old"
    
    # Saving a new one should preserve the old one and fix the schema
    agg_new = IssueAggregateSnapshot(
        run_id="run-new", issues=[]
    )
    repo.save_issue_aggregate(agg_new)
    
    loaded_old = repo.get_issue_aggregate("run-old")
    loaded_new = repo.get_issue_aggregate("run-new")
    
    assert loaded_old is not None
    assert loaded_old.run_id == "run-old"
    assert loaded_new is not None
    assert loaded_new.run_id == "run-new"
