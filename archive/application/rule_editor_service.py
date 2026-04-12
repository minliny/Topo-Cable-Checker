from typing import List, Dict, Any, Optional
import copy
from src.application.dto_models import (
    RuleEditorBaselineDTO, 
    RuleEditorDraftDTO, 
    RuleValidationResultDTO, 
    RuleCompilePreviewDTO,
    CompileErrorDTO,
    BaselineVersionDTO,
    BaselineDiffDTO,
    RuleDiffItemDTO
)
from src.domain.interfaces import IBaselineRepository
from src.domain.rule_compiler import RuleCompiler, RuleCompileError, TemplateRegistry
from typing import Tuple

class RuleEditorService:
    def __init__(self, repo: IBaselineRepository = None):
        if repo is None:
            from src.infrastructure.repository import BaselineRepository
            self.repo = repo or BaselineRepository()
        else:
            self.repo = repo
        # Mocking an in-memory draft workspace for the editor
        # Structure: { baseline_id: { rule_id: rule_definition_dict } }
        self._draft_workspace: Dict[str, Dict[str, Any]] = {}

    def _ensure_workspace(self, baseline_id: str):
        if baseline_id not in self._draft_workspace:
            baseline = self.repo.get_by_id(baseline_id)
            if baseline:
                # Deep copy to ensure draft edits don't mutate the baseline directly
                rule_set = getattr(baseline, "rule_set", baseline.get("rule_set", {})) if isinstance(baseline, dict) else baseline.rule_set
                self._draft_workspace[baseline_id] = copy.deepcopy(rule_set)
            else:
                self._draft_workspace[baseline_id] = {}

    def get_editor_baseline(self, baseline_id: str) -> Optional[RuleEditorBaselineDTO]:
        baseline = self.repo.get_by_id(baseline_id)
        if not baseline:
            return None
        
        self._ensure_workspace(baseline_id)
        
        draft_rules = self._draft_workspace[baseline_id]
        published_rules = getattr(baseline, "rule_set", baseline.get("rule_set", {})) if isinstance(baseline, dict) else baseline.rule_set
        baseline_version = getattr(baseline, "baseline_version", baseline.get("baseline_version", "v1.0")) if isinstance(baseline, dict) else baseline.baseline_version
        baseline_name = getattr(baseline, "name", baseline.get("name", f"Baseline {baseline_id}")) if isinstance(baseline, dict) else getattr(baseline, "name", f"Baseline {baseline_id}")
        
        return RuleEditorBaselineDTO(
            baseline_id=baseline_id,
            baseline_name=baseline_name,
            baseline_version=baseline_version,
            baseline_status="editing",
            language_version="v1.0", # Simplified
            draft_rule_count=len(draft_rules),
            published_rule_count=len(published_rules)
        )

    def list_editor_rules(self, baseline_id: str) -> List[RuleEditorDraftDTO]:
        self._ensure_workspace(baseline_id)
        drafts = self._draft_workspace[baseline_id]
        
        dtos = []
        for rule_id, rule_def in drafts.items():
            # Perform a silent compile check to determine compile_status for the list view
            compile_status = "success"
            try:
                RuleCompiler.compile(rule_id, rule_def)
            except RuleCompileError:
                compile_status = "error"
                
            dtos.append(RuleEditorDraftDTO(
                rule_id=rule_id,
                source_form=rule_def.get("rule_type", "native"),
                language_version=rule_def.get("language_version", "v1.0"),
                target_type=rule_def.get("target_type", rule_def.get("scope_selector", {}).get("target_type", "devices")),
                severity=rule_def.get("severity", "medium"),
                enabled=rule_def.get("enabled", True),
                raw_definition=rule_def,
                draft_status="draft",
                is_dirty=True, # Simplified: all items in workspace are considered dirty
                compile_status=compile_status
            ))
        return dtos

    def get_editor_rule(self, baseline_id: str, rule_id: str) -> Optional[RuleEditorDraftDTO]:
        rules = self.list_editor_rules(baseline_id)
        for r in rules:
            if r.rule_id == rule_id:
                return r
        return None

    def validate_rule_draft(self, rule_id: str, rule_definition: Dict[str, Any]) -> RuleValidationResultDTO:
        try:
            RuleCompiler.compile(rule_id, rule_definition)
            return RuleValidationResultDTO(rule_id=rule_id, is_valid=True, compile_errors=[])
        except RuleCompileError as e:
            error_dto = CompileErrorDTO(
                rule_id=rule_id,
                error_type=e.error_type,
                message=e.message,
                language_version=rule_definition.get("language_version", "v1.0")
            )
            return RuleValidationResultDTO(rule_id=rule_id, is_valid=False, compile_errors=[error_dto])

    def compile_rule_preview(self, rule_id: str, rule_definition: Dict[str, Any]) -> RuleCompilePreviewDTO:
        import dataclasses
        try:
            compiled = RuleCompiler.compile(rule_id, rule_definition)
            return RuleCompilePreviewDTO(
                rule_id=rule_id,
                compile_status="success",
                compiled_rule=dataclasses.asdict(compiled),
                compile_errors=[]
            )
        except RuleCompileError as e:
            error_dto = CompileErrorDTO(
                rule_id=rule_id,
                error_type=e.error_type,
                message=e.message,
                language_version=rule_definition.get("language_version", "v1.0")
            )
            return RuleCompilePreviewDTO(
                rule_id=rule_id,
                compile_status="error",
                compiled_rule=None,
                compile_errors=[error_dto]
            )

    def save_rule_draft(self, baseline_id: str, rule_id: str, rule_definition: Dict[str, Any]):
        self._ensure_workspace(baseline_id)
        self._draft_workspace[baseline_id][rule_id] = rule_definition

    def publish_baseline_version(self, baseline_id: str, change_note: str) -> Tuple[bool, str, int, str]:
        """
        Returns: (is_success, new_version, published_count, error_message)
        """
        self._ensure_workspace(baseline_id)
        drafts = self._draft_workspace[baseline_id]
        
        # 1. Compile check all drafts
        for rule_id, rule_def in drafts.items():
            try:
                RuleCompiler.compile(rule_id, rule_def)
            except RuleCompileError as e:
                return False, "", 0, f"Cannot publish. Compile error in {rule_id}: {e.message}"
                
        # 2. Get baseline
        baseline = self.repo.get_by_id(baseline_id)
        if not baseline:
            return False, "", 0, "Baseline not found"
            
        # 3. Bump version and save
        current_version = getattr(baseline, "baseline_version", baseline.get("baseline_version", "v1.0")) if isinstance(baseline, dict) else baseline.baseline_version
        
        # Snapshot the old version into the version history before updating the main record
        # In a real db, this would be a separate table. We'll use the 'baseline_version_snapshot' field.
        snapshots = getattr(baseline, "baseline_version_snapshot", baseline.get("baseline_version_snapshot", {})) if isinstance(baseline, dict) else baseline.baseline_version_snapshot
        if not snapshots:
            snapshots = {}
            
        old_rule_set = getattr(baseline, "rule_set", baseline.get("rule_set", {})) if isinstance(baseline, dict) else baseline.rule_set
        snapshots[current_version] = copy.deepcopy(old_rule_set)
        
        try:
            major, minor = current_version.lstrip("v").split(".")
            new_version = f"v{major}.{int(minor) + 1}"
        except:
            new_version = f"{current_version}_new"
            
        if isinstance(baseline, dict):
            baseline["rule_set"] = copy.deepcopy(drafts)
            baseline["baseline_version"] = new_version
            baseline["baseline_version_snapshot"] = snapshots
        else:
            baseline.rule_set = copy.deepcopy(drafts)
            baseline.baseline_version = new_version
            baseline.baseline_version_snapshot = snapshots
            
        self.repo.save(baseline)
        
        return True, new_version, len(drafts), ""

    def get_template_form_schema(self, template_name: str) -> Dict[str, Any]:
        t = TemplateRegistry.get_template(template_name)
        if not t:
            return {}
        return {
            "template_name": template_name,
            "supported_params": t["supported_params"]
        }

    def list_baseline_versions(self, baseline_id: str) -> List[BaselineVersionDTO]:
        baseline = self.repo.get_by_id(baseline_id)
        if not baseline:
            return []

        snapshots = getattr(baseline, "baseline_version_snapshot", baseline.get("baseline_version_snapshot", {})) if isinstance(baseline, dict) else baseline.baseline_version_snapshot
        
        versions = []
        for ver, rule_set in snapshots.items():
            versions.append(BaselineVersionDTO(
                baseline_id=baseline_id,
                baseline_version=ver,
                rule_count=len(rule_set),
                created_at="past"
            ))
            
        current_version = getattr(baseline, "baseline_version", baseline.get("baseline_version", "v1.0")) if isinstance(baseline, dict) else baseline.baseline_version
        current_rule_set = getattr(baseline, "rule_set", baseline.get("rule_set", {})) if isinstance(baseline, dict) else baseline.rule_set
        versions.append(BaselineVersionDTO(
            baseline_id=baseline_id,
            baseline_version=current_version,
            rule_count=len(current_rule_set),
            created_at="current"
        ))
        
        return sorted(versions, key=lambda x: x.baseline_version, reverse=True)

    def _get_rule_set_for_version(self, baseline, version: str) -> Dict[str, Any]:
        current_version = getattr(baseline, "baseline_version", baseline.get("baseline_version", "v1.0")) if isinstance(baseline, dict) else baseline.baseline_version
        if version == current_version:
            return getattr(baseline, "rule_set", baseline.get("rule_set", {})) if isinstance(baseline, dict) else baseline.rule_set
            
        snapshots = getattr(baseline, "baseline_version_snapshot", baseline.get("baseline_version_snapshot", {})) if isinstance(baseline, dict) else baseline.baseline_version_snapshot
        return snapshots.get(version, {})

    def get_baseline_diff(self, baseline_id: str, version_1: str, version_2: str) -> Optional[BaselineDiffDTO]:
        baseline = self.repo.get_by_id(baseline_id)
        if not baseline:
            return None
            
        rules_v1 = self._get_rule_set_for_version(baseline, version_1)
        rules_v2 = self._get_rule_set_for_version(baseline, version_2)
        
        added = []
        removed = []
        modified = []
        
        # Check added and modified
        for rule_id, rule_def2 in rules_v2.items():
            if rule_id not in rules_v1:
                added.append(RuleDiffItemDTO(rule_id=rule_id, change_type="added", changed_fields=[], before=None, after=rule_def2))
            else:
                rule_def1 = rules_v1[rule_id]
                changed_fields = []
                for k, v in rule_def2.items():
                    if rule_def1.get(k) != v:
                        changed_fields.append(k)
                for k in rule_def1.keys():
                    if k not in rule_def2:
                        changed_fields.append(k)
                
                if changed_fields:
                    modified.append(RuleDiffItemDTO(
                        rule_id=rule_id, 
                        change_type="modified", 
                        changed_fields=changed_fields,
                        before=rule_def1,
                        after=rule_def2
                    ))
                    
        # Check removed
        for rule_id, rule_def1 in rules_v1.items():
            if rule_id not in rules_v2:
                removed.append(RuleDiffItemDTO(rule_id=rule_id, change_type="removed", changed_fields=[], before=rule_def1, after=None))
                
        return BaselineDiffDTO(
            baseline_id=baseline_id,
            version_1=version_1,
            version_2=version_2,
            added_rules=added,
            removed_rules=removed,
            modified_rules=modified
        )

    def rollback_to_version(self, baseline_id: str, target_version: str) -> Tuple[bool, str, str]:
        baseline = self.repo.get_by_id(baseline_id)
        if not baseline:
            return False, "", "Baseline not found"
            
        target_rules = self._get_rule_set_for_version(baseline, target_version)
        if not target_rules:
            return False, "", f"Version {target_version} not found"
            
        self._draft_workspace[baseline_id] = copy.deepcopy(target_rules)
        success, new_ver, _, msg = self.publish_baseline_version(baseline_id, f"Rollback to {target_version}")
        return success, new_ver, msg
