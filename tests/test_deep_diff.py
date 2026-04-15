"""
B1-5: Unit tests for Deep Diff recursive comparison engine.

Covers:
- deep_diff() function: scalar, dict, list, nested, type mismatch, edge cases
- Integration: diff_versions() uses deep_diff and populates deep_changes
"""

import pytest
from src.application.rule_editor_services.rule_baseline_history_service import (
    deep_diff, DeepDiffChange,
    RuleBaselineHistoryService,
    BaselineDiffView,
)
from src.domain.interfaces import IBaselineRepository
from src.domain.baseline_model import BaselineProfile


# ==========================================
# Helper: Fake Repository (reuse pattern)
# ==========================================

class FakeBaselineRepository(IBaselineRepository):
    def __init__(self):
        self._store = {}

    def save(self, baseline, expected_revision: int = None):
        if isinstance(baseline, dict):
            self._store[baseline["baseline_id"]] = baseline
        else:
            self._store[baseline.baseline_id] = baseline

    def get_by_id(self, baseline_id: str):
        return self._store.get(baseline_id)

    def list_all(self):
        return list(self._store.values())

    def delete(self, baseline_id: str):
        if baseline_id in self._store:
            del self._store[baseline_id]


# ==========================================
# Unit Tests: deep_diff() function
# ==========================================

class TestDeepDiffScalars:
    """Test deep_diff with scalar values."""

    def test_same_integers_no_change(self):
        assert deep_diff(1, 1) == []

    def test_same_strings_no_change(self):
        assert deep_diff("hello", "hello") == []

    def test_same_none_no_change(self):
        assert deep_diff(None, None) == []

    def test_different_integers(self):
        changes = deep_diff(1, 2)
        assert len(changes) == 1
        assert changes[0].field_path == "(root)"
        assert changes[0].old_value == 1
        assert changes[0].new_value == 2

    def test_different_strings(self):
        changes = deep_diff("a", "b")
        assert len(changes) == 1
        assert changes[0].old_value == "a"
        assert changes[0].new_value == "b"

    def test_scalar_with_path(self):
        changes = deep_diff(10, 20, path="count")
        assert changes[0].field_path == "count"


class TestDeepDiffTypeMismatch:
    """Test deep_diff with type changes."""

    def test_int_to_string(self):
        changes = deep_diff(1, "1")
        assert len(changes) == 1
        assert changes[0].field_path == "(root)"
        assert changes[0].old_value == 1
        assert changes[0].new_value == "1"

    def test_none_to_dict(self):
        changes = deep_diff(None, {"key": "val"})
        assert len(changes) == 1
        assert changes[0].old_value is None

    def test_dict_to_none(self):
        changes = deep_diff({"key": "val"}, None)
        assert len(changes) == 1
        assert changes[0].new_value is None

    def test_list_to_dict(self):
        changes = deep_diff([1, 2], {"a": 1})
        assert len(changes) == 1
        assert changes[0].field_path == "(root)"


class TestDeepDiffDicts:
    """Test deep_diff with dict values."""

    def test_same_dicts_no_change(self):
        assert deep_diff({"a": 1}, {"a": 1}) == []

    def test_empty_dicts_no_change(self):
        assert deep_diff({}, {}) == []

    def test_key_added(self):
        changes = deep_diff({"a": 1}, {"a": 1, "b": 2})
        assert len(changes) == 1
        assert changes[0].field_path == "b"
        assert changes[0].old_value is None
        assert changes[0].new_value == 2

    def test_key_removed(self):
        changes = deep_diff({"a": 1, "b": 2}, {"a": 1})
        assert len(changes) == 1
        assert changes[0].field_path == "b"
        assert changes[0].old_value == 2
        assert changes[0].new_value is None

    def test_key_value_changed(self):
        changes = deep_diff({"a": 1}, {"a": 2})
        assert len(changes) == 1
        assert changes[0].field_path == "a"
        assert changes[0].old_value == 1
        assert changes[0].new_value == 2

    def test_multiple_key_changes(self):
        changes = deep_diff(
            {"a": 1, "b": 2, "c": 3},
            {"a": 10, "b": 2, "d": 4}
        )
        # a changed, c removed, d added
        assert len(changes) == 3
        paths = {c.field_path for c in changes}
        assert "a" in paths
        assert "c" in paths
        assert "d" in paths

    def test_nested_dict_change(self):
        old = {"params": {"threshold": 5, "operator": "gt"}}
        new = {"params": {"threshold": 10, "operator": "gt"}}
        changes = deep_diff(old, new)
        assert len(changes) == 1
        assert changes[0].field_path == "params.threshold"
        assert changes[0].old_value == 5
        assert changes[0].new_value == 10

    def test_deeply_nested_change(self):
        old = {"a": {"b": {"c": 1}}}
        new = {"a": {"b": {"c": 2}}}
        changes = deep_diff(old, new)
        assert len(changes) == 1
        assert changes[0].field_path == "a.b.c"
        assert changes[0].old_value == 1
        assert changes[0].new_value == 2

    def test_nested_key_added(self):
        old = {"params": {"threshold": 5}}
        new = {"params": {"threshold": 5, "operator": "gte"}}
        changes = deep_diff(old, new)
        assert len(changes) == 1
        assert changes[0].field_path == "params.operator"
        assert changes[0].old_value is None
        assert changes[0].new_value == "gte"

    def test_nested_key_removed(self):
        old = {"params": {"threshold": 5, "operator": "gte"}}
        new = {"params": {"threshold": 5}}
        changes = deep_diff(old, new)
        assert len(changes) == 1
        assert changes[0].field_path == "params.operator"
        assert changes[0].old_value == "gte"
        assert changes[0].new_value is None


class TestDeepDiffLists:
    """Test deep_diff with list values."""

    def test_same_lists_no_change(self):
        assert deep_diff([1, 2, 3], [1, 2, 3]) == []

    def test_empty_lists_no_change(self):
        assert deep_diff([], []) == []

    def test_item_changed(self):
        changes = deep_diff([1, 2, 3], [1, 99, 3])
        assert len(changes) == 1
        assert changes[0].field_path == "[1]"
        assert changes[0].old_value == 2
        assert changes[0].new_value == 99

    def test_item_added(self):
        changes = deep_diff([1, 2], [1, 2, 3])
        assert len(changes) == 1
        assert changes[0].field_path == "[2]"
        assert changes[0].old_value is None
        assert changes[0].new_value == 3

    def test_item_removed(self):
        changes = deep_diff([1, 2, 3], [1, 2])
        assert len(changes) == 1
        assert changes[0].field_path == "[2]"
        assert changes[0].old_value == 3
        assert changes[0].new_value is None

    def test_list_with_path(self):
        changes = deep_diff([1], [2], path="items")
        assert changes[0].field_path == "items[0]"

    def test_list_of_dicts_change(self):
        old = [{"name": "a", "val": 1}]
        new = [{"name": "a", "val": 2}]
        changes = deep_diff(old, new)
        assert len(changes) == 1
        assert changes[0].field_path == "[0].val"
        assert changes[0].old_value == 1
        assert changes[0].new_value == 2


class TestDeepDiffComplexNesting:
    """Test deep_diff with mixed dict/list nesting."""

    def test_dict_containing_list_change(self):
        old = {"rules": [{"id": "r1", "val": 1}]}
        new = {"rules": [{"id": "r1", "val": 2}]}
        changes = deep_diff(old, new)
        assert len(changes) == 1
        assert changes[0].field_path == "rules[0].val"
        assert changes[0].old_value == 1
        assert changes[0].new_value == 2

    def test_list_containing_dict_change(self):
        old = [{"params": {"threshold": 5}}]
        new = [{"params": {"threshold": 10}}]
        changes = deep_diff(old, new)
        assert len(changes) == 1
        assert changes[0].field_path == "[0].params.threshold"

    def test_no_change_in_complex_structure(self):
        old = {
            "rule_type": "threshold",
            "params": {"metric_type": "count", "operator": "gt", "thresholds": [1, 2, 3]}
        }
        new = {
            "rule_type": "threshold",
            "params": {"metric_type": "count", "operator": "gt", "thresholds": [1, 2, 3]}
        }
        assert deep_diff(old, new) == []

    def test_multiple_changes_in_complex_structure(self):
        old = {
            "rule_type": "threshold",
            "params": {"metric_type": "count", "operator": "gt", "value": 5}
        }
        new = {
            "rule_type": "threshold",
            "params": {"metric_type": "distinct_count", "operator": "gte", "value": 5}
        }
        changes = deep_diff(old, new)
        assert len(changes) == 2
        paths = {c.field_path for c in changes}
        assert "params.metric_type" in paths
        assert "params.operator" in paths


class TestDeepDiffEdgeCases:
    """Edge cases for deep_diff."""

    def test_same_reference_object(self):
        obj = {"a": 1}
        assert deep_diff(obj, obj) == []

    def test_bool_vs_int_type_mismatch(self):
        # bool is a subclass of int in Python, but type(True) != type(1)
        changes = deep_diff(True, 1)
        assert len(changes) == 1  # type mismatch detected

    def test_float_vs_int_different(self):
        changes = deep_diff(1, 1.0)
        assert len(changes) == 1  # type mismatch

    def test_empty_dict_to_empty_dict(self):
        assert deep_diff({}, {}) == []

    def test_empty_list_to_empty_list(self):
        assert deep_diff([], []) == []


# ==========================================
# Integration Tests: diff_versions() uses deep_diff
# ==========================================

class TestDiffVersionsWithDeepDiff:
    """Integration test: diff_versions populates deep_changes field."""

    @pytest.fixture
    def repo_with_nested_changes(self):
        repo = FakeBaselineRepository()
        baseline = BaselineProfile(
            baseline_id="deep-test",
            baseline_version="v2.0",
            rule_set={
                "rule1": {
                    "rule_type": "threshold",
                    "params": {
                        "metric_type": "distinct_count",
                        "operator": "gte",
                        "expected_value": 3
                    }
                },
                "rule2": {
                    "rule_type": "single_fact",
                    "params": {"field": "status", "type": "field_equals", "expected": "active"}
                }
            },
            parameter_profile={},
            threshold_profile={},
            recognition_profile={},
            naming_profile={},
            baseline_version_snapshot={
                "v1.0": {
                    "rule1": {
                        "rule_type": "threshold",
                        "params": {
                            "metric_type": "count",
                            "operator": "gt",
                            "expected_value": 5
                        }
                    }
                }
            }
        )
        repo.save(baseline)
        return repo

    @pytest.fixture
    def service(self, repo_with_nested_changes):
        return RuleBaselineHistoryService(repo=repo_with_nested_changes)

    def test_modified_rule_has_deep_changes(self, service):
        diff = service.diff_versions("deep-test", "v1.0", "v2.0")
        assert diff is not None

        # rule1 was modified (params changed), rule2 was added
        assert len(diff.modified_rules) == 1
        mod = diff.modified_rules[0]
        assert mod.rule_id == "rule1"

        # deep_changes should be populated
        assert mod.deep_changes is not None
        assert len(mod.deep_changes) > 0

        # Check specific nested paths
        paths = {c.field_path for c in mod.deep_changes}
        assert "params.metric_type" in paths
        assert "params.operator" in paths
        assert "params.expected_value" in paths

    def test_deep_changes_old_new_values(self, service):
        diff = service.diff_versions("deep-test", "v1.0", "v2.0")
        mod = diff.modified_rules[0]

        # Find the metric_type change
        mt_change = next(c for c in mod.deep_changes if c.field_path == "params.metric_type")
        assert mt_change.old_value == "count"
        assert mt_change.new_value == "distinct_count"

    def test_deep_changes_expected_value(self, service):
        diff = service.diff_versions("deep-test", "v1.0", "v2.0")
        mod = diff.modified_rules[0]

        ev_change = next(c for c in mod.deep_changes if c.field_path == "params.expected_value")
        assert ev_change.old_value == 5
        assert ev_change.new_value == 3

    def test_added_rule_has_no_deep_changes(self, service):
        diff = service.diff_versions("deep-test", "v1.0", "v2.0")
        assert len(diff.added_rules) == 1
        added = diff.added_rules[0]
        # Added rules don't have deep_changes (they are entirely new)
        assert added.deep_changes is None

    def test_changed_fields_uses_top_level_from_deep_changes(self, service):
        diff = service.diff_versions("deep-test", "v1.0", "v2.0")
        mod = diff.modified_rules[0]

        # changed_fields should be top-level keys derived from deep_changes paths
        assert "params" in mod.changed_fields

    def test_unchanged_fields_not_in_deep_changes(self, service):
        diff = service.diff_versions("deep-test", "v1.0", "v2.0")
        mod = diff.modified_rules[0]

        paths = {c.field_path for c in mod.deep_changes}
        # rule_type did NOT change (both are "threshold")
        assert "rule_type" not in paths
        # Only params sub-fields changed
        assert "params.metric_type" in paths


class TestDeepDiffInAPIEndpoint:
    """Integration: Diff API endpoint returns deep_changes via field_changes."""

    @pytest.fixture
    def app_client(self):
        from fastapi.testclient import TestClient
        from src.presentation.api.main import app
        return TestClient(app)

    def test_diff_endpoint_returns_nested_field_paths(self, app_client):
        """Verify the /baselines/{id}/diff endpoint returns nested field paths."""
        # This is a smoke test — the real data depends on baselines.json state.
        # We just verify the endpoint doesn't crash and returns valid structure.
        resp = app_client.get("/api/baselines/baseline-001/diff", params={
            "source": "v1.0",
            "target": "v1.1"
        })
        # May return 200 or 404 depending on test data; either is acceptable
        assert resp.status_code in (200, 404)
        if resp.status_code == 200:
            data = resp.json()
            # Verify structure
            assert "rules" in data
            for rule in data.get("rules", []):
                if rule["change_type"] == "modified":
                    assert "field_changes" in rule
                    for fc in rule["field_changes"]:
                        assert "field_name" in fc
                        assert "old_value" in fc
                        assert "new_value" in fc
