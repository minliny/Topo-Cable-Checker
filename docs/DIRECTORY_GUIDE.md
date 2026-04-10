# Directory Guide

- `src/domain/`: Contains `CheckTask`, `TaskStatus`, `BaselineProfile`, and `ResultModels`.
- `src/application/`: Service modules (`task_services`, `check_run_services`, etc.) for orchestration.
- `src/presentation/`: Entry points including `cli/`, `local_web/`, and `result_delivery.py` for delivering results.
- `src/infrastructure/`: Connectors (Excel reader, DB, etc.).
- `src/crosscutting/`: Minimal capabilities (`errors`, `logging`, `config`, `ids`, `time`, `clipboard`, `temp_files`, `ide_launcher`).
