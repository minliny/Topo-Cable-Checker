# Directory Guide

- `src/domain/`: Contains `CheckTask`, `TaskStatus`, `BaselineProfile`, and `ResultModels`.
- `src/application/`: Service modules (`task_services`, `check_run_services`, etc.) for orchestration.
- `src/presentation/cli/`: Minimal CLI `main.py` entrypoint.
- `src/infrastructure/`: Connectors (Excel reader, DB, etc.).
- `src/crosscutting/`: Minimal capabilities (`errors`, `logging`, `config`, `ids`, `time`).
