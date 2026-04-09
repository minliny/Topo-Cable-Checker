import requests
import subprocess
import time
import os

print("--- Acceptance Test: Setup ---")
env = dict(os.environ, PYTHONPATH="/workspace")

# Create task and run it using CLI to populate data
out = subprocess.check_output(["python", "src/presentation/cli/main.py", "task", "create", "--baseline", "B001", "--file", "test_network_data.xlsx"], env=env).decode()
task_id = out.split()[-1].strip()

subprocess.run(["python", "src/presentation/cli/main.py", "recognize", "--task", task_id], env=env, check=True)

# Start web server in background
print("--- Starting Web Server ---")
server = subprocess.Popen(["python", "src/presentation/local_web/main.py"], env=env)
time.sleep(2)

try:
    print("\n--- Acceptance Test: Confirm Recognition (Web) ---")
    resp = requests.post(f"http://localhost:8000/task/{task_id}/confirm", allow_redirects=False)
    assert resp.status_code == 303, f"Expected 303 Redirect, got {resp.status_code}"
    
    print("\n--- Acceptance Test: Run Checks & Export (CLI) ---")
    out = subprocess.check_output(["python", "src/presentation/cli/main.py", "run", "--task", task_id], env=env).decode()
    run_id = out.split()[-1].strip()
    subprocess.run(["python", "src/presentation/cli/main.py", "review", "--run", run_id, "--device", "SW-01"], env=env, check=True)
    subprocess.run(["python", "src/presentation/cli/main.py", "export", "--run", run_id, "--format", "json"], env=env, check=True)

    print("\n--- Acceptance Test: View Overview & Filter Issues (Web) ---")
    # No filter
    resp = requests.get(f"http://localhost:8000/run/{run_id}")
    assert "Run Overview" in resp.text
    assert "Showing 4 issues" in resp.text
    
    # With filter
    resp = requests.get(f"http://localhost:8000/run/{run_id}?severity=medium&rule_id=R2")
    assert "Showing 2 issues" in resp.text

    print("\n--- Acceptance Test: View Review Context (Web) ---")
    resp = requests.get(f"http://localhost:8000/review/{run_id}/SW-01")
    assert "Review Device: SW-01" in resp.text

    print("\n--- Acceptance Test: View Export Artifact (Web) ---")
    resp = requests.get(f"http://localhost:8000/download/{run_id}/json")
    assert resp.status_code == 200
    assert len(resp.content) > 0

    print("\nALL ACCEPTANCE TESTS PASSED!")

finally:
    server.terminate()
