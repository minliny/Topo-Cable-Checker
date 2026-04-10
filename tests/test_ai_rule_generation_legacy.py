import pytest
from typing import Dict, Any

from src.application.ports.llm_gateway import ILLMGateway, LLMResponse
from src.application.rule_editor_services.rule_editor_mvp_service import RuleEditorMVPService
from src.legacy_ai_internal.ai_rule_generation_service import (
    AiRuleGenerationService, 
    AiRuleGenerationRequest
)
from src.application.rule_editor_services.rule_spec_renderer import RuleSpecRenderer
from src.application.rule_editor_services.rule_schema_builder import RuleDraftSchemaBuilder

class FakeLLMGateway(ILLMGateway):
    def __init__(self, response_content: Dict[str, Any]):
        self.response_content = response_content
        self.last_system_prompt = ""
        self.last_user_input = ""
        self.last_output_schema = None

    def generate_structured_rule_draft(
        self,
        system_instruction: str,
        user_input: str,
        output_schema: Dict[str, Any] | None = None,
    ) -> LLMResponse:
        self.last_system_prompt = system_instruction
        self.last_user_input = user_input
        self.last_output_schema = output_schema
        return LLMResponse(content=self.response_content, raw_output=str(self.response_content))

@pytest.fixture
def editor_service():
    return RuleEditorMVPService()

def test_generate_rule_draft_from_text_success(editor_service):
    llm_output = {
        "rule_type": "threshold",
        "target_type": "devices",
        "severity": "high",
        "rule_definition": {
            "metric_type": "count",
            "operator": "gt",
            "expected_value": 100
        }
    }
    gateway = FakeLLMGateway(llm_output)
    service = AiRuleGenerationService(gateway, editor_service)
    
    req = AiRuleGenerationRequest(user_input="Create a rule where device count is greater than 100")
    result = service.generate_rule_draft_from_text(req)
    
    assert result.success is True
    assert result.candidate_rule_type == "threshold"
    assert result.candidate_rule_definition == llm_output["rule_definition"]
    assert result.validated_draft is not None
    assert result.validated_draft.validation_result.is_valid is True
    assert len(result.validation_errors) == 0
    assert len(result.schema_errors) == 0
    assert len(result.editor_validation_errors) == 0

def test_generate_rule_draft_from_text_unknown_rule_type(editor_service):
    llm_output = {
        "rule_type": "magic_rule",
        "target_type": "devices",
        "severity": "low",
        "rule_definition": {
            "foo": "bar"
        }
    }
    gateway = FakeLLMGateway(llm_output)
    service = AiRuleGenerationService(gateway, editor_service)
    
    req = AiRuleGenerationRequest(user_input="Do some magic")
    result = service.generate_rule_draft_from_text(req)
    
    assert result.success is False
    assert result.validated_draft is None
    assert len(result.validation_errors) > 0
    assert any(err.code == "unknown_rule_type" for err in result.schema_errors)

def test_generate_rule_draft_from_text_missing_required_field(editor_service):
    llm_output = {
        "rule_type": "threshold",
        "target_type": "devices",
        "severity": "medium",
        "rule_definition": {
            # missing metric_type which is required
            "operator": "lt",
            "expected_value": 50
        }
    }
    gateway = FakeLLMGateway(llm_output)
    service = AiRuleGenerationService(gateway, editor_service)
    
    req = AiRuleGenerationRequest(user_input="Check if less than 50")
    result = service.generate_rule_draft_from_text(req)
    
    assert result.success is False
    assert result.validated_draft is None
    assert any(err.code == "missing_required_field" and err.field == "rule_definition.metric_type" for err in result.schema_errors)

def test_generate_rule_draft_from_text_invalid_enum_value(editor_service):
    llm_output = {
        "rule_type": "threshold",
        "target_type": "devices",
        "severity": "medium",
        "rule_definition": {
            "metric_type": "count",
            "operator": "invalid_op", # invalid enum
            "expected_value": 50
        }
    }
    gateway = FakeLLMGateway(llm_output)
    service = AiRuleGenerationService(gateway, editor_service)
    
    req = AiRuleGenerationRequest(user_input="Check if invalid_op than 50")
    result = service.generate_rule_draft_from_text(req)
    
    assert result.success is False
    assert result.validated_draft is None
    assert any(err.code == "invalid_enum_value" and err.field == "rule_definition.operator" for err in result.schema_errors)

def test_prompt_builder_includes_catalog_constraints():
    schema = RuleDraftSchemaBuilder.build()
    prompt = RuleSpecRenderer.build(schema=schema, user_input="x")
    
    # Assert rule type information
    assert "Rule Type: `threshold`" in prompt
    assert "Rule Type: `single_fact`" in prompt
    
    # Assert required field
    assert "REQUIRED" in prompt
    
    # Assert enum values
    assert "ENUM: ['count', 'distinct_count', 'sum', 'average']" in prompt
    
    # Assert expected output format structure
    assert '"rule_type": "string"' in prompt
    assert '"rule_definition"' in prompt

def test_ai_generation_service_runs_schema_validation_before_editor_validation():
    class ExplodingEditorService(RuleEditorMVPService):
        def validate_and_build_draft(self, *args, **kwargs):
            raise AssertionError("Editor validation should not run when schema validation fails")

    llm_output = ["invalid"]
    gateway = FakeLLMGateway(llm_output)
    service = AiRuleGenerationService(gateway, ExplodingEditorService())

    req = AiRuleGenerationRequest(user_input="x")
    result = service.generate_rule_draft_from_text(req)

    assert result.success is False
    assert result.validated_draft is None
    assert any(e.code == "invalid_top_level_shape" for e in result.schema_errors)

def test_gateway_receives_output_schema(editor_service):
    llm_output = {
        "rule_type": "threshold",
        "target_type": "devices",
        "severity": "high",
        "rule_definition": {
            "metric_type": "count",
            "operator": "gt",
            "expected_value": 100
        }
    }
    gateway = FakeLLMGateway(llm_output)
    service = AiRuleGenerationService(gateway, editor_service)

    result = service.generate_rule_draft_from_text(AiRuleGenerationRequest(user_input="x"))
    assert result.raw_model_output is not None
    assert gateway.last_output_schema is not None

def test_ai_generation_result_preserves_raw_model_output(editor_service):
    llm_output = {
        "rule_type": "threshold",
        "target_type": "devices",
        "severity": "medium",
        "rule_definition": {
            "metric_type": "count",
            "operator": "eq",
            "expected_value": 10
        },
        "some_extra_reasoning": "I chose threshold because..."
    }
    gateway = FakeLLMGateway(llm_output)
    service = AiRuleGenerationService(gateway, editor_service)
    
    req = AiRuleGenerationRequest(user_input="Count equals 10")
    result = service.generate_rule_draft_from_text(req)
    
    assert result.raw_model_output is not None
    assert result.raw_model_output == llm_output
    assert result.raw_model_output.get("some_extra_reasoning") == "I chose threshold because..."
    assert any(e.code == "unknown_top_level_field" and e.field == "some_extra_reasoning" for e in result.schema_errors)
