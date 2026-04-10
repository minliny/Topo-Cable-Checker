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

## `run` Command Advanced Parameters

The `run` command now supports result delivery options:

| Parameter | Description | Default |
| --- | --- | --- |
| `--copy-result` | Copy result to clipboard | Enabled |
| `--no-copy-result` | Disable clipboard copy | - |
| `--open-result` | Open result file in PyCharm/IDE | Enabled |
| `--no-open-result` | Disable IDE opening | - |
| `--result-format` | Result output format (markdown/text) | markdown |
| `--max-issues` | Maximum issues to display | 20 |

### Minimal Examples

```bash
# Default behavior: Copy to clipboard + Open in PyCharm
python src/presentation/cli/main.py run --task <task_id>

# Disable all result delivery
python src/presentation/cli/main.py run --task <task_id> --no-copy-result --no-open-result

# Only copy, don't open
python src/presentation/cli/main.py run --task <task_id> --no-open-result

# Text format
python src/presentation/cli/main.py run --task <task_id> --result-format text
```

### Degradation Behavior

| Scenario | Behavior |
| --- | --- |
| Clipboard copy fails | Logs a warning, continues to write temp file and open it |
| Temp file write fails | Logs a warning, does not block the successful check result |
| PyCharm not found | Falls back to system default editor |
| PyCharm open fails | Logs a warning, does not block main flow |
| All deliveries fail | Check result still returns normally, CLI exit code remains 0 |
