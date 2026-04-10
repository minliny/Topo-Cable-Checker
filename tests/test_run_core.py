import pytest
import os
import subprocess
import json

def test_cli_run_without_optional():
    # Setup: Create a task
    res = subprocess.run(
        ["python", "-m", "src.presentation.cli.main", "task", "create", "--baseline", "B001", "--file", "data/samples/test.xlsx"],
        capture_output=True, text=True
    )
    assert res.returncode == 0
    task_id = res.stdout.strip().split()[-1]
    
    # Recognize
    subprocess.run(["python", "-m", "src.presentation.cli.main", "recognize", "--task", task_id], capture_output=True)
    subprocess.run(["python", "-m", "src.presentation.cli.main", "confirm-recognition", "--task", task_id], capture_output=True)
    
    # Run core flow WITHOUT --copy or --open
    res_run = subprocess.run(
        ["python", "-m", "src.presentation.cli.main", "run", "--task", task_id],
        capture_output=True, text=True
    )
    
    assert res_run.returncode == 0
    assert "Run completed" in res_run.stdout
    assert "ResultDelivery triggered" not in res_run.stdout
    assert "IDE launched" not in res_run.stdout
