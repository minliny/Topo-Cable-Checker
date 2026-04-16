from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
import copy
import datetime
from src.domain.interfaces import IBaselineRepository
from src.application.rule_editor_services.rule_editor_mvp_service import RuleDraftView
from src.domain.baseline_model import RuleSetPayload


# ==========================================
# B1: Deep Diff — Recursive comparison engine
# ==========================================

@dataclass
class DeepDiffChange:
    """B1: Represents a single field-level change with full path."""
    field_path: str          # Dot-separated path, e.g. "params.threshold"
    old_value: Any
    new_value: Any


def deep_diff(old_obj: Any, new_obj: Any, path: str = "") -> List[DeepDiffChange]:
    """
    B1: Recursively compare two objects and return a list of DeepDiffChange items.
    
    - For dicts: recurse into each key, detect added/removed keys
    - For lists: compare by index position, detect length changes
    - For scalars: direct equality check
    
    Returns a flat list of changes with full dot-path notation.
    """
    changes: List[DeepDiffChange] = []
    
    # Same reference or equal values → no change
    if old_obj is new_obj:
        return changes
    
    # Type mismatch → whole value changed
    if type(old_obj) != type(new_obj):
        changes.append(DeepDiffChange(
            field_path=path or "(root)",
            old_value=old_obj,
            new_value=new_obj
        ))
        return changes
    
    # Both are dicts → recurse per key
    if isinstance(old_obj, dict):
        all_keys = set(old_obj.keys()) | set(new_obj.keys())
        for key in sorted(all_keys, key=str):
            child_path = f"{path}.{key}" if path else str(key)
            if key not in old_obj:
                # Key added
                changes.append(DeepDiffChange(
                    field_path=child_path,
                    old_value=None,
                    new_value=new_obj[key]
                ))
            elif key not in new_obj:
                # Key removed
                changes.append(DeepDiffChange(
                    field_path=child_path,
                    old_value=old_obj[key],
                    new_value=None
                ))
            else:
                # Key exists in both → recurse
                changes.extend(deep_diff(old_obj[key], new_obj[key], child_path))
        return changes
    
    # Both are lists → compare by index
    if isinstance(old_obj, list):
        max_len = max(len(old_obj), len(new_obj))
        for i in range(max_len):
            child_path = f"{path}[{i}]"
            if i >= len(old_obj):
                # Item added
                changes.append(DeepDiffChange(
                    field_path=child_path,
                    old_value=None,
                    new_value=new_obj[i]
                ))
            elif i >= len(new_obj):
                # Item removed
                changes.append(DeepDiffChange(
                    field_path=child_path,
                    old_value=old_obj[i],
                    new_value=None
                ))
            else:
                # Item exists in both → recurse
                changes.extend(deep_diff(old_obj[i], new_obj[i], child_path))
        return changes
    
    # Scalars → direct comparison
    if old_obj != new_obj:
        changes.append(DeepDiffChange(
            field_path=path or "(root)",
            old_value=old_obj,
            new_value=new_obj
        ))
    
    return changes

@dataclass
class BaselineVersionListItemView:
    version: str
    created_at: str
    rule_count: int
    is_current: bool

@dataclass
class BaselineDiffRuleChangeView:
    rule_id: str
    change_type: str  # "added", "removed", "modified"
    changed_fields: List[str]
    before: Optional[Dict[str, Any]]
    after: Optional[Dict[str, Any]]
    deep_changes: Optional[List[DeepDiffChange]] = None  # B1: Full recursive diff details

@dataclass
class BaselineDiffView:
    baseline_id: str
    from_version: str
    to_version: str
    added_rules: List[BaselineDiffRuleChangeView]
    removed_rules: List[BaselineDiffRuleChangeView]
    modified_rules: List[BaselineDiffRuleChangeView]
    summary_text: str

@dataclass
class BaselineRollbackResult:
    rollback_success: bool
    rollback_target_version: str
    rollback_new_version: str
    errors: List[str]

class RuleBaselineHistoryService:
    def __init__(self, repo: IBaselineRepository):
        self.repo = repo

    def _get_rule_set_for_version(self, baseline: Any, version: str) -> Optional[RuleSetPayload]:
        current_version = getattr(baseline, "baseline_version", "v1.0")
        snapshots = getattr(baseline, "baseline_version_snapshot", {})
        current_rule_set = getattr(baseline, "rule_set", {})
        working_draft = getattr(baseline, "working_draft", None)

        if version == "draft":
            draft_rule_set = copy.deepcopy(current_rule_set)
            if not working_draft:
                return draft_rule_set

            draft_rule_id = working_draft.get("rule_id") if isinstance(working_draft, dict) else None
            if not draft_rule_id:
                return draft_rule_set

            draft_view = RuleDraftView(
                rule_id=draft_rule_id,
                rule_type=working_draft.get("rule_type", "threshold"),
                target_type=working_draft.get("target_type", "devices"),
                severity=working_draft.get("severity", "warning"),
                params=working_draft.get("params", {}) or {},
                validation_result=None,
            )
            draft_rule_set[draft_rule_id] = draft_view.to_rule_def()
            return draft_rule_set

        if version == current_version:
            return copy.deepcopy(current_rule_set)
            
        if version in snapshots:
            return copy.deepcopy(snapshots[version])
            
        return None  # B2: Version not found → None (distinguish from empty rule_set {})

    def list_baseline_versions(self, baseline_id: str) -> List[BaselineVersionListItemView]:
        baseline = self.repo.get_by_id(baseline_id)
        if not baseline:
            return []

        current_version = getattr(baseline, "baseline_version", "v1.0")
        snapshots = getattr(baseline, "baseline_version_snapshot", {})
        current_rule_set = getattr(baseline, "rule_set", {})

        versions = []
        for ver, rule_set in snapshots.items():
            versions.append(BaselineVersionListItemView(
                version=ver,
                created_at="past",  # Ideally read from metadata if available
                rule_count=len(rule_set),
                is_current=False
            ))
            
        versions.append(BaselineVersionListItemView(
            version=current_version,
            created_at="current",
            rule_count=len(current_rule_set),
            is_current=True
        ))
        
        # Sort versions simply by version string assuming v1.x format
        return sorted(versions, key=lambda x: x.version, reverse=True)

    def get_baseline_version(self, baseline_id: str, version: str) -> Optional[RuleSetPayload]:
        baseline = self.repo.get_by_id(baseline_id)
        if not baseline:
            return None
        return self._get_rule_set_for_version(baseline, version)

    def diff_versions(self, baseline_id: str, from_version: str, to_version: str) -> Optional[BaselineDiffView]:
        baseline = self.repo.get_by_id(baseline_id)
        if not baseline:
            return None
            
        rules_from = self._get_rule_set_for_version(baseline, from_version)
        rules_to = self._get_rule_set_for_version(baseline, to_version)
        
        if rules_from is None or rules_to is None:
            return None
            
        added = []
        removed = []
        modified = []
        
        for rule_id, rule_def_to in rules_to.items():
            if rule_id not in rules_from:
                added.append(BaselineDiffRuleChangeView(
                    rule_id=rule_id, change_type="added", changed_fields=[], before=None, after=rule_def_to
                ))
            else:
                rule_def_from = rules_from[rule_id]
                
                # B1: Use deep_diff for recursive comparison instead of shallow key compare
                diff_changes = deep_diff(rule_def_from, rule_def_to)
                
                if diff_changes:
                    # Extract top-level changed field names for backward compatibility
                    top_level_fields = sorted(set(
                        c.field_path.split(".")[0].split("[")[0] 
                        for c in diff_changes
                    ))
                    modified.append(BaselineDiffRuleChangeView(
                        rule_id=rule_id, 
                        change_type="modified", 
                        changed_fields=top_level_fields, 
                        before=rule_def_from, 
                        after=rule_def_to,
                        deep_changes=diff_changes  # B1: full recursive change details
                    ))
                    
        for rule_id, rule_def_from in rules_from.items():
            if rule_id not in rules_to:
                removed.append(BaselineDiffRuleChangeView(
                    rule_id=rule_id, change_type="removed", changed_fields=[], before=rule_def_from, after=None
                ))
                
        summary_text = f"Diff from {from_version} to {to_version}: {len(added)} added, {len(removed)} removed, {len(modified)} modified."

        return BaselineDiffView(
            baseline_id=baseline_id,
            from_version=from_version,
            to_version=to_version,
            added_rules=added,
            removed_rules=removed,
            modified_rules=modified,
            summary_text=summary_text
        )

    def rollback_to_version(self, baseline_id: str, target_version: str, reason: str = "") -> BaselineRollbackResult:
        baseline = self.repo.get_by_id(baseline_id)
        if not baseline:
            return BaselineRollbackResult(False, target_version, "", [f"Baseline {baseline_id} not found."])
            
        target_rule_set = self._get_rule_set_for_version(baseline, target_version)
        # B2: Use "is None" instead of "not" — empty dict {} is a valid rule_set (0 rules)
        if target_rule_set is None and target_version != "v0.0":
            return BaselineRollbackResult(False, target_version, "", [f"Version {target_version} not found in history."])

        # Prepare for version bump
        current_version = getattr(baseline, "baseline_version", "v1.0")
        old_rule_set = getattr(baseline, "rule_set", {})
        snapshots = getattr(baseline, "baseline_version_snapshot", {})

        if not snapshots:
            snapshots = {}

        # Snapshot current state before rollback
        snapshots[current_version] = copy.deepcopy(old_rule_set)

        # Bump version
        try:
            major, minor = current_version.lstrip("v").split(".")
            new_version = f"v{major}.{int(minor) + 1}"
        except Exception:
            new_version = f"{current_version}_rollback"

        # Apply target rule set to current
        baseline.rule_set = copy.deepcopy(target_rule_set)
        baseline.baseline_version = new_version
        baseline.baseline_version_snapshot = snapshots

        self.repo.save(baseline)

        return BaselineRollbackResult(
            rollback_success=True,
            rollback_target_version=target_version,
            rollback_new_version=new_version,
            errors=[]
        )
