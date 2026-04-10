# Schema-Driven AI Rule Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor AI Rule Generation MVP to be schema-driven (canonical schema from Catalog → prompt expression → schema-aware gateway → local schema validator → editor validation).

**Architecture:** Add `AiDraftSchema` (dataclass) as the stable Application-layer contract derived from `RuleCatalogPresentationService`. PromptBuilder becomes presentation-only. LLM output is locally schema-validated before any call into `RuleEditorMVPService`, which remains the business truth source.

**Tech Stack:** Python, pytest, existing Application/Domain layering, no external LLM SDK.

---

## File map (create/modify)

**Create**
- `src/application/rule_editor_services/ai_rule_schema_builder.py`
- `src/application/rule_editor_services/ai_rule_output_validator.py`
- `tests/test_ai_rule_schema_builder.py`
- `tests/test_ai_rule_output_validator.py`

**Modify**
- `src/application/rule_editor_services/ai_rule_generation_service.py`
- `src/application/rule_editor_services/ai_rule_prompt_builder.py`
- `src/application/ports/llm_gateway.py`
- `tests/test_ai_rule_generation_service.py`
- `docs/PROJECT_STATE_SNAPSHOT.yaml`
- `docs/PROJECT_OVERVIEW.md`

---

## Task 1: Upgrade `ILLMGateway` to accept `output_schema`

**Files:**
- Modify: `src/application/ports/llm_gateway.py`
- Modify: `tests/test_ai_rule_generation_service.py`

- [ ] **Step 1: Write failing test for gateway receiving `output_schema`**

Update `tests/test_ai_rule_generation_service.py` to store `last_output_schema` in the fake and assert it is not `None`.

```python
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

def test_gateway_receives_output_schema(editor_service):
    llm_output = {
        "rule_type": "threshold",
        "target_type": "devices",
        "severity": "high",
        "rule_definition": {"metric_type": "count", "operator": "gt", "expected_value": 100},
    }
    gateway = FakeLLMGateway(llm_output)
    service = AiRuleGenerationService(gateway, editor_service)

    result = service.generate_rule_draft_from_text(AiRuleGenerationRequest(user_input="x"))
    assert result.raw_model_output is not None
    assert gateway.last_output_schema is not None
```

- [ ] **Step 2: Run the single test to verify it fails**

Run:
```bash
pytest tests/test_ai_rule_generation_service.py::test_gateway_receives_output_schema -q
```

Expected: FAIL because `ILLMGateway.generate_structured_rule_draft(...)` signature doesn’t accept `output_schema` yet.

- [ ] **Step 3: Update port interface**

Modify `src/application/ports/llm_gateway.py` to:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class LLMResponse:
    content: Dict[str, Any]
    raw_output: str

class ILLMGateway(ABC):
    @abstractmethod
    def generate_structured_rule_draft(
        self,
        system_instruction: str,
        user_input: str,
        output_schema: Optional[Dict[str, Any]] = None,
    ) -> LLMResponse:
        pass
```

- [ ] **Step 4: Fix the fake gateway and any call sites compilation errors**

Update any call sites to pass named parameter `system_instruction` (or keep `system_prompt` but make interface consistent—preferred: `system_instruction`).

- [ ] **Step 5: Re-run the single test**

Run:
```bash
pytest tests/test_ai_rule_generation_service.py::test_gateway_receives_output_schema -q
```

Expected: still FAIL until Tasks 2–4 are done (service doesn’t pass schema yet). That’s acceptable; keep moving with TDD, or temporarily wire a placeholder schema dict in the service and remove later.

---

## Task 2: Implement canonical schema and `AiRuleSchemaBuilder`

**Files:**
- Create: `src/application/rule_editor_services/ai_rule_schema_builder.py`
- Create: `tests/test_ai_rule_schema_builder.py`

- [ ] **Step 1: Write failing test for canonical schema build**

Create `tests/test_ai_rule_schema_builder.py`:

```python
from src.application.rule_editor_services.ai_rule_schema_builder import AiRuleSchemaBuilder

def test_ai_rule_schema_builder_builds_canonical_schema():
    schema = AiRuleSchemaBuilder.build()
    assert schema.rule_types

    threshold = next((t for t in schema.rule_types if t.rule_type == "threshold"), None)
    assert threshold is not None

    metric_type = next((f for f in threshold.fields if f.name == "metric_type"), None)
    assert metric_type is not None
    assert metric_type.required is True
    assert metric_type.enum_values is not None
    assert "count" in metric_type.enum_values

    assert "rule_type" in schema.output_contract["properties"]
    assert "target_type" in schema.output_contract["properties"]
    assert "severity" in schema.output_contract["properties"]
    assert "rule_definition" in schema.output_contract["properties"]
    assert schema.output_contract["additionalProperties"] is False
```

- [ ] **Step 2: Run the new test to verify it fails**

Run:
```bash
pytest tests/test_ai_rule_schema_builder.py -q
```

Expected: FAIL because `AiRuleSchemaBuilder` doesn’t exist.

- [ ] **Step 3: Implement schema dataclasses + builder**

Create `src/application/rule_editor_services/ai_rule_schema_builder.py`:

```python
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.application.rule_catalog_services.rule_catalog_presentation_service import RuleCatalogPresentationService

@dataclass(frozen=True)
class AiRuleFieldSchema:
    name: str
    field_type: str
    required: bool
    enum_values: Optional[List[str]]
    description: Optional[str]
    default: Any

@dataclass(frozen=True)
class AiRuleTypeSchema:
    rule_type: str
    summary: Optional[str]
    fields: List[AiRuleFieldSchema]

@dataclass(frozen=True)
class AiDraftSchema:
    rule_types: List[AiRuleTypeSchema]
    output_contract: Dict[str, Any]

class AiRuleSchemaBuilder:
    @classmethod
    def build(cls) -> AiDraftSchema:
        previews = RuleCatalogPresentationService.list_rule_previews()
        rule_types: List[AiRuleTypeSchema] = []

        for p in previews:
            form_def = RuleCatalogPresentationService.get_rule_form_definition(p.rule_type)
            if not form_def:
                continue

            fields: List[AiRuleFieldSchema] = []
            for f in form_def.parameter_fields:
                fields.append(
                    AiRuleFieldSchema(
                        name=f.field_name,
                        field_type=f.field_type,
                        required=f.required,
                        enum_values=f.enum_options,
                        description=f.help_text or None,
                        default=f.default_value,
                    )
                )

            rule_types.append(
                AiRuleTypeSchema(
                    rule_type=p.rule_type,
                    summary=p.description or None,
                    fields=fields,
                )
            )

        output_contract = cls._build_output_contract(rule_types)
        return AiDraftSchema(rule_types=rule_types, output_contract=output_contract)

    @classmethod
    def to_gateway_schema(cls, schema: AiDraftSchema) -> Dict[str, Any]:
        return dict(schema.output_contract)

    @classmethod
    def _build_output_contract(cls, rule_types: List[AiRuleTypeSchema]) -> Dict[str, Any]:
        return {
            "type": "object",
            "additionalProperties": False,
            "required": ["rule_type", "target_type", "severity", "rule_definition"],
            "properties": {
                "rule_type": {"type": "string", "enum": [rt.rule_type for rt in rule_types]},
                "target_type": {"type": "string"},
                "severity": {"type": "string"},
                "rule_definition": {"type": "object"},
            },
        }
```

- [ ] **Step 4: Run schema builder test**

Run:
```bash
pytest tests/test_ai_rule_schema_builder.py -q
```

Expected: PASS.

---

## Task 3: Implement `AiRuleOutputValidator` (local schema gate)

**Files:**
- Create: `src/application/rule_editor_services/ai_rule_output_validator.py`
- Create: `tests/test_ai_rule_output_validator.py`

- [ ] **Step 1: Write failing validator tests (core rejection cases)**

Create `tests/test_ai_rule_output_validator.py`:

```python
from src.application.rule_editor_services.ai_rule_output_validator import AiRuleOutputValidator
from src.application.rule_editor_services.ai_rule_schema_builder import AiRuleSchemaBuilder

def test_ai_output_validator_rejects_invalid_top_level_shape():
    schema = AiRuleSchemaBuilder.build()
    result = AiRuleOutputValidator.validate(["not-a-dict"], schema)
    assert result.is_valid is False
    assert any(e.code == "invalid_top_level_shape" for e in result.errors)

def test_ai_output_validator_rejects_unknown_top_level_fields():
    schema = AiRuleSchemaBuilder.build()
    result = AiRuleOutputValidator.validate(
        {"rule_type": "threshold", "target_type": "devices", "severity": "high", "rule_definition": {}, "x": 1},
        schema,
    )
    assert result.is_valid is False
    assert any(e.code == "unknown_top_level_field" for e in result.errors)

def test_ai_output_validator_rejects_unknown_rule_definition_fields():
    schema = AiRuleSchemaBuilder.build()
    result = AiRuleOutputValidator.validate(
        {"rule_type": "threshold", "target_type": "devices", "severity": "high", "rule_definition": {"nope": 1}},
        schema,
    )
    assert result.is_valid is False
    assert any(e.code == "unknown_field" for e in result.errors)

def test_ai_output_validator_rejects_invalid_enum_value():
    schema = AiRuleSchemaBuilder.build()
    result = AiRuleOutputValidator.validate(
        {
            "rule_type": "threshold",
            "target_type": "devices",
            "severity": "high",
            "rule_definition": {"metric_type": "count", "operator": "INVALID", "expected_value": 1},
        },
        schema,
    )
    assert result.is_valid is False
    assert any(e.code == "invalid_enum_value" for e in result.errors)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
pytest tests/test_ai_rule_output_validator.py -q
```

Expected: FAIL because validator doesn’t exist.

- [ ] **Step 3: Implement validator with structured result**

Create `src/application/rule_editor_services/ai_rule_output_validator.py`:

```python
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

from src.application.rule_editor_services.ai_rule_schema_builder import AiDraftSchema, AiRuleTypeSchema, AiRuleFieldSchema

@dataclass(frozen=True)
class AiSchemaValidationError:
    code: str
    field: str
    message: str

@dataclass(frozen=True)
class AiSchemaValidationResult:
    is_valid: bool
    errors: List[AiSchemaValidationError]
    candidate_rule_type: Optional[str]
    candidate_target_type: Optional[str]
    candidate_severity: Optional[str]
    candidate_rule_definition: Optional[Dict[str, Any]]

class AiRuleOutputValidator:
    _ALLOWED_TOP_LEVEL: Set[str] = {"rule_type", "target_type", "severity", "rule_definition"}

    @classmethod
    def validate(cls, raw_output: Any, schema: AiDraftSchema) -> AiSchemaValidationResult:
        errors: List[AiSchemaValidationError] = []

        if not isinstance(raw_output, dict):
            errors.append(AiSchemaValidationError("invalid_top_level_shape", "_top", "Top-level output must be an object."))
            return AiSchemaValidationResult(False, errors, None, None, None, None)

        unknown_top = [k for k in raw_output.keys() if k not in cls._ALLOWED_TOP_LEVEL]
        for k in unknown_top:
            errors.append(AiSchemaValidationError("unknown_top_level_field", k, f"Unknown top-level field: {k}"))

        rule_type = raw_output.get("rule_type")
        target_type = raw_output.get("target_type")
        severity = raw_output.get("severity")
        rule_definition = raw_output.get("rule_definition")

        if not isinstance(rule_type, str) or not rule_type.strip():
            errors.append(AiSchemaValidationError("invalid_rule_type", "rule_type", "rule_type must be a non-empty string."))
            return AiSchemaValidationResult(False, errors, None, target_type, severity, cls._as_dict(rule_definition))

        rule_type_schema = next((rt for rt in schema.rule_types if rt.rule_type == rule_type), None)
        if rule_type_schema is None:
            errors.append(AiSchemaValidationError("unknown_rule_type", "rule_type", f"Unknown rule_type: {rule_type}"))
            return AiSchemaValidationResult(False, errors, rule_type, target_type, severity, cls._as_dict(rule_definition))

        if not isinstance(rule_definition, dict):
            errors.append(AiSchemaValidationError("invalid_rule_definition", "rule_definition", "rule_definition must be an object."))
            return AiSchemaValidationResult(False, errors, rule_type, target_type, severity, None)

        allowed_fields = {f.name: f for f in rule_type_schema.fields}

        for fname in rule_definition.keys():
            if fname not in allowed_fields:
                errors.append(AiSchemaValidationError("unknown_field", f"rule_definition.{fname}", f"Unknown field for rule_type '{rule_type}': {fname}"))

        for f in rule_type_schema.fields:
            if f.required:
                v = rule_definition.get(f.name)
                if v is None or (isinstance(v, str) and not v.strip()):
                    errors.append(AiSchemaValidationError("missing_required_field", f"rule_definition.{f.name}", f"Missing required field: {f.name}"))

        for f in rule_type_schema.fields:
            if f.name not in rule_definition:
                continue
            v = rule_definition.get(f.name)
            if v is None:
                continue
            if f.enum_values and v not in f.enum_values:
                errors.append(AiSchemaValidationError("invalid_enum_value", f"rule_definition.{f.name}", f"Invalid enum value '{v}'. Must be one of: {f.enum_values}"))
            type_code = cls._check_type(v, f.field_type)
            if type_code:
                errors.append(AiSchemaValidationError("invalid_field_type", f"rule_definition.{f.name}", type_code))

        for top_field in ["target_type", "severity"]:
            if not isinstance(raw_output.get(top_field), str) or not raw_output.get(top_field):
                errors.append(AiSchemaValidationError("missing_required_field", top_field, f"Missing required top-level field: {top_field}"))

        is_valid = len(errors) == 0
        return AiSchemaValidationResult(is_valid, errors, rule_type, target_type, severity, rule_definition)

    @classmethod
    def _as_dict(cls, val: Any) -> Optional[Dict[str, Any]]:
        return val if isinstance(val, dict) else None

    @classmethod
    def _check_type(cls, val: Any, field_type: str) -> Optional[str]:
        if field_type == "string":
            return None if isinstance(val, str) else "Expected string."
        if field_type == "select":
            return None if isinstance(val, str) else "Expected string."
        if field_type == "number":
            return None if isinstance(val, (int, float)) and not isinstance(val, bool) else "Expected number."
        if field_type == "integer":
            return None if isinstance(val, int) and not isinstance(val, bool) else "Expected integer."
        if field_type == "boolean":
            return None if isinstance(val, bool) else "Expected boolean."
        return None
```

- [ ] **Step 4: Run validator tests**

Run:
```bash
pytest tests/test_ai_rule_output_validator.py -q
```

Expected: PASS.

---

## Task 4: Refactor PromptBuilder + GenerationService to schema-driven chain

**Files:**
- Modify: `src/application/rule_editor_services/ai_rule_prompt_builder.py`
- Modify: `src/application/rule_editor_services/ai_rule_generation_service.py`
- Modify: `tests/test_ai_rule_generation_service.py`

- [ ] **Step 1: Update PromptBuilder API to accept schema**

Replace `build_system_prompt()` with:

```python
from src.application.rule_editor_services.ai_rule_schema_builder import AiDraftSchema

class AiRulePromptBuilder:
    @classmethod
    def build(cls, schema: AiDraftSchema, user_input: str) -> str:
        ...
```

Ensure it does not import `RuleCatalogPresentationService`.

- [ ] **Step 2: Add failing test ensuring schema validation runs before editor validation**

In `tests/test_ai_rule_generation_service.py`, add a stub editor that explodes if called:

```python
class ExplodingEditorService(RuleEditorMVPService):
    def validate_and_build_draft(self, *args, **kwargs):
        raise AssertionError("Editor validation should not run when schema validation fails")

def test_ai_generation_service_runs_schema_validation_before_editor_validation():
    llm_output = ["invalid"]  # invalid top-level shape
    gateway = FakeLLMGateway(llm_output)
    editor = ExplodingEditorService()
    service = AiRuleGenerationService(gateway, editor)

    result = service.generate_rule_draft_from_text(AiRuleGenerationRequest(user_input="x"))
    assert result.success is False
    assert result.validated_draft is None
    assert any(e.field == "_top" for e in result.validation_errors)
```

- [ ] **Step 3: Implement new chain in `AiRuleGenerationService`**

Update service to:
1) `schema = AiRuleSchemaBuilder.build()`
2) `system_instruction = AiRulePromptBuilder.build(schema, request.user_input)`
3) `gateway_schema = AiRuleSchemaBuilder.to_gateway_schema(schema)` (pure dict)
4) `llm_response = gateway.generate_structured_rule_draft(system_instruction=..., user_input=..., output_schema=gateway_schema)`
5) `schema_result = AiRuleOutputValidator.validate(llm_response.content, schema)`
6) If schema invalid: map `schema_result.errors` into `AiGenerationValidationErrorView` (schema_error path) and **return early**
7) If schema valid: call editor validation and map editor errors (editor_validation_error path)

Also update `AiRuleGenerationResult` semantics:
- schema_error: `validated_draft=None`, `candidate_*` filled from schema_result if available
- editor_validation_error: keep `candidate_*` and `raw_model_output`, `validated_draft=None`
- success: `validated_draft` not `None`

- [ ] **Step 4: Update existing success/unknown/missing-required tests**

Update all fake LLM outputs to include required top-level `target_type` and `severity` and ensure schema validator passes.

- [ ] **Step 5: Run AI generation service test file**

Run:
```bash
pytest tests/test_ai_rule_generation_service.py -q
```

Expected: PASS.

---

## Task 5: Docs sync (schema-driven status)

**Files:**
- Modify: `docs/PROJECT_STATE_SNAPSHOT.yaml`
- Modify: `docs/PROJECT_OVERVIEW.md`

- [ ] **Step 1: Update snapshot to mention schema-driven chain**

Update `ai_agent_status` to explicitly state:
- Canonical schema between Catalog and LLM
- PromptBuilder is expression-only
- Local schema validator gates output before editor validation

- [ ] **Step 2: Update overview to mention schema-driven contract**

In AI section, add bullets:
- “Canonical schema 是 Catalog 与 LLM 之间稳定契约”
- “PromptBuilder 只负责表达层”
- “RuleEditorMVPService 仍然是最终业务真值”

- [ ] **Step 3: Run full test suite**

Run:
```bash
pytest -q
```

Expected: PASS.

---

## Self-review checklist (before implementation completes)
- [ ] Ensure LLM output top-level is strictly 4 fields (reject unknown top-level fields)
- [ ] Ensure `target_type` / `severity` are required and never implicitly defaulted in service
- [ ] Ensure schema validation failure never calls editor validation
- [ ] Ensure editor validation failure retains candidate + raw_model_output
- [ ] Ensure prompt text only exists in builder code (no docs embedding prompt content)

