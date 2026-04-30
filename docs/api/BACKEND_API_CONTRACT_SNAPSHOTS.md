# Backend API Contract Snapshots

## Overview

This document describes the API contract snapshots system for the TopoChecker project. Snapshots固化当前 mock-compatible 响应结构，防止后续后端改动破坏前端契约。

## Purpose

API contract snapshots serve as:

1. **Contract Documentation**: Define the expected API response structure
2. **Breaking Change Detection**: Alert when backend responses change
3. **Integration Testing**: Validate frontend-backend compatibility
4. **Regression Prevention**: Prevent accidental breaking changes

## Snapshot Coverage

The following endpoints have snapshots in `tests/backend_api_contract/`:

### Health
| Endpoint | Snapshot | Description |
|----------|----------|-------------|
| `GET /health` | `health.json` | Health check response |

### Baseline Domain
| Endpoint | Snapshot | Description |
|----------|----------|-------------|
| `GET /api/baselines` | `baselines.json` | Baseline list |
| `GET /api/baselines/{id}` | `baseline_detail.json` | Baseline detail with rulesets, rules, profiles |
| `GET /api/baselines/{id}/profile-map` | `baseline_profile_map.json` | Profile mapping |
| `GET /api/baselines/{id}/version-snapshot` | `baseline_version_snapshot.json` | Version statistics |

### Rule Domain
| Endpoint | Snapshot | Description |
|----------|----------|-------------|
| `GET /api/rules/definitions` | `rule_definitions.json` | Rule definitions |
| `GET /api/rulesets` | `rulesets.json` | Rule sets |

### Profile Domain
| Endpoint | Snapshot | Description |
|----------|----------|-------------|
| `GET /api/profiles/parameters` | `parameter_profiles.json` | Parameter profiles |
| `GET /api/profiles/thresholds` | `threshold_profiles.json` | Threshold profiles |
| `GET /api/scopes/selectors` | `scope_selectors.json` | Scope selectors |

### Execution Domain
| Endpoint | Snapshot | Description |
|----------|----------|-------------|
| `GET /api/data-sources` | `data_sources.json` | Data sources |
| `GET /api/scopes` | `execution_scopes.json` | Execution scopes |
| `GET /api/recognition/status` | `recognition_status.json` | Recognition status |

### Version Domain
| Endpoint | Snapshot | Description |
|----------|----------|-------------|
| `GET /api/baselines/{id}/versions` | `versions.json` | Version list |
| `GET /api/versions/{id}` | `version_snapshot.json` | Version snapshot |
| `GET /api/versions/diff` | `version_diff.json` | Version diff (pre-computed) |

### Run Domain
| Endpoint | Snapshot | Description |
|----------|----------|-------------|
| `GET /api/runs` | `runs.json` | Run history |
| `GET /api/runs/{id}` | `run_detail.json` | Run detail with bundle |
| `GET /api/bundles/{id}` | `bundle.json` | Check result bundle |
| `GET /api/issues/{id}` | `issue_detail.json` | Issue detail |

### Diff Domain
| Endpoint | Snapshot | Description |
|----------|----------|-------------|
| `GET /api/diff/recheck` | `recheck_diff.json` | Recheck diff (pre-computed) |

## Key Constraints

### P0: Diff Data is Pre-computed

**The frontend MUST NOT compute diffs.** All diff data must come from the backend as pre-computed snapshots.

#### RecheckDiffSnapshot Structure

```json
{
  "diff": {
    "diff_id": "run-001->run-002",
    "base_run_id": "run-001",
    "target_run_id": "run-002",
    "summary": { "status": "generated" },
    "issue_count_change": {
      "added": 1,
      "removed": 0,
      "unchanged": 9,
      "severity_changed": 0
    },
    "severity_change": { "high": 1 },
    "added_issues": [...],
    "removed_issues": [...],
    "changed_issues": [...],
    "unchanged_issues": [...]
  }
}
```

**Forbidden in Frontend**:
- ❌ `Set` operations on issue arrays
- ❌ Array diffing logic
- ❌ Comparing issue lists
- ❌ Computing added/removed/changed issues

#### VersionDiffSnapshot Structure

```json
{
  "diff": {
    "diff_id": "baseline-001|v1.0.0->baseline-001|v1.1.0",
    "from_version": "baseline-001|v1.0.0",
    "to_version": "baseline-001|v1.1.0",
    "summary": { "added": 2, "removed": 0, "modified": 1 },
    "rule_changes": [...],
    "field_changes": [...]
  }
}
```

## Usage

### Updating Snapshots

When backend API changes (expected or intentional), update snapshots:

```bash
bash scripts/update_backend_api_snapshots.sh
```

This will:
1. Connect to `http://localhost:8000`
2. Fetch all endpoint responses
3. Write to `tests/backend_api_contract/*.json`

### Checking Snapshots

Verify backend matches snapshots:

```bash
bash scripts/check_backend_api_contract_snapshots.sh
```

This will:
1. Connect to `http://localhost:8000`
2. Fetch all endpoint responses
3. Compare with snapshots
4. Report mismatches

If there are failures:
- Review the changes
- If changes are intentional, run `update_backend_api_snapshots.sh`
- If changes are accidental, fix the backend

## When to Update Snapshots

### Intentional Changes
- Backend API intentionally changed
- Added new fields (backward compatible)
- Fixed bugs in response structure

### Do NOT Update for
- Temporary debugging
- Adding test data
- Changes that should not be propagated

## Security Notes

- All scripts only use `localhost` or `127.0.0.1`
- No production URLs configured
- No credentials in snapshots
- No real user data in snapshots

## Files Reference

| File | Purpose |
|------|---------|
| `tests/backend_api_contract/*.json` | Snapshot files |
| `scripts/update_backend_api_snapshots.sh` | Update snapshots from backend |
| `scripts/check_backend_api_contract_snapshots.sh` | Verify against snapshots |
| `docs/api/BACKEND_API_CONTRACT_SNAPSHOTS.md` | This document |

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-01-20 | Initial snapshot set |
