import requests
import time
import json
from pprint import pprint

BASE_URL = "http://127.0.0.1:8000/api"

print("Starting W16 Recovery Validation...")

# A. Multi-rule Draft Recovery Validation
print("\n--- A. Multi-rule Draft Recovery Validation ---")
# Get baselines
res = requests.get(f"{BASE_URL}/baselines")
baselines = res.json()
baseline_id = baselines[0]['id'] if baselines else "B001"
print(f"Using baseline: {baseline_id}")

# A1. Save full rule_set draft
# The endpoint is /rules/draft/save
print("\n[A1] Saving draft with multi rules...")
# Does the endpoint accept rule_set? Let's try sending multiple rules or rule_set
payload = {
    "baseline_id": baseline_id,
    "rule_id": "rule_1",
    "rule_type": "threshold",
    "target_type": "devices",
    "severity": "warning",
    "params": {"key": "val1"}
}
res = requests.post(f"{BASE_URL}/rules/draft/save", json=payload)
print("Save draft status:", res.status_code)
if res.status_code == 200:
    print("Response:", res.json())

# Load draft
res = requests.get(f"{BASE_URL}/rules/draft/{baseline_id}")
print("Load draft status:", res.status_code)
if res.status_code == 200:
    draft = res.json()
    print("Draft has_draft:", draft.get("has_draft"))
    print("Draft data keys:", list(draft.get("draft_data", {}).keys()))

