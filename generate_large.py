import json

large_baseline = {
  "baseline_id": "SIM_LARGE",
  "baseline_version": "v1.0",
  "recognition_profile": { "strategy": "excel_basic" },
  "naming_profile": { "strategy": "snake_case" },
  "rule_set": {},
  "parameter_profile": {},
  "threshold_profile": {},
  "baseline_version_snapshot": {},
  "version_history_meta": {}
}

for i in range(1000):
    large_baseline["rule_set"][f"R_large_{i}"] = {
        "rule_type": "threshold",
        "template": "threshold_check",
        "target_type": "devices",
        "severity": "warning",
        "params": { "metric_type": "count", "threshold_key": f"T{i}" }
    }

with open("/workspace/data/baselines.json", "r") as f:
    data = json.load(f)

data["SIM_LARGE"] = large_baseline

with open("/workspace/data/baselines.json", "w") as f:
    json.dump(data, f)
print("Large baseline added!")
