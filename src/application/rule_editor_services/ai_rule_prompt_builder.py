import json
from typing import List
from src.application.rule_catalog_services.rule_catalog_presentation_service import RuleCatalogPresentationService

class AiRulePromptBuilder:
    """
    Builds the system prompt and instructions for the AI Rule Generation Agent.
    Injects catalog constraints, required fields, and expected output formats.
    """
    
    @classmethod
    def build_system_prompt(cls) -> str:
        rule_previews = RuleCatalogPresentationService.list_rule_previews()
        
        prompt_parts = [
            "You are an AI rule generation assistant.",
            "Your task is to map the user's natural language request into a valid rule draft.",
            "You MUST ONLY use the rule types and fields defined below.",
            "You MUST output your response in valid JSON format matching the schema exactly.",
            "",
            "### Output JSON Schema",
            "```json",
            "{",
            '  "rule_type": "string (the selected rule type)",',
            '  "target_type": "string (the selected target type)",',
            '  "severity": "string (low, medium, high, critical)",',
            '  "rule_definition": {',
            '    "field1": "value1",',
            '    "field2": "value2"',
            "  }",
            "}",
            "```",
            "",
            "### General Constraints",
            "- DO NOT invent any rule types, fields, or target types.",
            "- DO NOT output explanatory text outside of the JSON.",
            "- If you cannot determine a required field, provide an empty string or null to let the downstream validation catch it.",
            "",
            "### Available Rule Types and Constraints"
        ]
        
        for preview in rule_previews:
            form_def = RuleCatalogPresentationService.get_rule_form_definition(preview.rule_type)
            if not form_def:
                continue
                
            prompt_parts.append(f"\n#### Rule Type: `{preview.rule_type}`")
            prompt_parts.append(f"Name: {preview.display_name}")
            prompt_parts.append(f"Description: {preview.description}")
            prompt_parts.append(f"Supported Targets: {', '.join(form_def.supported_targets)}")
            
            capabilities = [f"- {cap.description}" for cap in form_def.capabilities]
            prompt_parts.append("Capabilities:\n" + "\n".join(capabilities))
            
            prompt_parts.append("Fields:")
            for field in form_def.parameter_fields:
                req = "REQUIRED" if field.required else "OPTIONAL"
                enum_info = f", ENUM: {field.enum_options}" if field.enum_options else ""
                default_info = f", DEFAULT: {field.default_value}" if field.default_value is not None else ""
                prompt_parts.append(f"  - `{field.field_name}` ({field.field_type}): {req}{enum_info}{default_info} - {field.help_text}")
                
        return "\n".join(prompt_parts)
