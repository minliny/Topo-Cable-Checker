import yaml
from src.domain.rule_compiler import RuleCompiler, RuleCompileError

with open("tests/rule_language_matrix.yaml", "r") as f:
    matrix = yaml.safe_load(f)

results = {
    "total_cases": 0,
    "dsl_success_cases": 0,
    "template_success_cases": 0,
    "compile_error_cases": 0
}

for case in matrix.get("dsl_success_cases", []):
    results["total_cases"] += 1
    try:
        compiled = RuleCompiler.compile(case["case_id"], case["input_rule"])
        assert compiled["executor"] == case["expected_executor"]
        assert compiled["scope_selector"]["target_type"] == case["expected_target_type"]
        results["dsl_success_cases"] += 1
    except Exception as e:
        print(f"Failed DSL success case {case['case_id']}: {e}")

for case in matrix.get("template_success_cases", []):
    results["total_cases"] += 1
    try:
        compiled = RuleCompiler.compile(case["case_id"], case["input_rule"])
        assert compiled["executor"] == case["expected_executor"]
        assert compiled["scope_selector"]["target_type"] == case["expected_target_type"]
        results["template_success_cases"] += 1
    except Exception as e:
        print(f"Failed Template success case {case['case_id']}: {e}")

for case in matrix.get("compile_error_cases", []):
    results["total_cases"] += 1
    try:
        compiled = RuleCompiler.compile(case["case_id"], case["input_rule"])
        print(f"Failed Compile Error case {case['case_id']}: Expected error but compiled successfully")
    except RuleCompileError as e:
        if e.error_type == case["expected_error"]:
            results["compile_error_cases"] += 1
        else:
            print(f"Failed Compile Error case {case['case_id']}: Expected {case['expected_error']}, got {e.error_type}")

print(yaml.dump({"test_matrix_summary": results}, sort_keys=False))

# Capture example for output
try:
    RuleCompiler.compile("err_unsupported_language_version", {
        "language_version": "v2.0",
        "rule_type": "dsl"
    })
except RuleCompileError as e:
    print(yaml.dump({"versioning_example": e.to_dict()}, sort_keys=False))
