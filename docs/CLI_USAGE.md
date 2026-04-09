# CLI Usage

Use `checktool` commands to orchestrate checks:
- `python src/presentation/cli/main.py baseline list`
- `python src/presentation/cli/main.py task create --baseline <id> --file <path>`
- `python src/presentation/cli/main.py recognize --task <task_id>`
- `python src/presentation/cli/main.py confirm-recognition --task <task_id>`
- `python src/presentation/cli/main.py run --task <task_id>`
- `python src/presentation/cli/main.py summary --run <run_id>`
- `python src/presentation/cli/main.py issues --run <run_id>`
- `python src/presentation/cli/main.py review --run <run_id> --device <name>`
- `python src/presentation/cli/main.py diff --task <task_id> --prev <prev_id> --curr <curr_id>`
- `python src/presentation/cli/main.py export --run <run_id> --format json`
