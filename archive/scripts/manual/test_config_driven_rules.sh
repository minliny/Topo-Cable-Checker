#!/bin/bash
set -e
export PYTHONPATH=/workspace

rm -f data/baselines.json

echo "1. Initialize Baseline with Config-Driven Rules"
python src/presentation/cli/main.py baseline list > /dev/null

echo "2. Create Task with test_config_driven_data.xlsx"
TASK_OUT=$(python src/presentation/cli/main.py task create --baseline B001 --file test_config_driven_data.xlsx)
TASK_ID=$(echo "$TASK_OUT" | awk '{print $3}')

echo "3. Run Pipeline"
python src/presentation/cli/main.py recognize --task $TASK_ID > /dev/null
python src/presentation/cli/main.py confirm-recognition --task $TASK_ID > /dev/null
RUN_OUT=$(python src/presentation/cli/main.py run --task $TASK_ID)
RUN_ID=$(echo "$RUN_OUT" | awk '{print $5}')

echo -e "\n--- RESULT SUMMARY ---"
python src/presentation/cli/main.py summary --run $RUN_ID

echo -e "\n--- ISSUES GENERATED ---"
python src/presentation/cli/main.py issues --run $RUN_ID

echo -e "\n--- RAW ISSUE JSON (Evidence inspection) ---"
cat data/issue_aggregates.json | grep -A 20 '"rule_id"' | head -n 40
