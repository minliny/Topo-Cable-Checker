# Architecture Status

The current architecture follows a strict 5-layer model:
1. **Presentation**: CLI entrypoints in `src/presentation/cli`.
2. **Application**: Orchestration services split by responsibility in `src/application/`.
3. **Domain**: Core business logic and models in `src/domain/`.
4. **Infrastructure**: Adapters for external dependencies in `src/infrastructure/`.
5. **Cross-cutting**: Common utilities (logging, errors, config, etc.) in `src/crosscutting/`.

**Status:**
- `src/core` and `src/app` have been removed or do not exist.
- Single execution path strictly enforced via the Application layer.
