# Backend API Contract Snapshots

This directory contains JSON snapshots of the backend API responses. These snapshots serve as a contract between the frontend and backend to ensure compatibility.

## Purpose

These snapshots validate that the backend API responses match the expected structure. When the backend changes, these snapshots help identify breaking changes.

## Coverage

| Endpoint | Snapshot File | Description |
|----------|--------------|-------------|
| `GET /health` | `health.json` | Health check |
| `GET /api/baselines` | `baselines.json` | Baseline list |
| `GET /api/baselines/{id}` | `baseline_detail.json` | Baseline detail |
| `GET /api/baselines/{id}/profile-map` | `baseline_profile_map.json` | Profile mapping |
| `GET /api/baselines/{id}/version-snapshot` | `baseline_version_snapshot.json` | Version snapshot |
| `GET /api/rules/definitions` | `rule_definitions.json` | Rule definitions |
| `GET /api/rulesets` | `rulesets.json` | Rule sets |
| `GET /api/profiles/parameters` | `parameter_profiles.json` | Parameter profiles |
| `GET /api/profiles/thresholds` | `threshold_profiles.json` | Threshold profiles |
| `GET /api/scopes/selectors` | `scope_selectors.json` | Scope selectors |
| `GET /api/data-sources` | `data_sources.json` | Data sources |
| `GET /api/scopes` | `execution_scopes.json` | Execution scopes |
| `GET /api/baselines/{id}/versions` | `versions.json` | Version list |
| `GET /api/versions/{id}` | `version_snapshot.json` | Version snapshot |
| `GET /api/versions/diff` | `version_diff.json` | Version diff |
| `GET /api/recognition/status` | `recognition_status.json` | Recognition status |
| `GET /api/runs` | `runs.json` | Run history |
| `GET /api/runs/{id}` | `run_detail.json` | Run detail with bundle |
| `GET /api/bundles/{id}` | `bundle.json` | Check result bundle |
| `GET /api/issues/{id}` | `issue_detail.json` | Issue detail |
| `GET /api/diff/recheck` | `recheck_diff.json` | Recheck diff |

## Key Constraints

### Diff Data is Pre-computed

The `recheck_diff.json` and `version_diff.json` snapshots contain pre-computed diff data. **The frontend must NOT compute diffs.** All diff data must come from the backend as pre-computed snapshots.

### Snapshot Fields

- `RecheckDiffSnapshot.added_issues` - Issues present in target run only
- `RecheckDiffSnapshot.removed_issues` - Issues present in base run only
- `RecheckDiffSnapshot.changed_issues` - Issues with changed severity
- `RecheckDiffSnapshot.unchanged_issues` - Issues with same severity

## Updating Snapshots

When backend API changes, update snapshots using:

```bash
bash scripts/update_backend_api_snapshots.sh
```

## Checking Snapshots

Verify backend matches snapshots using:

```bash
bash scripts/check_backend_api_contract_snapshots.sh
```

## Notes

- These snapshots represent the mock-compatible API responses
- Snapshots do NOT include real database connections
- Snapshots do NOT include real check engine results
