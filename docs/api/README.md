# API Documentation

## Current Status: Contract Alignment Phase

This directory contains API documentation for the TopoChecker frontend-backend integration.

**IMPORTANT**: The real backend is NOT implemented yet. This is a contract alignment phase.

## Documents

### [FRONTEND_BACKEND_API_CONTRACT.md](./FRONTEND_BACKEND_API_CONTRACT.md)

The complete API contract specification covering:

- **Baseline Domain**: Baseline CRUD, profile mapping, version snapshots
- **Rule Domain**: Rule definitions, rule sets, overrides
- **Version Management Domain**: Version list, snapshots, diffs
- **Execution Domain**: Data sources, scopes, recognition, check execution
- **Run History Domain**: Run history list and details
- **Workbench Domain**: Check result bundles, issue details
- **Diff Compare Domain**: Recheck diff snapshots
- **Profiles/Selectors Domain**: Parameter profiles, threshold profiles, scope selectors

## Architecture

```
Frontend (React/TypeScript)
    │
    ├── pages/           # UI components
    ├── api/services.ts  # Page-level service methods
    ├── api/provider.ts  # API client factory
    │
    └── api/mockClient.ts  ← CURRENT (returns mock data)
            │
            └── api/realClient.ts  ← SCAFFOLD (not implemented)
                    │
                    └── [Future: HTTP to backend]
```

## Key Principles

### 1. Diff Calculation Boundary

**The frontend MUST NOT compute diffs.**

- `RecheckDiffSnapshot` - Must be returned by backend
- `VersionDiffSnapshot` - Must be returned by backend
- Frontend only displays pre-computed diff data

### 2. Recognition Confirmation Flow

The execution flow must preserve the recognition confirmation step:

1. User selects baseline, data source, scope
2. User clicks "Recognize" → Backend returns `RecognitionResult`
3. User reviews and clicks "Confirm" → Backend updates status
4. Only then "Start Check" button is enabled

### 3. Workbench Read-Only Boundary

The Analysis Workbench is read-only:

- Can view `CheckResultBundle`
- Can view `IssueItem` details
- Cannot edit baseline/rules/versions
- Cannot trigger new executions

## Frontend API Layer

The frontend API layer is located in `frontend/src/api/`:

| File | Purpose |
|------|---------|
| `contracts.ts` | TypeScript interfaces for API requests/responses |
| `client.ts` | `ApiClient` interface definition |
| `mockClient.ts` | Mock implementation using local data |
| `realClient.ts` | Scaffold implementation (throws errors) |
| `provider.ts` | API client factory (default: mock) |
| `services.ts` | Page-level service methods |
| `index.ts` | Centralized exports |

## Next Phase: HTTP Transport Implementation

The next phase will implement real HTTP transport:

1. Set `USE_MOCK = false` in `provider.ts`
2. Implement HTTP calls in `realClient.ts`
3. Add authentication headers
4. Add error handling
5. Add request/response logging

**No changes to pages or services are required.**

## Mock Data Sources

Current mock data comes from:

| File | Data |
|------|------|
| `mocks/execution.mock.ts` | Data sources, scopes, recognition, runs |
| `mocks/diff.mock.ts` | Pre-computed diff snapshots |
| `mocks/version.mock.ts` | Version snapshots and diffs |
| `mocks/profiles.mock.ts` | Parameter profiles, threshold profiles, scopes, rule sets |

## Error Handling

The API contract defines standard error codes:

- `400` - Bad request (invalid parameters)
- `401` - Unauthorized
- `404` - Resource not found
- `409` - Conflict (state transition invalid)
- `500` - Internal server error

## Version History

| Version | Date | Status |
|---------|------|--------|
| 1.0.0 | 2026-01-20 | Contract alignment complete |
