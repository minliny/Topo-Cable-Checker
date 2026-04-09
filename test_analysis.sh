#!/bin/bash
set -e
export PYTHONPATH=/workspace

echo "1. Create Task with test_network_data.xlsx"
TASK_OUT=$(python src/presentation/cli/main.py task create --baseline B001 --file test_network_data.xlsx)
TASK_ID=$(echo "$TASK_OUT" | awk '{print $3}')

echo "2. Recognize Excel Data"
python src/presentation/cli/main.py recognize --task $TASK_ID > /dev/null

echo "3. Confirm Recognition"
python src/presentation/cli/main.py confirm-recognition --task $TASK_ID > /dev/null

echo "4. Run Checks & Analysis Pipeline"
RUN_OUT=$(python src/presentation/cli/main.py run --task $TASK_ID)
RUN_ID=$(echo "$RUN_OUT" | awk '{print $5}')

echo -e "\n--- STATISTICS LAYER ---"
python src/presentation/cli/main.py statistics --run $RUN_ID

echo -e "\n--- AGGREGATE LAYER ---"
python src/presentation/cli/main.py issues --run $RUN_ID

echo -e "\n--- REVIEW CONTEXT (SW-01) ---"
python src/presentation/cli/main.py review --run $RUN_ID --device SW-01
