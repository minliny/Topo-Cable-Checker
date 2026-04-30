# Frontend-Backend API Contract

## Overview

This document defines the API contract between the TopoChecker frontend and backend. The frontend currently uses mock data, and this contract serves as the specification for implementing the real backend API.

**IMPORTANT**: This is a contract alignment document. The real backend is NOT implemented yet. The `realClient.ts` in the frontend is a scaffold that only throws errors.

## Architecture

```
Frontend Pages
      ↓
services.ts (Page-level service methods)
      ↓
provider.ts (API client factory)
      ↓
mockClient.ts (current default) ←→ realClient.ts (scaffold, not implemented)
      ↓                                ↓
mock data files                    [Future: HTTP to backend]
```

## Contract Principles

### P0: Diff Calculation Boundary

**CRITICAL**: The frontend MUST NOT compute diffs. All diff data must come from the backend as pre-computed snapshots.

- `RecheckDiffSnapshot` - Returned by backend, frontend only displays
- `VersionDiffSnapshot` - Returned by backend, frontend only displays
- Frontend pages must NOT perform Set operations, array diffing, or any computational logic to derive diffs

### P1: Recognition Confirmation Flow

The execution flow MUST preserve the recognition confirmation step:

1. User selects baseline, data source, scope
2. User clicks "Recognize" → Backend returns `RecognitionResult`
3. User reviews and clicks "Confirm" → Backend updates status to `confirmed`
4. Only then "Start Check" button is enabled

### P2: Workbench Read-Only Boundary

The Analysis Workbench is read-only:

- Can view `CheckResultBundle`
- Can view `IssueItem` details
- Cannot edit baseline/rules/versions
- Cannot trigger new executions

---

## API Endpoints

### 1. Baseline Domain

#### 1.1 Get Baseline List

| Property | Value |
|----------|-------|
| Endpoint | `GET /api/baselines` |
| Method | GET |
| Auth | Required |

**Response DTO**: `GetBaselineListResponse`

```typescript
interface GetBaselineListResponse {
  baselines: Baseline[];
}
```

**Frontend Contract**: `frontend/src/api/contracts.ts` → `GetBaselineListResponse`

**Service Method**: `getBaselineList()` in `services.ts`

**Mock Source**: `STUB_BASELINES` in `mockClient.ts`

**Error Codes**:
- `401` - Unauthorized
- `500` - Internal server error

---

#### 1.2 Get Baseline Detail

| Property | Value |
|----------|-------|
| Endpoint | `GET /api/baselines/{baseline_id}` |
| Method | GET |
| Auth | Required |

**Path Parameters**:
- `baseline_id` (string) - The baseline identifier

**Response DTO**: `GetBaselineDetailResponse`

```typescript
interface GetBaselineDetailResponse {
  baseline: Baseline;
  rulesets: RuleSet[];
  rules: RuleDefinition[];
  parameter_profile?: ParameterProfile;
  threshold_profile?: ThresholdProfile;
  scope_selector?: ScopeSelector;
}
```

**Frontend Contract**: `frontend/src/api/contracts.ts` → `GetBaselineDetailResponse`

**Service Method**: `getBaselineDetail(baselineId)` in `services.ts`

**Mock Source**: `STUB_BASELINES`, `STUB_RULES` in `mockClient.ts`

**Error Codes**:
- `401` - Unauthorized
- `404` - Baseline not found
- `500` - Internal server error

---

#### 1.3 Update Baseline

| Property | Value |
|----------|-------|
| Endpoint | `PATCH /api/baselines/{baseline_id}` |
| Method | PATCH |
| Auth | Required |

**Path Parameters**:
- `baseline_id` (string) - The baseline identifier

**Request Body**: `UpdateBaselineRequest`

```typescript
interface UpdateBaselineRequest {
  name?: string;
  description?: string;
  status?: 'published' | 'draft' | 'deprecated';
  identification_strategy?: object;
  naming_template?: string;
  parameter_profile_id?: string;
  threshold_profile_id?: string;
  scope_selector_id?: string;
  ruleset_ids?: string[];
}
```

**Response**: `204 No Content` on success

**Frontend Contract**: `frontend/src/api/contracts.ts` → `UpdateBaselineRequest`

**Service Method**: `updateBaseline(baselineId, request)` in `services.ts`

**Mock Source**: No-op in `mockClient.ts`

**Error Codes**:
- `400` - Invalid request body
- `401` - Unauthorized
- `404` - Baseline not found
- `409` - Conflict (e.g., status transition invalid)
- `500` - Internal server error

---

#### 1.4 Get Baseline Profile Map Entry

| Property | Value |
|----------|-------|
| Endpoint | `GET /api/baselines/{baseline_id}/profile-map` |
| Method | GET |
| Auth | Required |

**Path Parameters**:
- `baseline_id` (string) - The baseline identifier

**Response DTO**: `GetBaselineProfileMapEntryResponse`

```typescript
interface GetBaselineProfileMapEntryResponse {
  parameter_profile_id: string;
  threshold_profile_id: string;
  scope_selector_id: string;
  ruleset_ids: string[];
}
```

**Frontend Contract**: `frontend/src/api/contracts.ts` → `GetBaselineProfileMapEntryResponse`

**Service Method**: `getBaselineProfileMapEntry(baselineId)` in `services.ts`

**Mock Source**: `BASELINE_PROFILE_MAP` in `mocks/profiles.mock.ts`

**Error Codes**:
- `401` - Unauthorized
- `404` - Baseline not found
- `500` - Internal server error

---

#### 1.5 Get Baseline Version Snapshot

| Property | Value |
|----------|-------|
| Endpoint | `GET /api/baselines/{baseline_id}/version-snapshot` |
| Method | GET |
| Auth | Required |

**Path Parameters**:
- `baseline_id` (string) - The baseline identifier

**Response DTO**: `GetBaselineVersionSnapshotResponse`

```typescript
interface GetBaselineVersionSnapshotResponse {
  baseline_id: string;
  current_version: string;
  previous_version: string | null;
  rule_added_count: number;
  rule_removed_count: number;
  parameter_changed_count: number;
  threshold_changed_count: number;
}
```

**Frontend Contract**: `frontend/src/api/contracts.ts` → `GetBaselineVersionSnapshotResponse`

**Service Method**: `getBaselineVersionSnapshot(baselineId)` in `services.ts`

**Mock Source**: `BASELINE_VERSION_SNAPSHOTS` in `mocks/version.mock.ts`

**Error Codes**:
- `401` - Unauthorized
- `404` - Baseline not found
- `500` - Internal server error

---

### 2. Rule Domain

#### 2.1 Get Rule Definitions

| Property | Value |
|----------|-------|
| Endpoint | `GET /api/rules/definitions` |
| Method | GET |
| Auth | Required |

**Query Parameters**:
- `baseline_id` (optional) - Filter by baseline

**Response DTO**: `GetRuleDefinitionsResponse`

```typescript
interface GetRuleDefinitionsResponse {
  rules: RuleDefinition[];
}
```

**Frontend Contract**: `frontend/src/api/contracts.ts` → `GetRuleDefinitionsResponse`

**Service Method**: `getRuleDefinitions()` in `services.ts`

**Mock Source**: `STUB_RULES` in `mockClient.ts`

**Error Codes**:
- `401` - Unauthorized
- `500` - Internal server error

---

#### 2.2 Get Rule Set List

| Property | Value |
|----------|-------|
| Endpoint | `GET /api/rulesets` |
| Method | GET |
| Auth | Required |

**Response DTO**: `GetRuleSetListResponse`

```typescript
interface GetRuleSetListResponse {
  rulesets: RuleSet[];
}
```

**Frontend Contract**: `frontend/src/api/contracts.ts` → `GetRuleSetListResponse`

**Service Method**: `getRuleSetList()` in `services.ts`

**Mock Source**: `RULE_SETS` in `mocks/profiles.mock.ts`

**Error Codes**:
- `401` - Unauthorized
- `500` - Internal server error

---

#### 2.3 Update Rule Override

| Property | Value |
|----------|-------|
| Endpoint | `PATCH /api/rules/{rule_id}/override` |
| Method | PATCH |
| Auth | Required |

**Path Parameters**:
- `rule_id` (string) - The rule identifier

**Request Body**: `UpdateRuleOverrideRequest`

```typescript
interface UpdateRuleOverrideRequest {
  rule_id: string;
  rule_overrides: Record<string, number | string | boolean>;
}
```

**Response**: `204 No Content` on success

**Frontend Contract**: `frontend/src/api/contracts.ts` → `UpdateRuleOverrideRequest`

**Service Method**: `updateRuleOverride(request)` in `services.ts`

**Mock Source**: No-op in `mockClient.ts`

**Error Codes**:
- `400` - Invalid override values
- `401` - Unauthorized
- `404` - Rule not found
- `500` - Internal server error

---

### 3. Version Management Domain

#### 3.1 Get Version List

| Property | Value |
|----------|-------|
| Endpoint | `GET /api/baselines/{baseline_id}/versions` |
| Method | GET |
| Auth | Required |

**Path Parameters**:
- `baseline_id` (string) - The baseline identifier

**Response DTO**: `GetVersionListResponse`

```typescript
interface GetVersionListResponse {
  versions: VersionSnapshot[];
}
```

**Frontend Contract**: `frontend/src/api/contracts.ts` → `GetVersionListResponse`

**Service Method**: `getVersionList(baselineId)` in `services.ts`

**Mock Source**: `VERSION_SNAPSHOTS` in `mocks/version.mock.ts`

**Error Codes**:
- `401` - Unauthorized
- `404` - Baseline not found
- `500` - Internal server error

---

#### 3.2 Get Version Snapshot

| Property | Value |
|----------|-------|
| Endpoint | `GET /api/versions/{version_id}` |
| Method | GET |
| Auth | Required |

**Path Parameters**:
- `version_id` (string) - The version identifier (format: `baseline_id|version`)

**Response DTO**: `GetVersionSnapshotResponse`

```typescript
interface GetVersionSnapshotResponse {
  snapshot: VersionSnapshot;
}
```

**Frontend Contract**: `frontend/src/api/contracts.ts` → `GetVersionSnapshotResponse`

**Service Method**: `getVersionSnapshot(versionId)` in `services.ts`

**Mock Source**: `VERSION_SNAPSHOTS` in `mocks/version.mock.ts`

**Error Codes**:
- `401` - Unauthorized
- `404` - Version not found
- `500` - Internal server error

---

#### 3.3 Get Version Diff

| Property | Value |
|----------|-------|
| Endpoint | `GET /api/versions/diff` |
| Method | GET |
| Auth | Required |

**Query Parameters**:
- `from_version` (string) - Source version ID
- `to_version` (string) - Target version ID

**Response DTO**: `GetVersionDiffResponse`

```typescript
interface GetVersionDiffResponse {
  diff: VersionDiffSnapshot;
}
```

**IMPORTANT**: The backend MUST compute and return the diff. The frontend MUST NOT compute diffs.

**Frontend Contract**: `frontend/src/api/contracts.ts` → `GetVersionDiffResponse`

**Service Method**: `getVersionDiff(fromVersion, toVersion)` in `services.ts`

**Mock Source**: `VERSION_DIFF_SNAPSHOTS` in `mocks/version.mock.ts`

**Error Codes**:
- `400` - Invalid version parameters
- `401` - Unauthorized
- `404` - Version(s) not found
- `500` - Internal server error

---

#### 3.4 Create Version

| Property | Value |
|----------|-------|
| Endpoint | `POST /api/baselines/{baseline_id}/versions` |
| Method | POST |
| Auth | Required |

**Path Parameters**:
- `baseline_id` (string) - The baseline identifier

**Request Body**: `CreateVersionRequest`

```typescript
interface CreateVersionRequest {
  description: string;
  status?: 'draft';
}
```

**Response**: `201 Created` with `{ version_id: string }`

**Frontend Contract**: `frontend/src/api/contracts.ts` → `CreateVersionRequest`

**Service Method**: `createVersion(baselineId, request)` in `services.ts`

**Mock Source**: Returns stub ID in `mockClient.ts`

**Error Codes**:
- `400` - Invalid request body
- `401` - Unauthorized
- `404` - Baseline not found
- `409` - Conflict (e.g., version already exists)
- `500` - Internal server error

---

#### 3.5 Publish Version

| Property | Value |
|----------|-------|
| Endpoint | `POST /api/versions/{version_id}/publish` |
| Method | POST |
| Auth | Required |

**Path Parameters**:
- `version_id` (string) - The version identifier

**Request Body**: `PublishVersionRequest`

```typescript
interface PublishVersionRequest {
  version_id: string;
}
```

**Response**: `204 No Content` on success

**Frontend Contract**: `frontend/src/api/contracts.ts` → `PublishVersionRequest`

**Service Method**: `publishVersion(request)` in `services.ts`

**Mock Source**: No-op in `mockClient.ts`

**Error Codes**:
- `400` - Invalid version state for publishing
- `401` - Unauthorized
- `404` - Version not found
- `409` - Conflict (e.g., already published)
- `500` - Internal server error

---

### 4. Execution Domain

#### 4.1 Get Data Source List

| Property | Value |
|----------|-------|
| Endpoint | `GET /api/data-sources` |
| Method | GET |
| Auth | Required |

**Response DTO**: `GetDataSourceListResponse`

```typescript
interface GetDataSourceListResponse {
  data_sources: DataSource[];
}
```

**Frontend Contract**: `frontend/src/api/contracts.ts` → `GetDataSourceListResponse`

**Service Method**: `getDataSourceList()` in `services.ts`

**Mock Source**: `DATA_SOURCES` in `mocks/execution.mock.ts`

**Error Codes**:
- `401` - Unauthorized
- `500` - Internal server error

---

#### 4.2 Get Scope List

| Property | Value |
|----------|-------|
| Endpoint | `GET /api/scopes` |
| Method | GET |
| Auth | Required |

**Response DTO**: `GetScopeListResponse`

```typescript
interface GetScopeListResponse {
  scopes: ExecutionScope[];
}
```

**Frontend Contract**: `frontend/src/api/contracts.ts` → `GetScopeListResponse`

**Service Method**: `getScopeList()` in `services.ts`

**Mock Source**: `EXECUTION_SCOPES` in `mocks/execution.mock.ts`

**Error Codes**:
- `401` - Unauthorized
- `500` - Internal server error

---

#### 4.3 Get Recognition Status

| Property | Value |
|----------|-------|
| Endpoint | `GET /api/recognition/status` |
| Method | GET |
| Auth | Required |

**Response DTO**: `GetRecognitionStatusResponse`

```typescript
interface GetRecognitionStatusResponse {
  status: 'not_started' | 'ready' | 'confirmed' | 'rejected';
  result?: RecognitionResult;
}
```

**Frontend Contract**: `frontend/src/api/contracts.ts` → `GetRecognitionStatusResponse`

**Service Method**: `getRecognitionStatus()` in `services.ts`

**Mock Source**: Returns default status in `mockClient.ts`

**Error Codes**:
- `401` - Unauthorized
- `500` - Internal server error

---

#### 4.4 Start Recognition

| Property | Value |
|----------|-------|
| Endpoint | `POST /api/recognition/start` |
| Method | POST |
| Auth | Required |

**Request Body**: `StartRecognitionRequest`

```typescript
interface StartRecognitionRequest {
  dataset_id: string;
  scope_id: string;
}
```

**Response**: `200 OK` with `{ recognition_id: string }`

**Frontend Contract**: `frontend/src/api/contracts.ts` → `StartRecognitionRequest`

**Service Method**: `startRecognition(request)` in `services.ts`

**Mock Source**: Returns stub ID in `mockClient.ts`

**Error Codes**:
- `400` - Invalid request parameters
- `401` - Unauthorized
- `404` - Dataset or scope not found
- `500` - Internal server error

---

#### 4.5 Confirm Recognition

| Property | Value |
|----------|-------|
| Endpoint | `POST /api/recognition/confirm` |
| Method | POST |
| Auth | Required |

**Request Body**: `ConfirmRecognitionRequest`

```typescript
interface ConfirmRecognitionRequest {
  confirmed: boolean;
}
```

**Response**: `204 No Content` on success

**IMPORTANT**: This endpoint is part of the required recognition confirmation flow. The "Start Check" button must only be enabled after this returns success.

**Frontend Contract**: `frontend/src/api/contracts.ts` → `ConfirmRecognitionRequest`

**Service Method**: `confirmRecognition(request)` in `services.ts`

**Mock Source**: No-op in `mockClient.ts`

**Error Codes**:
- `400` - Invalid confirmation state
- `401` - Unauthorized
- `409` - Conflict (e.g., recognition not in ready state)
- `500` - Internal server error

---

#### 4.6 Start Check

| Property | Value |
|----------|-------|
| Endpoint | `POST /api/checks/start` |
| Method | POST |
| Auth | Required |

**Request Body**: `StartCheckRequest`

```typescript
interface StartCheckRequest {
  baseline_id: string;
  scenario_id: string;
}
```

**Response**: `200 OK` with `{ run_id: string }`

**IMPORTANT**: This endpoint must only be called after recognition is confirmed.

**Frontend Contract**: `frontend/src/api/contracts.ts` → `StartCheckRequest`

**Service Method**: `startCheck(request)` in `services.ts`

**Mock Source**: Returns stub ID in `mockClient.ts`

**Error Codes**:
- `400` - Recognition not confirmed
- `401` - Unauthorized
- `404` - Baseline or scenario not found
- `500` - Internal server error

---

### 5. Run History Domain

#### 5.1 Get Run History

| Property | Value |
|----------|-------|
| Endpoint | `GET /api/runs` |
| Method | GET |
| Auth | Required |

**Query Parameters**:
- `baseline_id` (optional) - Filter by baseline
- `status` (optional) - Filter by status
- `limit` (optional) - Max results
- `offset` (optional) - Pagination offset

**Response DTO**: `GetRunHistoryResponse`

```typescript
interface GetRunHistoryResponse {
  runs: RunHistoryEntry[];
}
```

**Frontend Contract**: `frontend/src/api/contracts.ts` → `GetRunHistoryResponse`

**Service Method**: `getRunHistory()` in `services.ts`

**Mock Source**: `INIT_RUNS` in `mocks/execution.mock.ts`

**Error Codes**:
- `401` - Unauthorized
- `500` - Internal server error

---

#### 5.2 Get Run Detail

| Property | Value |
|----------|-------|
| Endpoint | `GET /api/runs/{run_id}` |
| Method | GET |
| Auth | Required |

**Path Parameters**:
- `run_id` (string) - The run identifier

**Response DTO**: `GetRunDetailResponse`

```typescript
interface GetRunDetailResponse {
  run: RunHistoryEntry;
  bundle?: CheckResultBundle;
}
```

**Frontend Contract**: `frontend/src/api/contracts.ts` → `GetRunDetailResponse`

**Service Method**: `getRunDetail(runId)` in `services.ts`

**Mock Source**: `INIT_RUNS` in `mocks/execution.mock.ts`

**Error Codes**:
- `401` - Unauthorized
- `404` - Run not found
- `500` - Internal server error

---

### 6. Workbench Domain

#### 6.1 Get Check Result Bundle

| Property | Value |
|----------|-------|
| Endpoint | `GET /api/bundles/{bundle_id}` |
| Method | GET |
| Auth | Required |

**Path Parameters**:
- `bundle_id` (string) - The bundle identifier

**Response DTO**: `GetCheckResultBundleResponse`

```typescript
interface GetCheckResultBundleResponse {
  bundle: CheckResultBundle;
}
```

**Frontend Contract**: `frontend/src/api/contracts.ts` → `GetCheckResultBundleResponse`

**Service Method**: `getCheckResultBundle(bundleId)` in `services.ts`

**Mock Source**: `CheckResultBundle` data in `mocks/execution.mock.ts`

**Error Codes**:
- `401` - Unauthorized
- `404` - Bundle not found
- `500` - Internal server error

---

#### 6.2 Get Issue Detail

| Property | Value |
|----------|-------|
| Endpoint | `GET /api/issues/{issue_id}` |
| Method | GET |
| Auth | Required |

**Path Parameters**:
- `issue_id` (string) - The issue identifier

**Response DTO**: `GetIssueDetailResponse`

```typescript
interface GetIssueDetailResponse {
  issue: IssueItem;
}
```

**Frontend Contract**: `frontend/src/api/contracts.ts` → `GetIssueDetailResponse`

**Service Method**: `getIssueDetail(issueId)` in `services.ts`

**Mock Source**: Issue data derived from bundles in `mockClient.ts`

**Error Codes**:
- `401` - Unauthorized
- `404` - Issue not found
- `500` - Internal server error

---

### 7. Diff Compare Domain

#### 7.1 Get Recheck Diff

| Property | Value |
|----------|-------|
| Endpoint | `GET /api/diff/recheck` |
| Method | GET |
| Auth | Required |

**Query Parameters**:
- `base_run_id` (string) - Base run identifier
- `target_run_id` (string) - Target run identifier

**Response DTO**: `GetRecheckDiffResponse`

```typescript
interface GetRecheckDiffResponse {
  diff: RecheckDiffSnapshot;
}
```

**IMPORTANT**: The backend MUST compute and return the diff. The frontend MUST NOT compute diffs. The `RecheckDiffSnapshot` contains pre-computed diff data including added/removed/changed issues.

**Frontend Contract**: `frontend/src/api/contracts.ts` → `GetRecheckDiffResponse`

**Service Method**: `getRecheckDiff(baseRunId, targetRunId)` in `services.ts`

**Mock Source**: `RECHECK_DIFF_SNAPSHOTS` in `mocks/diff.mock.ts`

**Error Codes**:
- `400` - Invalid run parameters
- `401` - Unauthorized
- `404` - Run(s) not found or diff not available
- `500` - Internal server error

---

### 8. Profiles/Selectors Domain

#### 8.1 Get Parameter Profile List

| Property | Value |
|----------|-------|
| Endpoint | `GET /api/profiles/parameters` |
| Method | GET |
| Auth | Required |

**Response DTO**: `GetParameterProfileListResponse`

```typescript
interface GetParameterProfileListResponse {
  profiles: ParameterProfile[];
}
```

**Frontend Contract**: `frontend/src/api/contracts.ts` → `GetParameterProfileListResponse`

**Service Method**: `getParameterProfileList()` in `services.ts`

**Mock Source**: `PARAMETER_PROFILES` in `mocks/profiles.mock.ts`

**Error Codes**:
- `401` - Unauthorized
- `500` - Internal server error

---

#### 8.2 Get Threshold Profile List

| Property | Value |
|----------|-------|
| Endpoint | `GET /api/profiles/thresholds` |
| Method | GET |
| Auth | Required |

**Response DTO**: `GetThresholdProfileListResponse`

```typescript
interface GetThresholdProfileListResponse {
  profiles: ThresholdProfile[];
}
```

**Frontend Contract**: `frontend/src/api/contracts.ts` → `GetThresholdProfileListResponse`

**Service Method**: `getThresholdProfileList()` in `services.ts`

**Mock Source**: `THRESHOLD_PROFILES` in `mocks/profiles.mock.ts`

**Error Codes**:
- `401` - Unauthorized
- `500` - Internal server error

---

#### 8.3 Get Scope Selector List

| Property | Value |
|----------|-------|
| Endpoint | `GET /api/scopes/selectors` |
| Method | GET |
| Auth | Required |

**Response DTO**: `GetScopeSelectorListResponse`

```typescript
interface GetScopeSelectorListResponse {
  selectors: ScopeSelector[];
}
```

**Frontend Contract**: `frontend/src/api/contracts.ts` → `GetScopeSelectorListResponse`

**Service Method**: `getScopeSelectorList()` in `services.ts`

**Mock Source**: `SCOPE_SELECTORS` in `mocks/profiles.mock.ts`

**Error Codes**:
- `401` - Unauthorized
- `500` - Internal server error

---

## Data Types Reference

All data types are defined in:
- `frontend/src/models/` - Domain models
- `frontend/src/api/contracts.ts` - API request/response types

### Key Types

| Type | Location | Description |
|------|----------|-------------|
| `Baseline` | `models/baseline.ts` | Baseline configuration |
| `RuleSet` | `models/baseline.ts` | Rule set collection |
| `RuleDefinition` | `models/baseline.ts` | Individual rule definition |
| `VersionSnapshot` | `models/version.ts` | Version snapshot |
| `VersionDiffSnapshot` | `models/version.ts` | **Pre-computed** version diff |
| `RecheckDiffSnapshot` | `models/diff.ts` | **Pre-computed** recheck diff |
| `CheckResultBundle` | `models/execution.ts` | Check result bundle |
| `IssueItem` | `models/execution.ts` | Individual issue |
| `RunHistoryEntry` | `models/execution.ts` | Run history entry |
| `RecognitionResult` | `models/execution.ts` | Recognition result |

---

## Error Response Format

All errors should follow a consistent format:

```typescript
interface ApiErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}
```

---

## Implementation Checklist

When implementing the real backend:

- [ ] Implement all endpoints defined in this document
- [ ] Ensure `VersionDiffSnapshot` is computed on the backend
- [ ] Ensure `RecheckDiffSnapshot` is computed on the backend
- [ ] Preserve recognition confirmation flow
- [ ] Return proper error codes
- [ ] Add authentication/authorization
- [ ] Add request validation
- [ ] Add rate limiting
- [ ] Add logging/monitoring

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-20 | Initial contract alignment document |
