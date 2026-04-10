from typing import List

from src.application.rule_editor_services.rule_schema_builder import RuleDraftSchema

class RuleSpecRenderer:
    """
    Builds rule specification document for human and external AI reading.
    Injects catalog constraints, required fields, and expected output formats.
    """
    
    @classmethod
    def build(cls, schema: RuleDraftSchema, user_input: str) -> str:
        prompt_parts = [
            "You are an AI rule generation assistant.",
            "Your task is to map the user's natural language request into a valid rule draft.",
            "You MUST ONLY use the rule types and fields defined by the provided schema.",
            "You MUST output your response as valid JSON only.",
            "",
            "### Output JSON Schema",
            "```json",
            "{",
            '  "rule_type": "string",',
            '  "target_type": "string",',
            '  "severity": "string",',
            '  "rule_definition": { "field": "value" }',
            "}",
            "```",
            "",
            "### General Constraints",
            "- Top-level MUST ONLY contain: rule_type, target_type, severity, rule_definition",
            "- rule_type MUST be one of the allowed rule types below.",
            "- rule_definition MUST be an object containing ONLY allowed fields for the selected rule_type.",
            "- Do not output any explanatory text outside of the JSON.",
            "- If you cannot determine a required field, output null or empty string to allow downstream validation to fail explicitly.",
            "",
            "### Allowed Rule Types and Field Constraints",
            "",
            f"User input: {user_input}",
        ]
        
        for rt in schema.rule_types:
            prompt_parts.append(f"\n#### Rule Type: `{rt.rule_type}`")
            if rt.summary:
                prompt_parts.append(f"Summary: {rt.summary}")
            if rt.supported_targets:
                prompt_parts.append(f"Supported targets: {', '.join(rt.supported_targets)}")
            prompt_parts.append("Fields:")
            for f in rt.fields:
                req = "REQUIRED" if f.required else "OPTIONAL"
                enum_info = f", ENUM: {f.enum_values}" if f.enum_values else ""
                default_info = f", DEFAULT: {f.default}" if f.default is not None else ""
                desc = f.description or ""
                prompt_parts.append(f"  - `{f.name}` ({f.field_type}): {req}{enum_info}{default_info} {desc}".strip())
                
        return "\n".join(prompt_parts)
