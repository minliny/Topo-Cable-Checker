# Architecture Status

The current architecture follows a strict 5-layer model:
1. **Presentation**: CLI entrypoints in `src/presentation/cli`, Local Web UI in `src/presentation/local_web`, and `result_delivery.py` for result output formatting and delivery. Both interact only with the Application layer using DTOs.
2. **Application**: Orchestration services and Query services. Query services act as an anti-corruption layer (ACL) mapping Domain entities to DTOs.
3. **Domain**: Core business logic and models in `src/domain/`. Includes Rule Engine, Facts, and structured Result models.
4. **Infrastructure**: Adapters for external dependencies. Includes `ExcelReader` (openpyxl) and JSON-based `Repository`.
5. **Cross-cutting**: Common utilities (logging, errors, config, clipboard, ide_launcher, temp_files) in `src/crosscutting/`.

**Current System Boundaries:**
- The Presentation layer cannot read or modify the Repository directly.
- The Application layer handles all state transitions, normalization, and rule execution.
- Data flows purely via DTO contracts between Application and Presentation.
