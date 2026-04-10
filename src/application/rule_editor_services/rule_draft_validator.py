from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

from src.application.rule_editor_services.rule_schema_builder import RuleDraftSchema

@dataclass(frozen=True)
class DraftSchemaValidationError:
    code: str
    field: str
    message: str

@dataclass(frozen=True)
class DraftSchemaValidationResult:
    is_valid: bool
    schema_errors: List[DraftSchemaValidationError]
    candidate_rule_type: Optional[str]
    candidate_target_type: Optional[str]
    candidate_severity: Optional[str]
    candidate_rule_definition: Optional[Dict[str, Any]]

class RuleDraftValidator:
    _ALLOWED_TOP_LEVEL: Set[str] = {"rule_type", "target_type", "severity", "rule_definition"}

    @classmethod
    def validate(cls, raw_output: Any, schema: RuleDraftSchema) -> DraftSchemaValidationResult:
        errors: List[DraftSchemaValidationError] = []

        if not isinstance(raw_output, dict):
            errors.append(
                DraftSchemaValidationError(
                    code="invalid_top_level_shape",
                    field="_top",
                    message="Top-level output must be an object.",
                )
            )
            return DraftSchemaValidationResult(False, errors, None, None, None, None)

        unknown_top = [k for k in raw_output.keys() if k not in cls._ALLOWED_TOP_LEVEL]
        for k in unknown_top:
            errors.append(
                DraftSchemaValidationError(
                    code="unknown_top_level_field",
                    field=k,
                    message=f"Unknown top-level field: {k}",
                )
            )

        rule_type = raw_output.get("rule_type")
        target_type = raw_output.get("target_type")
        severity = raw_output.get("severity")
        rule_definition = raw_output.get("rule_definition")

        for top_field in ["rule_type", "target_type", "severity", "rule_definition"]:
            if top_field not in raw_output:
                errors.append(
                    DraftSchemaValidationError(
                        code="missing_required_field",
                        field=top_field,
                        message=f"Missing required top-level field: {top_field}",
                    )
                )

        if not isinstance(rule_type, str) or not rule_type.strip():
            errors.append(
                DraftSchemaValidationError(
                    code="invalid_rule_type",
                    field="rule_type",
                    message="rule_type must be a non-empty string.",
                )
            )
            return DraftSchemaValidationResult(False, errors, None, cls._as_str(target_type), cls._as_str(severity), cls._as_dict(rule_definition))

        rule_type_schema = next((rt for rt in schema.rule_types if rt.rule_type == rule_type), None)
        if rule_type_schema is None:
            errors.append(
                DraftSchemaValidationError(
                    code="unknown_rule_type",
                    field="rule_type",
                    message=f"Unknown rule_type: {rule_type}",
                )
            )
            return DraftSchemaValidationResult(False, errors, rule_type, cls._as_str(target_type), cls._as_str(severity), cls._as_dict(rule_definition))

        if not isinstance(target_type, str) or not target_type.strip():
            errors.append(
                DraftSchemaValidationError(
                    code="invalid_field_type",
                    field="target_type",
                    message="Expected string.",
                )
            )

        if not isinstance(severity, str) or not severity.strip():
            errors.append(
                DraftSchemaValidationError(
                    code="invalid_field_type",
                    field="severity",
                    message="Expected string.",
                )
            )

        if not isinstance(rule_definition, dict):
            errors.append(
                DraftSchemaValidationError(
                    code="invalid_rule_definition",
                    field="rule_definition",
                    message="rule_definition must be an object.",
                )
            )
            return DraftSchemaValidationResult(False, errors, rule_type, cls._as_str(target_type), cls._as_str(severity), None)

        allowed_fields = {f.name: f for f in rule_type_schema.fields}

        for fname in rule_definition.keys():
            if fname not in allowed_fields:
                errors.append(
                    DraftSchemaValidationError(
                        code="unknown_field",
                        field=f"rule_definition.{fname}",
                        message=f"Unknown field for rule_type '{rule_type}': {fname}",
                    )
                )

        for f in rule_type_schema.fields:
            if f.required:
                v = rule_definition.get(f.name)
                if v is None or (isinstance(v, str) and not v.strip()):
                    errors.append(
                        DraftSchemaValidationError(
                            code="missing_required_field",
                            field=f"rule_definition.{f.name}",
                            message=f"Missing required field: {f.name}",
                        )
                    )

        for f in rule_type_schema.fields:
            if f.name not in rule_definition:
                continue
            v = rule_definition.get(f.name)
            if v is None:
                continue

            if f.enum_values and v not in f.enum_values:
                errors.append(
                    DraftSchemaValidationError(
                        code="invalid_enum_value",
                        field=f"rule_definition.{f.name}",
                        message=f"Invalid enum value '{v}'. Must be one of: {f.enum_values}",
                    )
                )

            type_error = cls._check_type(v, f.field_type)
            if type_error:
                errors.append(
                    DraftSchemaValidationError(
                        code="invalid_field_type",
                        field=f"rule_definition.{f.name}",
                        message=type_error,
                    )
                )

        return DraftSchemaValidationResult(
            is_valid=(len(errors) == 0),
            schema_errors=errors,
            candidate_rule_type=rule_type,
            candidate_target_type=cls._as_str(target_type),
            candidate_severity=cls._as_str(severity),
            candidate_rule_definition=rule_definition,
        )

    @classmethod
    def _as_dict(cls, val: Any) -> Optional[Dict[str, Any]]:
        return val if isinstance(val, dict) else None

    @classmethod
    def _as_str(cls, val: Any) -> Optional[str]:
        return val if isinstance(val, str) else None

    @classmethod
    def _check_type(cls, val: Any, field_type: str) -> Optional[str]:
        if field_type in ["string", "select"]:
            return None if isinstance(val, str) else "Expected string."
        if field_type == "number":
            return None if isinstance(val, (int, float)) and not isinstance(val, bool) else "Expected number."
        if field_type == "integer":
            return None if isinstance(val, int) and not isinstance(val, bool) else "Expected integer."
        if field_type == "boolean":
            return None if isinstance(val, bool) else "Expected boolean."
        return None
