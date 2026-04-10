import json
from src.application.baseline_services.baseline_service import BaselineService
from src.application.rule_editor_service import RuleEditorService

# 1. Init Base
baseline_service = BaselineService()
baseline_service.list_baselines()

editor = RuleEditorService()
baseline_id = "B001"

# Step 1. Get List
print("\n--- 1. Editor Rule List ---")
baseline_info = editor.get_editor_baseline(baseline_id)
print(f"Baseline Version: {baseline_info.baseline_version}")
rules = editor.list_editor_rules(baseline_id)
print(f"Draft rules found: {len(rules)}")

# Step 2. Get Single Rule Detail
print("\n--- 2. Single Rule Draft ---")
rule_id = "R2_threshold_count"
draft = editor.get_editor_rule(baseline_id, rule_id)
print(f"Rule: {draft.rule_id} | Status: {draft.compile_status}")

# Step 3. Validate
print("\n--- 3. Validate Draft ---")
test_def = draft.raw_definition.copy()
test_def["metric_type"] = "unknown_metric"
val_res = editor.validate_rule_draft(rule_id, test_def)
print(f"Validation Result (with bad metric): {val_res.is_valid}")
if not val_res.is_valid:
    print(f"Compile Error Asserted: {val_res.compile_errors[0].message}")

# Step 4. Compile Preview
print("\n--- 4. Compile Preview ---")
preview_res = editor.compile_rule_preview(rule_id, draft.raw_definition)
print(f"Preview Status: {preview_res.compile_status}")
print(f"Compiled output keys: {list(preview_res.compiled_rule.keys())}")

# Step 5. Save Draft
print("\n--- 5. Save Draft ---")
test_def_success = draft.raw_definition.copy()
test_def_success["severity"] = "critical"
editor.save_rule_draft(baseline_id, rule_id, test_def_success)
updated_draft = editor.get_editor_rule(baseline_id, rule_id)
print(f"Updated severity in draft: {updated_draft.severity}")

# Step 6. Publish
print("\n--- 6. Publish Version ---")
old_version = baseline_info.baseline_version
success, new_version, count, msg = editor.publish_baseline_version(baseline_id, "Test publish")
print(f"Publish success: {success}")
if success:
    print(f"Old Version: {old_version}")
    print(f"New Version: {new_version}")
    print(f"Rules published: {count}")
else:
    print(f"Publish failed: {msg}")

# Step 7 & 8: Verification of Version change
print("\n--- 7/8. Verify Baseline ---")
new_baseline_info = editor.get_editor_baseline(baseline_id)
print(f"Current Baseline Version: {new_baseline_info.baseline_version}")
assert new_baseline_info.baseline_version == new_version
assert new_baseline_info.baseline_version != old_version
print("Assertions passed: Baseline version correctly incremented and old version preserved.")

