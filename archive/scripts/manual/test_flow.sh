#!/bin/bash
set -e

# Initialize python path
export PYTHONPATH=/workspace

echo "1. List baselines"
python src/presentation/cli/main.py baseline list

echo -e "\n2. Create Task"
TASK_OUT=$(python src/presentation/cli/main.py task create --baseline B001 --file test.xlsx)
echo "$TASK_OUT"
TASK_ID=$(echo "$TASK_OUT" | awk '{print $3}')

echo -e "\n[Status Check]"
python src/presentation/cli/main.py status --task $TASK_ID

echo -e "\n3. Recognize Data"
python src/presentation/cli/main.py recognize --task $TASK_ID

echo -e "\n[Status Check]"
python src/presentation/cli/main.py status --task $TASK_ID

echo -e "\n4. Confirm Recognition"
python src/presentation/cli/main.py confirm-recognition --task $TASK_ID

echo -e "\n[Status Check]"
python src/presentation/cli/main.py status --task $TASK_ID

echo -e "\n5. Run Checks (First Run)"
RUN_OUT=$(python src/presentation/cli/main.py run --task $TASK_ID)
echo "$RUN_OUT"
RUN_ID_1=$(echo "$RUN_OUT" | awk '{print $5}')

echo -e "\n[Status Check]"
python src/presentation/cli/main.py status --task $TASK_ID

echo -e "\n6. View Summary"
python src/presentation/cli/main.py summary --run $RUN_ID_1

echo -e "\n7. View Issues"
python src/presentation/cli/main.py issues --run $RUN_ID_1

echo -e "\n8. Review Issues"
python src/presentation/cli/main.py review --run $RUN_ID_1 --device Device_A

echo -e "\n9. Export Results"
python src/presentation/cli/main.py export --run $RUN_ID_1 --format json

echo -e "\n10. Re-Run to get second Run ID"
# Reset task status to ready_to_check to simulate a recheck flow
python -c "
from src.infrastructure.repository import TaskRepository
from src.domain.task_model import TaskStatus
repo = TaskRepository()
t = repo.get_by_id('$TASK_ID')
t.task_status = TaskStatus.ready_to_check
repo.save(t)
"
RUN_OUT_2=$(python src/presentation/cli/main.py run --task $TASK_ID)
echo "$RUN_OUT_2"
RUN_ID_2=$(echo "$RUN_OUT_2" | awk '{print $5}')

echo -e "\n11. Run Diff"
python src/presentation/cli/main.py diff --task $TASK_ID --prev $RUN_ID_1 --curr $RUN_ID_2

