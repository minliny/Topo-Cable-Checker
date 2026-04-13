import httpx
import time

client = httpx.Client()

url = "http://localhost:8000/api/rules/draft/save"
payload = {
    "baseline_id": "SIM_LARGE",
    "rule_id": "R_test",
    "rule_type": "threshold",
    "target_type": "devices",
    "severity": "warning",
    "params": {"metric_type": "count", "threshold_key": "T1"}
}

start = time.time()
for _ in range(10):
    res = client.post(url, json=payload)
    assert res.status_code == 200
print(f"10 Save Drafts took {time.time() - start:.2f}s")

val_url = "http://localhost:8000/api/rules/draft/validate"
start = time.time()
for _ in range(10):
    res = client.post(val_url, json={"rule_type": "threshold", "params": payload["params"]})
    assert res.status_code == 200
print(f"10 Validates took {time.time() - start:.2f}s")

pub_url = "http://localhost:8000/api/rules/publish"
start = time.time()
for i in range(10):
    res = client.post(pub_url, params={"baseline_id": "SIM_LARGE"}, json={"rule_type": "threshold", "target_type": "devices", "severity": "warning", "params": payload["params"]})
    # print(res.json())
print(f"10 Publishes attempted took {time.time() - start:.2f}s")

diff_url = "http://localhost:8000/api/baselines/SIM_LARGE/diff?from_version=draft&to_version=previous_version"
start = time.time()
for _ in range(10):
    res = client.get(diff_url)
print(f"10 Diffs took {time.time() - start:.2f}s")

