# Local Integration Smoke Test

## Overview

This document describes how to run the local smoke test to verify frontend-backend connectivity without connecting to real database or check engine.

## Prerequisites

1. **Python 3.9+** installed
2. **pip** package manager
3. **curl** command-line tool

## Architecture

```
Frontend (React/TypeScript)
      ↓ (mock mode default)
frontend/src/api/services.ts
      ↓ (mockClient)
mock data ← default

Frontend (React/TypeScript)
      ↓ (real mode - temporary)
frontend/src/api/services.ts
      ↓ (realClient)
backend/main.py (FastAPI)
      ↓ (mock data)
backend/data/mock_data.py
```

## Quick Start

### Step 1: Start Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Or start in background:

```bash
cd backend
nohup uvicorn main:app --port 8000 > server.log 2>&1 &
echo $!  # Note the PID for later kill
```

### Step 2: Run Smoke Test

```bash
bash scripts/smoke_frontend_backend_local.sh
```

Expected output when backend is running:
- All health checks pass
- API endpoints return valid JSON
- Recheck diff contains pre-computed snapshot fields

Expected output when backend is not running:
- Tests are skipped with "后端未运行" message
- Exit code: 2

## Smoke Test Coverage

The smoke test validates:

| Endpoint | Description | Validation |
|----------|-------------|------------|
| `GET /health` | Health check | HTTP 200 |
| `GET /api/baselines` | List baselines | HTTP 200, JSON with `baselines` |
| `GET /api/baselines/{id}` | Baseline detail | HTTP 200, JSON with `baseline` |
| `GET /api/baselines/{id}/profile-map` | Profile mapping | HTTP 200, JSON with `parameter_profile_id` |
| `GET /api/baselines/{id}/version-snapshot` | Version snapshot | HTTP 200, JSON with `current_version` |
| `GET /api/rules/definitions` | Rule definitions | HTTP 200, JSON with `rules` |
| `GET /api/data-sources` | Data sources | HTTP 200, JSON with `data_sources` |
| `GET /api/scopes` | Execution scopes | HTTP 200, JSON with `scopes` |
| `GET /api/profiles/parameters` | Parameter profiles | HTTP 200, JSON with `profiles` |
| `GET /api/profiles/thresholds` | Threshold profiles | HTTP 200, JSON with `profiles` |
| `GET /api/scopes/selectors` | Scope selectors | HTTP 200, JSON with `selectors` |
| `GET /api/versions/diff` | Version diff | HTTP 200, JSON with diff fields |
| `GET /api/recognition/status` | Recognition status | HTTP 200 |
| `GET /api/runs` | Run history | HTTP 200 |
| `GET /api/diff/recheck` | Recheck diff | HTTP 200, JSON with `added_issues` |

## Switching Frontend to Real Mode (Temporary)

**WARNING**: This temporarily switches frontend to use real backend. Default is mock mode.

1. Stop the smoke test
2. Add to your frontend code (e.g., in `main.tsx` before app render):

```typescript
import { setApiConfig } from './api';

setApiConfig({
  mode: 'real',
  baseUrl: 'http://localhost:8000'
});
```

3. Start frontend dev server:
```bash
cd frontend
npm run dev
```

4. Open browser and navigate to pages

5. **Important**: Reset to mock mode after testing:
```typescript
import { resetApiConfig } from './api';

resetApiConfig();
```

## Key Boundaries

### Diff Data is Pre-computed

The backend returns pre-computed `RecheckDiffSnapshot` from mock data. Frontend only displays.

**Do NOT**: Compute diffs in frontend UI.

### Default Mode is Mock

Frontend default is `mockClient`. Real mode requires explicit `setApiConfig()`.

**Do NOT**: Change the default in config.ts.

### Localhost Only

Real mode only works with localhost/127.0.0.1 URLs.

**Do NOT**: Configure production URLs.

## Troubleshooting

### Backend won't start

Check Python version:
```bash
python3 --version
```

Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

Check port availability:
```bash
lsof -i :8000
```

### Smoke test fails

Ensure backend is running:
```bash
curl http://localhost:8000/health
```

### Frontend pages show no data

Verify real mode is enabled:
```typescript
console.log(getApiConfig());
```

Should output: `{ mode: 'real', baseUrl: 'http://localhost:8000' }`

## Security Notes

- Backend only accepts localhost connections by default
- No production URLs configured
- No database connections
- No check engine integration
- No AI/LLM usage

## Stopping Services

### Stop Backend

```bash
pkill -f "uvicorn main:app"
```

Or if started with PID:
```bash
kill <PID>
```

### Reset Frontend to Mock Mode

Refresh page or call `resetApiConfig()` in browser console.

## Files Reference

| File | Purpose |
|------|---------|
| `scripts/smoke_frontend_backend_local.sh` | Smoke test script |
| `scripts/check_backend_api_skeleton.sh` | Backend skeleton validation |
| `frontend/src/api/config.ts` | API mode configuration |
| `frontend/src/api/realClient.ts` | Real HTTP client |
| `frontend/src/api/mockClient.ts` | Mock data client |
| `backend/main.py` | FastAPI application |
| `backend/routers/` | API endpoint routers |
| `backend/data/mock_data.py` | Static mock data |
