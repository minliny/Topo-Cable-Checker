from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import copy
import datetime
from src.domain.interfaces import IBaselineRepository
from src.infrastructure.repository import BaselineRepository

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
    def __init__(self, repo: Optional[IBaselineRepository] = None):
        self.repo = repo or BaselineRepository()

    def _get_rule_set_for_version(self, baseline: Any, version: str) -> Dict[str, Any]:
        if isinstance(baseline, dict):
            current_version = baseline.get("baseline_version", "v1.0")
            snapshots = baseline.get("baseline_version_snapshot", {})
            current_rule_set = baseline.get("rule_set", {})
        else:
            current_version = getattr(baseline, "baseline_version", "v1.0")
            snapshots = getattr(baseline, "baseline_version_snapshot", {})
            current_rule_set = getattr(baseline, "rule_set", {})

        if version == current_version:
            return copy.deepcopy(current_rule_set)
            
        if version in snapshots:
            return copy.deepcopy(snapshots[version])
            
        return {}

    def list_baseline_versions(self, baseline_id: str) -> List[BaselineVersionListItemView]:
        baseline = self.repo.get_by_id(baseline_id)
        if not baseline:
            return []

        if isinstance(baseline, dict):
            current_version = baseline.get("baseline_version", "v1.0")
            snapshots = baseline.get("baseline_version_snapshot", {})
            current_rule_set = baseline.get("rule_set", {})
        else:
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

    def get_baseline_version(self, baseline_id: str, version: str) -> Optional[Dict[str, Any]]:
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
        
        if not rules_from and from_version != "v0.0": # Handle edge case
            pass # Or handle not found
            
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
                changed_fields = []
                
                # Basic shallow diff comparison
                for k, v in rule_def_to.items():
                    if rule_def_from.get(k) != v:
                        changed_fields.append(k)
                for k in rule_def_from.keys():
                    if k not in rule_def_to:
                        changed_fields.append(k)
                
                if changed_fields:
                    modified.append(BaselineDiffRuleChangeView(
                        rule_id=rule_id, change_type="modified", changed_fields=changed_fields, before=rule_def_from, after=rule_def_to
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
        if not target_rule_set and target_version != "v0.0":
            return BaselineRollbackResult(False, target_version, "", [f"Version {target_version} not found in history."])

        # Prepare for version bump
        if isinstance(baseline, dict):
            current_version = baseline.get("baseline_version", "v1.0")
            old_rule_set = baseline.get("rule_set", {})
            snapshots = baseline.get("baseline_version_snapshot", {})
        else:
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
        if isinstance(baseline, dict):
            baseline["rule_set"] = copy.deepcopy(target_rule_set)
            baseline["baseline_version"] = new_version
            baseline["baseline_version_snapshot"] = snapshots
        else:
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
