import json
import yaml
from src.application.baseline_services.baseline_service import BaselineService
from src.application.rule_editor_service import RuleEditorService

baseline_service = BaselineService()
baseline_service.list_baselines()

editor = RuleEditorService()
baseline_id = "B001"

print("\n--- 1. Initial State ---")
initial_baseline = editor.get_editor_baseline(baseline_id)
v1_version = initial_baseline.baseline_version
print(f"Initial Version: {v1_version}")

print("\n--- 2. Add / Modify Rules and Publish ---")
# Modify an existing rule
draft1 = editor.get_editor_rule(baseline_id, "R1_scoped")
modified_def = draft1.raw_definition.copy()
modified_def["severity"] = "critical"
editor.save_rule_draft(baseline_id, "R1_scoped", modified_def)

# Add a new rule
new_rule = {
    "rule_type": "dsl",
    "target_type": "devices",
    "severity": "medium",
    "expression": {"when": "device_type == \"Switch\"", "assert": "status == \"active\""}
}
editor.save_rule_draft(baseline_id, "R_NEW_1", new_rule)

# Remove a rule
editor._draft_workspace[baseline_id].pop("R3_threshold_distinct", None)

success, v2_version, count, msg = editor.publish_baseline_version(baseline_id, "Productization Test")
print(f"Published {v2_version}: {success}")

print("\n--- 3. Test Baseline History ---")
versions = editor.list_baseline_versions(baseline_id)
print(f"Total Versions: {len(versions)}")
for v in versions:
    print(f" - {v.baseline_version} ({v.rule_count} rules)")
history_output = {"baseline_history": {"versions": [v.baseline_version for v in versions]}}

print("\n--- 4. Test Baseline Diff ---")
diff = editor.get_baseline_diff(baseline_id, v1_version, v2_version)
print(f"Diff Added: {len(diff.added_rules)}")
print(f"Diff Removed: {len(diff.removed_rules)}")
print(f"Diff Modified: {len(diff.modified_rules)}")
for m in diff.modified_rules:
    print(f" - {m.rule_id} changed: {m.changed_fields}")

diff_output = {
    "rule_diff_example": {
        "added": len(diff.added_rules),
        "removed": len(diff.removed_rules),
        "modified": len(diff.modified_rules),
        "modified_detail": [{"rule_id": m.rule_id, "changed_fields": m.changed_fields, "before": m.before, "after": m.after} for m in diff.modified_rules]
    }
}

print("\n--- 5. Test Rollback ---")
success, v3_version, msg = editor.rollback_to_version(baseline_id, v1_version)
print(f"Rollback to {v1_version} success: {success}, New Version: {v3_version}")

rollback_output = {
    "rollback_example": {
        "from": v1_version,
        "new_version": v3_version
    }
}

print("\n--- MUST OUTPUT CONTENTS ---")
print(yaml.dump(diff_output, sort_keys=False))
print(yaml.dump(history_output, sort_keys=False))
print(yaml.dump(rollback_output, sort_keys=False))

