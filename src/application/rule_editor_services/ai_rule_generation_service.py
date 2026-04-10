from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import uuid

from src.application.ports.llm_gateway import ILLMGateway
from src.application.rule_editor_services.rule_editor_mvp_service import RuleEditorMVPService, RuleDraftView
from src.application.rule_editor_services.ai_rule_prompt_builder import AiRulePromptBuilder
from src.application.rule_editor_services.ai_rule_schema_builder import AiRuleSchemaBuilder
from src.application.rule_editor_services.ai_rule_output_validator import AiRuleOutputValidator

@dataclass
class AiRuleGenerationRequest:
    user_input: str
    rule_id: Optional[str] = None

@dataclass
class AiGenerationValidationErrorView:
    code: str
    field: str
    message: str
    source: str

@dataclass
class AiGeneratedDraftCandidate:
    rule_type: str
    target_type: str
    severity: str
    rule_definition: Dict[str, Any]

@dataclass
class AiRuleGenerationResult:
    success: bool
    candidate_rule_type: Optional[str]
    candidate_rule_definition: Optional[Dict[str, Any]]
    validated_draft: Optional[RuleDraftView]
    schema_errors: List[AiGenerationValidationErrorView]
    editor_validation_errors: List[AiGenerationValidationErrorView]
    validation_errors: List[AiGenerationValidationErrorView]
    raw_model_output: Optional[Dict[str, Any]]

class AiRuleGenerationService:
    def __init__(self, llm_gateway: ILLMGateway, editor_service: RuleEditorMVPService):
        self._llm_gateway = llm_gateway
        self._editor_service = editor_service

    def generate_rule_draft_from_text(self, request: AiRuleGenerationRequest) -> AiRuleGenerationResult:
        schema = AiRuleSchemaBuilder.build()
        system_instruction = AiRulePromptBuilder.build(schema=schema, user_input=request.user_input)
        output_schema = AiRuleSchemaBuilder.to_gateway_schema(schema)

        llm_response = self._llm_gateway.generate_structured_rule_draft(
            system_instruction=system_instruction,
            user_input=request.user_input,
            output_schema=output_schema,
        )
        
        raw_output = llm_response.content

        schema_result = AiRuleOutputValidator.validate(raw_output, schema)
        if not schema_result.is_valid:
            schema_errors = [
                AiGenerationValidationErrorView(
                    code=e.code,
                    field=e.field,
                    message=e.message,
                    source="schema",
                )
                for e in schema_result.schema_errors
            ]

            return AiRuleGenerationResult(
                success=False,
                candidate_rule_type=schema_result.candidate_rule_type,
                candidate_rule_definition=schema_result.candidate_rule_definition,
                validated_draft=None,
                schema_errors=schema_errors,
                editor_validation_errors=[],
                validation_errors=schema_errors,
                raw_model_output=raw_output,
            )

        rule_id = request.rule_id or str(uuid.uuid4())

        draft_view = self._editor_service.validate_and_build_draft(
            rule_id=rule_id,
            rule_type=schema_result.candidate_rule_type or "",
            target_type=schema_result.candidate_target_type or "",
            severity=schema_result.candidate_severity or "",
            form_data=schema_result.candidate_rule_definition or {},
        )
        
        editor_validation_errors: List[AiGenerationValidationErrorView] = []
        if draft_view.validation_result and not draft_view.validation_result.is_valid:
            for field, msg in draft_view.validation_result.errors.items():
                editor_validation_errors.append(
                    AiGenerationValidationErrorView(
                        code="editor_validation_error",
                        field=field,
                        message=msg,
                        source="editor",
                    )
                )
                
        success = len(editor_validation_errors) == 0
        
        return AiRuleGenerationResult(
            success=success,
            candidate_rule_type=schema_result.candidate_rule_type,
            candidate_rule_definition=schema_result.candidate_rule_definition,
            validated_draft=draft_view if success else None,
            schema_errors=[],
            editor_validation_errors=editor_validation_errors,
            validation_errors=editor_validation_errors,
            raw_model_output=raw_output,
        )
