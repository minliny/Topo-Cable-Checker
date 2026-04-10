#!/bin/bash
set -e
export PYTHONPATH=/workspace

echo "=== RUN 1 (V1) ==="
TASK_OUT1=$(python src/presentation/cli/main.py task create --baseline B001 --file test_network_data.xlsx)
TASK_ID1=$(echo "$TASK_OUT1" | awk '{print $3}')
python src/presentation/cli/main.py recognize --task $TASK_ID1 > /dev/null
python src/presentation/cli/main.py confirm-recognition --task $TASK_ID1 > /dev/null
RUN_OUT1=$(python src/presentation/cli/main.py run --task $TASK_ID1)
RUN_ID1=$(echo "$RUN_OUT1" | awk '{print $5}')
python src/presentation/cli/main.py issues --run $RUN_ID1

echo -e "\n=== RUN 2 (V2) ==="
TASK_OUT2=$(python src/presentation/cli/main.py task create --baseline B001 --file test_network_data_v2.xlsx)
TASK_ID2=$(echo "$TASK_OUT2" | awk '{print $3}')
python src/presentation/cli/main.py recognize --task $TASK_ID2 > /dev/null
python src/presentation/cli/main.py confirm-recognition --task $TASK_ID2 > /dev/null
RUN_OUT2=$(python src/presentation/cli/main.py run --task $TASK_ID2)
RUN_ID2=$(echo "$RUN_OUT2" | awk '{print $5}')
python src/presentation/cli/main.py issues --run $RUN_ID2

echo -e "\n=== RECHECK DIFF ==="
python src/presentation/cli/main.py diff --task $TASK_ID2 --prev $RUN_ID1 --curr $RUN_ID2

