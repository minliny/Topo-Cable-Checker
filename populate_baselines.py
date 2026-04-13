import json
import glob

baselines = {}
for path in glob.glob("/workspace/samples/usage_simulation/*.json"):
    with open(path, "r") as f:
        data = json.load(f)
        if "baseline" in data:
            baseline = data["baseline"]
            baselines[baseline["baseline_id"]] = baseline

with open("/workspace/data/baselines.json", "w") as f:
    json.dump(baselines, f, indent=2)
print("Baselines populated!")
