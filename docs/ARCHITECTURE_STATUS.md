# Architecture Status

The repository is organized around a 5-layer model, with some known deviations:
1. **Presentation**: FastAPI app in `src/presentation/api`, CLI entrypoints in `src/presentation/cli`, and `result_delivery.py` for result formatting and delivery. The React UI lives in `frontend/`.
2. **Application**: Orchestration services for rule governance (draft/publish/diff/history) and check-run flows (task/recognition/run/review/export).
3. **Domain**: Core business logic and models in `src/domain/` (RuleCompiler, RuleEngine, Executors, Facts, Result models).
4. **Infrastructure**: Adapters for external dependencies (Excel reader, JSON repositories).
5. **Cross-cutting**: Common utilities (logging, errors, config, clipboard, ide_launcher, temp_files) in `src/crosscutting/`.

**Current System Boundaries:**
- Presentation does not write JSON files directly; writes are performed via repositories.
- Application orchestrates state transitions, normalization, and rule execution, but currently imports concrete repository implementations in several places (dependency inversion is not fully enforced).
