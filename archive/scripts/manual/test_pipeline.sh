#!/bin/bash
set -e
export PYTHONPATH=/workspace

echo "1. Initialize Baseline with 3 Rules"
python src/presentation/cli/main.py baseline list > /dev/null

echo "2. Create Task with test_network_data.xlsx"
TASK_OUT=$(python src/presentation/cli/main.py task create --baseline B001 --file test_network_data.xlsx)
TASK_ID=$(echo "$TASK_OUT" | awk '{print $3}')

echo "3. Recognize Excel Data"
python src/presentation/cli/main.py recognize --task $TASK_ID

echo "4. Confirm Recognition"
python src/presentation/cli/main.py confirm-recognition --task $TASK_ID

echo "5. Run Normalization & Rule Engine"
RUN_OUT=$(python src/presentation/cli/main.py run --task $TASK_ID)
RUN_ID=$(echo "$RUN_OUT" | awk '{print $5}')

echo -e "\n--- RESULT SUMMARY ---"
python src/presentation/cli/main.py summary --run $RUN_ID

echo -e "\n--- ISSUES GENERATED ---"
python src/presentation/cli/main.py issues --run $RUN_ID
