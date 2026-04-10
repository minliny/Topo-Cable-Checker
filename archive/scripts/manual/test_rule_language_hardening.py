from src.domain.rule_compiler import RuleCompiler, RuleCompileError, TemplateRegistry

rule_definitions = {
    "rule_success_dsl_regex_with_and": {
        "rule_type": "dsl",
        "target_type": "devices",
        "expression": {
            "when": {
                "all": [
                    'device_type == "Switch"',
                    'status exists'
                ]
            },
            "assert": {
                "regex": {
                    "field": "device_name",
                    "pattern": "^SW-\\d{2}$"
                }
            }
        }
    },
    "rule_success_dsl_exists": {
        "rule_type": "dsl",
        "target_type": "ports",
        "expression": {
            "assert": {
                "exists": "port_status"
            }
        }
    },
    "rule_success_template": {
        "rule_type": "template",
        "target_type": "devices",
        "template": "threshold_check",
        "params": {
            "metric_type": "count",
            "threshold_key": "T1"
        }
    },
    "rule_error_unknown_type": {
        "rule_type": "magic",
        "target_type": "devices"
    },
    "rule_error_missing_param": {
        "rule_type": "template",
        "target_type": "devices",
        "template": "group_consistency",
        "params": {
            "group_key": "device_type"
        }
    },
    "rule_error_unsupported_target": {
        "rule_type": "dsl",
        "target_type": "aliens",
        "expression": {
            "assert": "status == active"
        }
    },
    "rule_error_invalid_dsl": {
        "rule_type": "dsl",
        "target_type": "devices",
        "expression": {
            "when": "unknown format here",
            "assert": "status == active"
        }
    }
}

compile_errors = []
compiled_rules = {}

for rule_id, rule_def in rule_definitions.items():
    try:
        compiled = RuleCompiler.compile(rule_id, rule_def)
        compiled_rules[rule_id] = compiled
    except RuleCompileError as e:
        compile_errors.append(e.to_dict())

print(f"compiled_success_count: {len(compiled_rules)}")
print(f"compile_error_count: {len(compile_errors)}")

print("\n--- COMPILED RULES ---")
for rule_id, compiled in compiled_rules.items():
    print(f"{rule_id}: {compiled}")

print("\n--- COMPILE ERRORS ---")
for err in compile_errors:
    print(err)
