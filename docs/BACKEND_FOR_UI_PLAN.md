# Backend For UI (BFF) Minimum API Surface Plan

## 1. Backend Capability Audit Conclusion

### Current Status
The current repository (`/workspace/src`) contains a solid Domain/Application core designed for a CLI tool and an old SSR (Jinja2) interface. It uses a file-based JSON repository (`data/baselines.json`) to store `BaselineProfile` objects. **However, it completely lacks a modern JSON API (REST/FastAPI) layer consumable by a React frontend.**

### Reusable Assets
1. **Application Services**:
   - `BaselineService`: Can retrieve `BaselineProfile`.
   - `RuleBaselineHistoryService`: Can list historical versions and perform baseline diffs.
   - `RuleGovernanceService`: Can compile rules (useful for validation).
   - `RuleCatalogService`: Can list rule schemas.
2. **Domain Models**: `BaselineProfile`, `CompiledRule`, `RuleCompileError`.
3. **Infrastructure**: `BaselineRepository` (Reads/writes to `baselines.json`).
4. **Existing CLI Handlers**: Provide a good reference for orchestration logic (e.g., `src/presentation/cli/main.py`).

### Critical Gaps
1. **HTTP Routing Layer**: No FastAPI endpoints defined for JSON consumption.
2. **DTO Serialization Layer**: No Pydantic models aligning with the frontend's strict TypeScript DTOs.
3. **Tree Aggregation**: The repository stores flat baselines. The UI expects a nested tree (Baseline -> Draft/Versions/Candidates).
4. **Validation/Publish Error Handling**: Current application exceptions (`RuleCompileError`) are not mapped to structured `ValidationIssueDTO` (missing `field_path`).

### Minimum Viable Implementation (MVP) Plan
- **Shell**: Build a barebones FastAPI app in `src/presentation/api`.
- **Storage**: Reuse the existing `BaselineRepository` (JSON file-based) or `FakeBaselineRepository` (in-memory) to get HTTP running immediately without database setup.
- **Scope**: Implement *only* the 6 endpoints required by the frontend's first integration phase.

---

## 2. Minimum API Surface Definition & Response Contracts

The API contracts are strictly aligned with the Frontend's `src/types/dto.ts`.

### Phase 1: Read-Only Interfaces

#### 1. `GET /api/baselines`
- **Purpose**: Returns the nested tree structure for the left navigation.
- **Contract Risk**: High (Needs backend aggregation of flat baseline into tree nodes).
- **Response Shape**: `List[BaselineNodeDTO]`
```json
[
  {
    "id": "b1",
    "type": "baseline_root",
    "name": "Baseline 1.0",
    "baseline_id": "b1",
    "version_id": "root",
    "status": "published"
  },
  {
    "id": "b1-draft",
    "type": "working_draft",
    "name": "Draft",
    "baseline_id": "b1",
    "parent_id": "b1",
    "version_id": "draft",
    "status": "draft"
  }
]
```

#### 2. `GET /api/baselines/{baseline_id}/versions/{version_id}`
- **Purpose**: Returns version metadata for the history detail view.
- **Response Shape**: `VersionMetaDTO`
```json
{
  "version_id": "v1.0",
  "baseline_id": "b1",
  "version_label": "v1.0 (Prod)",
  "summary": "Initial release",
  "publisher": "System",
  "published_at": "2026-04-10T10:00:00Z",
  "parent_version_id": null
}
```

#### 3. `GET /api/baselines/{baseline_id}/diff?source={source}&target={target}`
- **Purpose**: Returns structured diff for the comparison view.
- **Contract Risk**: High (Requires backend to aggregate unified `rules` array).
- **Response Shape**: `DiffSourceTargetDTO`
```json
{
  "source_version_id": "draft",
  "target_version_id": "v1.0",
  "diff_summary": { "added": 1, "removed": 0, "modified": 0 },
  "rules": [
    {
      "rule_id": "rule_1",
      "change_type": "added",
      "changed_fields": [],
      "old_value": null,
      "new_value": { "rule_type": "threshold", "params": {} }
    }
  ]
}
```

#### 4. `POST /api/rules/draft/validate`
- **Purpose**: Validates rule draft configurations.
- **Contract Risk**: High (Needs `field_path`).
- **Request Shape**: `{"rule_type": "string", "params": {}}`
- **Response Shape**: `ValidationResultDTO`
```json
{
  "valid": false,
  "issues": [
    {
      "field_path": "params.threshold",
      "issue_type": "error",
      "message": "Value must be greater than 0",
      "suggestion": "Increase the threshold"
    }
  ]
}
```

### Phase 2: Write Interfaces

#### 5. `POST /api/rules/publish/{baseline_id}`
- **Purpose**: Publishes a draft to a new version.
- **Contract Risk**: High (Needs `blocked_issues` on HTTP 400).
- **Request Shape**: Draft rule object (optional).
- **Response Shape**: `PublishResultDTO`
```json
// 200 OK
{
  "success": true,
  "version_id": "v1.1",
  "version_label": "v1.1",
  "summary": "Published successfully"
}
// 400 Bad Request
{
  "success": false,
  "blocked_issues": [
    { "field_path": "params", "issue_type": "error", "message": "Validation failed" }
  ]
}
```

#### 6. `POST /api/rules/rollback`
- **Purpose**: Creates a rollback candidate draft.
- **Contract Risk**: High (Must return hydrated `draft_data`).
- **Request Shape**: `{"baseline_id": "b1", "version_id": "v1.0"}`
- **Response Shape**: `RollbackCandidateDTO`
```json
{
  "baseline_id": "b1",
  "source_version_id": "v1.0",
  "source_version_label": "v1.0",
  "draft_data": { "rule_type": "threshold", "params": {"operator": "eq"} }
}
```

## 3. Required New Backend Files (API Shell)

1. `src/presentation/api/main.py`: FastAPI application, CORS setup, router inclusion.
2. `src/presentation/api/dependencies.py`: Dependency injection for repos and application services.
3. `src/presentation/api/dto_models.py`: Pydantic models (Request/Response DTOs).
4. `src/presentation/api/routers/baselines.py`: Endpoints for Tree, Version, Diff. *(Now fully using `RuleBaselineHistoryService` for real diffs)*
5. `src/presentation/api/routers/rules.py`: Endpoints for Validate, Publish, Rollback. *(Publish now persists via `BaselineRepository`)*

## 4. Current Integration Status
All endpoints have graduated from "Simulated/Mocked" to **Real JSON Persistence / Real Domain Logic**.

- `GET /baselines`: **Stable/Real** (Dynamically aggregates trees from file-based repository)
- `GET /versions/{version_id}`: **Stable/Real** (Reads persisted `version_history_meta`)
- `GET /diff`: **Stable/Real** (Computes real recursive dictionary comparison using Domain `RuleBaselineHistoryService`)
- `POST /validate`: **Stable/Real** (Extracts strict `field_path` from underlying `RuleCompileError`)
- `POST /publish`: **Stable/Real** (Persists JSON snapshots with atomic safety, automatically bumps semantic versioning)
- `POST /rollback`: **Stable/Real** (Hydrates authentic configurations from deep historical snapshots)