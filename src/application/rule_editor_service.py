from typing import List, Dict, Any, Optional
import copy
from src.application.dto_models import (
    RuleEditorBaselineDTO, 
    RuleEditorDraftDTO, 
    RuleValidationResultDTO, 
    RuleCompilePreviewDTO,
    CompileErrorDTO
)
from src.infrastructure.repository import BaselineRepository
from src.domain.rule_compiler import RuleCompiler, RuleCompileError, TemplateRegistry

class RuleEditorService:
    def __init__(self):
        self.repo = BaselineRepository()
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
        try:
            compiled = RuleCompiler.compile(rule_id, rule_definition)
            return RuleCompilePreviewDTO(
                rule_id=rule_id,
                compile_status="success",
                compiled_rule=compiled,
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
            
        # 3. Bump version and save (simulated)
        current_version = getattr(baseline, "baseline_version", baseline.get("baseline_version", "v1.0")) if isinstance(baseline, dict) else baseline.baseline_version
        
        try:
            major, minor = current_version.lstrip("v").split(".")
            new_version = f"v{major}.{int(minor) + 1}"
        except:
            new_version = f"{current_version}_new"
            
        if isinstance(baseline, dict):
            baseline["rule_set"] = copy.deepcopy(drafts)
            baseline["baseline_version"] = new_version
        else:
            baseline.rule_set = copy.deepcopy(drafts)
            baseline.baseline_version = new_version
            
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
