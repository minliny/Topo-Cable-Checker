from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from src.application.rule_editor_services.rule_editor_mvp_service import RuleDraftView
from src.domain.rule_compiler import RuleCompiler, RuleCompileError
from src.domain.rule_engine.compiled_rule import RuleValidationError

@dataclass
class RuleDraftGovernanceError:
    error_type: str
    message: str
    field_name: Optional[str] = None

@dataclass
class RuleDraftCompileResult:
    compile_success: bool
    compiled_preview: Optional[Dict[str, Any]]
    validation_errors: List[RuleDraftGovernanceError]

@dataclass
class RuleDraftPublishCandidateView:
    rule_id: str
    rule_type: str
    target_type: str
    is_ready_for_publish: bool
    compile_result: RuleDraftCompileResult
    diff_summary: str

class RuleEditorGovernanceBridgeService:
    """
    Bridges the RuleEditor MVP output (RuleDraftView) into the governance/compiler layer.
    """

    def compile_draft_preview(self, draft: RuleDraftView) -> RuleDraftCompileResult:
        # First check if the draft itself failed UI-level validation
        if draft.validation_result and not draft.validation_result.is_valid:
            errors = [
                RuleDraftGovernanceError(
                    error_type="form_validation_error",
                    message=msg,
                    field_name=field if field != "_base" else None
                )
                for field, msg in draft.validation_result.errors.items()
            ]
            return RuleDraftCompileResult(
                compile_success=False,
                compiled_preview=None,
                validation_errors=errors
            )

        rule_def = draft.to_rule_def()
        errors = []
        compiled_dict = None

        try:
            # Attempt to compile
            compiled_rule = RuleCompiler.compile(draft.rule_id, rule_def)
            
            # Attempt to validate the compiled rule
            compiled_rule.validate()
            
            compiled_dict = compiled_rule.to_dict()
            
            # Strip internal objects from preview dict for safe JSON serialization in UI
            if "rule_meta" in compiled_dict:
                del compiled_dict["rule_meta"]
            if "capability" in compiled_dict:
                del compiled_dict["capability"]
                
        except RuleCompileError as e:
            errors.append(self._map_compile_error(e))
        except RuleValidationError as e:
            errors.append(RuleDraftGovernanceError(
                error_type="rule_validation_error",
                message=str(e),
                field_name=None
            ))
        except Exception as e:
            errors.append(RuleDraftGovernanceError(
                error_type="unexpected_error",
                message=f"An unexpected error occurred during compilation: {str(e)}",
                field_name=None
            ))

        return RuleDraftCompileResult(
            compile_success=(len(errors) == 0),
            compiled_preview=compiled_dict,
            validation_errors=errors
        )

    def _map_compile_error(self, error: RuleCompileError) -> RuleDraftGovernanceError:
        """
        Attempts to map low-level compiler errors to specific form fields.
        """
        field_name = None
        
        if error.error_type in ["missing_required_param", "invalid_parameter_schema"]:
            # Attempt to extract field name from message like "missing_required_param: metric_type is required"
            # or "Missing required parameter: metric_type"
            if "is required" in error.message:
                parts = error.message.split(":")
                if len(parts) > 1:
                    potential_field = parts[-1].replace("is required", "").strip()
                    field_name = potential_field
            elif "Missing required parameter" in error.message:
                parts = error.message.split(":")
                if len(parts) > 1:
                    potential_field = parts[-1].strip()
                    field_name = potential_field
                    
        elif error.error_type == "unknown_rule_capability":
            # Map capability inference errors back to a general form error
            field_name = "_base"

        return RuleDraftGovernanceError(
            error_type=error.error_type,
            message=error.message,
            field_name=field_name
        )

    def build_publish_candidate(self, draft: RuleDraftView) -> RuleDraftPublishCandidateView:
        compile_result = self.compile_draft_preview(draft)
        
        diff_summary = f"New rule '{draft.rule_id}' of type '{draft.rule_type}' targeting '{draft.target_type}'."
        if not compile_result.compile_success:
            diff_summary = f"Draft rule '{draft.rule_id}' has {len(compile_result.validation_errors)} compilation errors."

        return RuleDraftPublishCandidateView(
            rule_id=draft.rule_id,
            rule_type=draft.rule_type,
            target_type=draft.target_type,
            is_ready_for_publish=compile_result.compile_success,
            compile_result=compile_result,
            diff_summary=diff_summary
        )
