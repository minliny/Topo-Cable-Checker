from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import uuid

from src.application.ports.llm_gateway import ILLMGateway
from src.application.rule_editor_services.rule_editor_mvp_service import RuleEditorMVPService, RuleDraftView
from src.application.rule_editor_services.ai_rule_prompt_builder import AiRulePromptBuilder

@dataclass
class AiRuleGenerationRequest:
    user_input: str
    rule_id: Optional[str] = None

@dataclass
class AiGenerationValidationErrorView:
    field: str
    message: str

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
    validation_errors: List[AiGenerationValidationErrorView]
    raw_model_output: Optional[Dict[str, Any]]

class AiRuleGenerationService:
    """
    Coordinates AI rule generation by building prompt from catalog constraints, 
    calling LLM via gateway, parsing structured output, and finally delegating 
    validation to the MVP Rule Editor Service.
    """
    
    def __init__(self, llm_gateway: ILLMGateway, editor_service: RuleEditorMVPService):
        self._llm_gateway = llm_gateway
        self._editor_service = editor_service

    def generate_rule_draft_from_text(self, request: AiRuleGenerationRequest) -> AiRuleGenerationResult:
        # 1. Build context prompt
        system_prompt = AiRulePromptBuilder.build_system_prompt()
        
        # 2. Invoke LLM Gateway
        llm_response = self._llm_gateway.generate_structured_rule_draft(
            system_prompt=system_prompt,
            user_input=request.user_input
        )
        
        raw_output = llm_response.content
        
        # 3. Parse LLM response into candidate format
        rule_type = raw_output.get("rule_type")
        target_type = raw_output.get("target_type", "devices")
        severity = raw_output.get("severity", "medium")
        rule_definition = raw_output.get("rule_definition", {})
        
        rule_id = request.rule_id or str(uuid.uuid4())
        
        if not rule_type:
            return AiRuleGenerationResult(
                success=False,
                candidate_rule_type=None,
                candidate_rule_definition=rule_definition,
                validated_draft=None,
                validation_errors=[AiGenerationValidationErrorView(field="rule_type", message="Missing rule_type in AI output.")],
                raw_model_output=raw_output
            )
            
        # 4. Delegate to existing Editor Validation Pipeline
        draft_view = self._editor_service.validate_and_build_draft(
            rule_id=rule_id,
            rule_type=rule_type,
            target_type=target_type,
            severity=severity,
            form_data=rule_definition
        )
        
        # 5. Extract validation errors and construct final result
        validation_errors = []
        if draft_view.validation_result and not draft_view.validation_result.is_valid:
            for field, msg in draft_view.validation_result.errors.items():
                validation_errors.append(AiGenerationValidationErrorView(field=field, message=msg))
                
        success = len(validation_errors) == 0
        
        return AiRuleGenerationResult(
            success=success,
            candidate_rule_type=rule_type,
            candidate_rule_definition=rule_definition,
            validated_draft=draft_view if success else None,
            validation_errors=validation_errors,
            raw_model_output=raw_output
        )
