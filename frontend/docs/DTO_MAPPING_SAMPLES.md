# DTO Mapping & Integration Samples

This document stores the integration samples for the first phase of real backend API integration (Read-Only Interfaces).
*Note: Due to the actual backend FastAPI implementation not being fully complete yet in `src/presentation/api`, these represent the expected payloads based on the mock channel and DTO normalization logic.*

## 1. GET /baselines
- **Status**: PARTIAL (Adapter ready, waiting for backend tree structure)
- **UI Works**: YES
- **Contract Gaps**: YES
- **Gap Layer**: `raw response` -> `adapter`

### Original Request
`GET /api/baselines`

### Original Response Sample (Mock)
```json
[
  { "id": "base-001", "name": "Baseline 1.0 (Prod)", "status": "published" }
]
```

### Adapter Output DTO (`normalizeBaselineTreeResponse`)
```json
[
  {
    "id": "base-001",
    "type": "baseline_root",
    "name": "Baseline 1.0 (Prod)",
    "baseline_id": "base-001",
    "version_id": "root",
    "status": "published"
  }
]
```

### Reducer Consumption
Dispatches `SWITCH_CONTEXT` with `{ baselineId: "base-001", versionId: "draft" }`.
Left nav `BaselineList.tsx` currently mocks the nested versions under this root since the backend only returns a flat list.

### Known Gaps
Backend currently returns a flat list of Baselines. The UI expects a nested tree (Baseline -> Versions / Drafts). 
**Action**: `BaselineList.tsx` currently hardcodes the children. Backend needs to supply a `/baselines/tree` endpoint or the UI adapter must fetch `/versions` for each baseline and merge them.

---

## 2. GET /baselines/:id/versions/:id
- **Status**: NO (Backend endpoint missing)
- **UI Works**: YES (Using mock UI fallback)
- **Contract Gaps**: YES
- **Gap Layer**: `network`

### Expected Original Response
```json
{
  "version_id": "v1.0",
  "baseline_id": "base-001",
  "version_label": "v1.0 (Prod)",
  "summary": "Initial release",
  "publisher": "admin",
  "published_at": "2026-04-10T10:00:00Z"
}
```

### Adapter Output DTO (`normalizeVersionDetailResponse`)
*Matches expected response exactly. Adapter provides fallbacks like `"System"` for publisher if missing.*

### Known Gaps
Endpoint does not exist. `HistoryDetailView.tsx` currently renders without fetching this metadata.

---

## 3. GET /baselines/:id/diff
- **Status**: YES (Adapter handles old and new formats)
- **UI Works**: YES
- **Contract Gaps**: NO (Adapter bridges the gap)
- **Gap Layer**: `adapter`

### Original Request
`GET /api/baselines/base-001/diff?source=draft&target=previous_version`

### Original Response Sample (Mock - Legacy Format)
```json
{
  "added_rules": [ { "id": "rule-new-1", "name": "New Validation Rule", "type": "threshold" } ],
  "removed_rules": [],
  "modified_rules": []
}
```

### Adapter Output DTO (`normalizeDiffResponse`)
```json
{
  "source_version_id": "draft",
  "target_version_id": "previous_version",
  "diff_summary": { "added": 1, "removed": 0, "modified": 0 },
  "rules": [
    {
      "rule_id": "rule-new-1",
      "change_type": "added",
      "new_value": { "id": "rule-new-1", "name": "New Validation Rule", "type": "threshold" }
    }
  ]
}
```

### Reducer Consumption
Dispatches `DIFF_SUCCESS` with `diffData` containing unified `rules` array. Right panel shows summary, center panel shows rules.

---

## 4. POST /rules/draft/validate
- **Status**: PARTIAL
- **UI Works**: YES
- **Contract Gaps**: YES
- **Gap Layer**: `raw response`

### Original Request
```json
{
  "rule_type": "threshold",
  "params": {}
}
```

### Original Response Sample (Mock)
```json
{
  "validation_result": {
    "valid": false,
    "errors": [
      { "field_path": "params", "message": "Missing or invalid parameters" }
    ]
  }
}
```

### Adapter Output DTO (`normalizeValidationResponse`)
```json
{
  "valid": false,
  "issues": [
    {
      "field_path": "params",
      "issue_type": "error",
      "message": "Missing or invalid parameters"
    }
  ]
}
```

### Reducer Consumption
Dispatches `VALIDATION_SUCCESS`. UI Right Panel loops through `issues`. Clicking an issue calls `onJumpToField(issue.field_path)`.

### Known Gaps
If backend returns a raw array of strings `["Missing param"]` instead of objects, the adapter gracefully degrades it to `{ field_path: 'unknown', message: 'Missing param' }`. The UI will still render the error, but the click-to-jump functionality will be disabled.