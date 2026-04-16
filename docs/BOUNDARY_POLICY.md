# Boundary Policy

*(Established in Phase C3.2 Boundary Hardening)*

This document outlines the strict architectural boundary rules for the project, aligned with **Route C (Hybrid Transitional Route)**. The goal is to decouple our systems from concrete infrastructure and reduce the cost of future migrations (e.g., to a DB, service split, or storage evolution).

## 1. Infrastructure Dependency Injection
- **Rule**: Application Services MUST NOT secretly fallback or instantiate concrete infrastructure.
- **Violation**: `self.repo = repo or BaselineRepository()`
- **Correct**: `def __init__(self, repo: BaselineRepository): self.repo = repo`
- **Why**: Allows complete testability via `InMemoryBaselineRepository` and paves the way for a smooth transition to a database repository without changing application logic.
- **Composition Root**: All concrete dependencies MUST be wired in the composition roots (`src/presentation/api/dependencies.py` for FastAPI and `src/presentation/cli/main.py` for CLI).

## 2. Presentation Layer Restrictions
- **Rule**: Presentation layer components (Routers, CLI) MUST NOT bypass the Application layer to directly access Domain internals or Repository internals.
- **Violation**: A router calling `RuleCompiler.compile()` directly, or reading `baseline.working_draft["some_internal_key"]` and making business decisions on it.
- **Correct**: The router calls an Application Service, which orchestrates the Domain objects and returns a clean DTO.
- **Why**: Keeps the presentation layer purely focused on request/response mapping and HTTP/CLI concerns.

## 3. Strict DTO Contracts (Outward-Facing Shapes)
- **Rule**: API Responses MUST NOT leak internal domain or persistence shapes (e.g., unstructured `Dict[str, Any]`).
- **Violation**: Returning `working_draft: dict` directly to the client without a strict Pydantic schema.
- **Correct**: Returning a strongly typed `RuleDefinitionDTO` that explicitly defines the contract.
- **Why**: Prevents the UI or external consumers from coupling to our internal JSON persistence schema, allowing us to refactor our internal domain without breaking API contracts.

## 4. Segregation of Repository Writes
- **Rule**: All file writes outside of the core domain repositories MUST be explicitly categorized and decoupled from business state.
- **Categorization**:
  - **Business State**: Managed exclusively by `BaselineRepository`, `TaskRepository`, etc. (Candidates for future DB migration).
  - **Infra Artifacts**: Exports, generated reports, etc. MUST be written via the `FileStorage` utility (e.g., `ExportFileStorage`), never directly via `open()`.
  - **Observation/Telemetry**: Handled by dedicated recorders (e.g., JSONL appending), entirely separate from the business domain.
- **Why**: When we migrate to a database, we need to know exactly what is "State" (moves to DB) and what is an "Artifact" (stays on S3/Disk).

## 5. Testing with Fakes
- **Rule**: Core application services MUST be verifiable using In-Memory Fakes (e.g., `InMemoryBaselineRepository`).
- **Why**: Proves that the service logic is decoupled from the file system and guarantees that the dependency injection is complete.

## Conclusion
This policy enforces that while we continue to use a file-based persistence model, our **boundaries remain honest**. By adhering to these constraints, we ensure that our application architecture remains highly resilient and that future migrations will be isolated, predictable, and cost-effective.
