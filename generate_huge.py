import json
with open("/workspace/data/baselines.json", "r") as f:
    data = json.load(f)

for i in range(10000):
    data["SIM_LARGE"]["rule_set"][f"R_huge_{i}"] = {
        "rule_type": "threshold",
        "template": "threshold_check",
        "target_type": "devices",
        "severity": "warning",
        "params": { "metric_type": "count", "threshold_key": f"T{i}" }
    }

with open("/workspace/data/baselines.json", "w") as f:
    json.dump(data, f)
