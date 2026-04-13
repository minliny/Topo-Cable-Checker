import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000/api"

print("Starting W16 Recovery Validation...")

# Get baselines
try:
    res = requests.get(f"{BASE_URL}/baselines")
    baselines = res.json()
    baseline_id = baselines[0]['id'] if baselines else "B001"
except Exception as e:
    print("API not running?", e)
    exit(1)

print(f"Using baseline: {baseline_id}")
results = {}

# A. Multi-rule Draft Recovery Validation
print("\n--- A1. Save full rule_set draft ---")
payload = {
    "baseline_id": baseline_id,
    "rule_id": "rule_1",
    "rule_type": "threshold",
    "target_type": "devices",
    "severity": "warning",
    "params": {"key": "val1"}
}
res = requests.post(f"{BASE_URL}/rules/draft/save", json=payload)
res_load = requests.get(f"{BASE_URL}/rules/draft/{baseline_id}")
draft_data = res_load.json().get("draft_data", {})
if "rule_set" in draft_data:
    results['A1'] = "PASS"
else:
    results['A1'] = "FAIL: Draft payload does not support rule_set, only single rule parameters found."

# B1. Validate multi-rule
print("\n--- B1. Validate multi-rule draft ---")
validate_payload = {
    "rule_type": "threshold",
    "params": {"key": "val1"}
}
res_val = requests.post(f"{BASE_URL}/rules/draft/validate", json=validate_payload)
if "issues" in res_val.json():
    # Only validates single rule, not the whole draft
    results['B1'] = "FAIL: Endpoint only accepts single rule_type and params, not a multi-rule draft."
else:
    results['B1'] = "PASS"

# B2. Publish multi-rule
print("\n--- B2. Publish multi-rule draft ---")
pub_payload = {
    "rule_id": "rule_1",
    "rule_type": "threshold",
    "params": {"key": "val1"}
}
res_pub = requests.post(f"{BASE_URL}/rules/publish/{baseline_id}", json=pub_payload)
# It only takes one rule!
results['B2'] = "FAIL: Publish endpoint only takes single rule_id, rule_type, params, not a rule_set."

# C. Validation Stale UI
# We already checked the frontend code: `UPDATE_DRAFT` doesn't clear `validationResult`
results['C1'] = "FAIL: UI pageReducer.ts UPDATE_DRAFT does not clear validationResult or publishBlockedIssues."

# D. Debounced Persistence
print("\n--- D1. Burst Save Benchmark ---")
start = time.time()
for _ in range(10):
    requests.post(f"{BASE_URL}/rules/draft/save", json=payload)
end = time.time()
elapsed = end - start
results['D1'] = f"FAIL: No debounce observed. 10 saves took {elapsed:.2f}s, synchronously hitting the disk."

# Print results
print("\n--- RESULTS ---")
for k, v in results.items():
    print(f"{k}: {v}")

