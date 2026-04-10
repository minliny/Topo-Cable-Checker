import yaml
from src.application.rule_governance_service import RuleGovernanceService
from src.application.baseline_services.baseline_service import BaselineService

# Ensure Baseline B001 exists with rules
baseline_service = BaselineService()
baseline_service.list_baselines()

gov_service = RuleGovernanceService()

print("--- 1. List Rule Definitions ---")
rules = gov_service.list_rule_definitions("B001")
print(f"Total Rules Found: {len(rules)}")
for r in rules:
    print(f" - {r.rule_id} (Type: {r.rule_type}, Target: {r.target_type}, Status: {r.enabled})")

print("\n--- 2. Get Compiled Rule / Compile Error ---")
errors = gov_service.list_compile_errors("B001")
print(f"Compile Errors: {len(errors)}")
for err in errors:
    print(f" - Error in {err.rule_id}: [{err.error_type}] {err.message}")

if rules:
    rule_id = rules[0].rule_id
    compiled = gov_service.get_compiled_rule("B001", rule_id)
    if compiled:
        print(f"Compiled {rule_id} Executor: {compiled.compiled_executor}")

print("\n--- 3. Validate Rule Definition ---")
valid, err = gov_service.validate_rule_definition({
    "language_version": "v2.0",
    "rule_type": "dsl"
})
print(f"Validation Result: {valid}")
if err:
    print(f"Validation Error: [{err.error_type}] {err.message}")

print("\n--- 4. List Template Registry ---")
templates = gov_service.list_template_registry()
print(f"Templates Found: {len(templates)}")
for t in templates:
    print(f" - {t.template_name} -> {t.target_executor}")

print("\n--- GOVERNANCE TRACE EXAMPLE ---")
if rules:
    rule_id = rules[0].rule_id
    compiled = gov_service.get_compiled_rule("B001", rule_id)
    trace = {
        "baseline_version": rules[0].baseline_version,
        "rule_id": rule_id,
        "language_version": rules[0].language_version,
        "compile_status": "success" if compiled else "failure"
    }
    print(yaml.dump({"governance_trace_example": trace}, sort_keys=False))

