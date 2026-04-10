from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from src.application.rule_catalog_services.rule_catalog_presentation_service import (
    RuleCatalogPresentationService, 
    RulePreviewDTO, 
    RuleFormDefinitionDTO
)

@dataclass
class RuleTypeListItemView:
    rule_type: str
    display_name: str
    category: str
    description: str

@dataclass
class RuleFormView:
    rule_type: str
    form_definition: RuleFormDefinitionDTO
    initial_data: Dict[str, Any]

@dataclass
class RuleDraftValidationResult:
    is_valid: bool
    errors: Dict[str, str]  # field_name -> error_message
    
@dataclass
class RuleDraftView:
    rule_id: str
    rule_type: str
    target_type: str
    severity: str
    params: Dict[str, Any]
    validation_result: Optional[RuleDraftValidationResult] = None
    
    def to_rule_def(self) -> Dict[str, Any]:
        """Converts the draft to the dictionary format expected by the compiler."""
        return {
            "rule_type": "template",  # Defaulting to template for catalog-driven rules
            "template": self.rule_type,
            "target_type": self.target_type,
            "severity": self.severity,
            "params": self.params
        }

class RuleEditorMVPService:
    """
    A minimal viable product (MVP) service representing the backend for a Rule Editor UI.
    It solely consumes the RuleCatalogPresentationService to drive the UI flow.
    """
    
    def list_available_rule_types(self) -> List[RuleTypeListItemView]:
        previews = RuleCatalogPresentationService.list_rule_previews()
        return [
            RuleTypeListItemView(
                rule_type=p.rule_type,
                display_name=p.display_name,
                category=p.category,
                description=p.description
            )
            for p in previews
        ]
        
    def get_rule_preview(self, rule_type: str) -> Optional[RulePreviewDTO]:
        return RuleCatalogPresentationService.get_rule_preview(rule_type)
        
    def create_new_rule_form(self, rule_type: str) -> Optional[RuleFormView]:
        form_def = RuleCatalogPresentationService.get_rule_form_definition(rule_type)
        if not form_def:
            return None
            
        initial_data = form_def.default_example.copy() if form_def.default_example else {}
        
        return RuleFormView(
            rule_type=rule_type,
            form_definition=form_def,
            initial_data=initial_data
        )
        
    def validate_and_build_draft(
        self, 
        rule_id: str, 
        rule_type: str, 
        target_type: str, 
        severity: str, 
        form_data: Dict[str, Any]
    ) -> RuleDraftView:
        form_def = RuleCatalogPresentationService.get_rule_form_definition(rule_type)
        if not form_def:
            return RuleDraftView(
                rule_id=rule_id, rule_type=rule_type, target_type=target_type, 
                severity=severity, params=form_data,
                validation_result=RuleDraftValidationResult(False, {"_base": f"Unknown rule type: {rule_type}"})
            )
            
        errors = {}
        
        # Validate target_type
        if target_type not in form_def.supported_targets:
            errors["target_type"] = f"Unsupported target type: {target_type}. Supported: {form_def.supported_targets}"
            
        # Validate form fields based on parameter_fields definition
        for field in form_def.parameter_fields:
            field_val = form_data.get(field.field_name)
            
            # Check required
            if field.required and (field_val is None or str(field_val).strip() == ""):
                errors[field.field_name] = f"Field '{field.field_name}' is required."
                continue
                
            # Check enum options if present
            if field_val is not None and field.enum_options and field_val not in field.enum_options:
                errors[field.field_name] = f"Invalid value '{field_val}'. Must be one of: {field.enum_options}"
                
        is_valid = len(errors) == 0
        
        return RuleDraftView(
            rule_id=rule_id,
            rule_type=rule_type,
            target_type=target_type,
            severity=severity,
            params=form_data,
            validation_result=RuleDraftValidationResult(is_valid, errors)
        )
