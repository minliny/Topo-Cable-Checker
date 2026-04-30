# CI Baseline Configuration

## Overview

This document describes the CI (Continuous Integration) pipeline configuration for the TopoChecker project. The CI runs on GitHub Actions and validates both frontend and backend components.

## CI Configuration

| File | Purpose |
|------|---------|
| `.github/workflows/frontend-backend-ci.yml` | GitHub Actions workflow |

## Workflow Jobs

### 1. Frontend Checks (`frontend-checks`)

| Step | Description |
|------|-------------|
| Checkout | Clone repository |
| Setup Node.js | Install Node.js 20 with npm cache |
| Install frontend dependencies | `npm ci` |
| Frontend Typecheck | `npm run typecheck` |

### 2. Backend Checks (`backend-checks`)

| Step | Description |
|------|-------------|
| Checkout | Clone repository |
| Setup Python | Install Python 3.11 with pip cache |
| Install backend dependencies | `pip install -r requirements.txt` |
| Frontend Prototype Freeze | `bash scripts/check_frontend_prototype_freeze.sh` |
| Frontend Componentization | `bash scripts/check_frontend_componentization_phase1.sh` |
| Frontend Typecheck Baseline | `bash scripts/check_frontend_typecheck_baseline.sh` |
| Backend API Skeleton | `bash scripts/check_backend_api_skeleton.sh` |

### 3. Smoke & Snapshots (`smoke-and-snapshots`)

| Step | Description |
|------|-------------|
| Checkout | Clone repository |
| Setup Node.js | Install Node.js 20 with npm cache |
| Install frontend dependencies | `npm ci` |
| Frontend Typecheck | `npm run typecheck` |
| Setup Python | Install Python 3.11 with pip cache |
| Install backend dependencies | `pip install -r requirements.txt` |
| Start Backend | Start uvicorn on port 8000 |
| Verify Backend | Health check |
| Smoke Test | `bash scripts/smoke_frontend_backend_local.sh` |
| API Contract Snapshots | `bash scripts/check_backend_api_contract_snapshots.sh` |
| Stop Backend | Cleanup uvicorn process |

## Triggers

| Trigger | Description |
|---------|-------------|
| `push` to `main`, `develop` | Run on every push |
| `pull_request` to `main`, `develop` | Run on every PR |

## Blocking Merges

The following checks must pass before merging:

- `frontend-checks` job must pass
- `backend-checks` job must pass
- `smoke-and-snapshots` job must pass

If any job fails, the PR cannot be merged.

## Coverage

### Frontend Coverage

- TypeScript compilation (`npm run typecheck`)
- Component structure
- Model files
- Mock data files
- Page components

### Backend Coverage

- API skeleton structure
- Router files
- Mock data files
- Documentation

### Integration Coverage

- Backend health check
- All API endpoints
- API response structure
- Snapshot validation

## Current Constraints

The CI validates a **mock-compatible stack**. It does NOT test:

- ❌ Real database connections
- ❌ Real check engine execution
- ❌ Real external API calls
- ❌ AI/LLM services
- ❌ Production deployment

## Local Development vs CI

### Local Development

```bash
# Start backend
bash scripts/dev_start_backend.sh

# Run all checks
bash scripts/dev_check_all.sh

# Stop backend
bash scripts/dev_stop_backend.sh
```

### CI (GitHub Actions)

All checks run automatically on push/PR. No manual intervention required.

## Troubleshooting

### CI Fails on Typecheck

Run locally:
```bash
cd frontend
npm run typecheck
```

### CI Fails on Smoke Test

Ensure backend can start:
```bash
bash scripts/dev_start_backend.sh
curl http://127.0.0.1:8000/health
```

### CI Fails on Snapshots

Update snapshots if backend API intentionally changed:
```bash
bash scripts/update_backend_api_snapshots.sh
git commit -am "chore: update API snapshots"
```

## Files Reference

| Directory | Purpose |
|-----------|---------|
| `.github/workflows/` | CI configuration |
| `scripts/` | Development and validation scripts |
| `frontend/` | React/TypeScript frontend |
| `backend/` | FastAPI backend |
| `tests/backend_api_contract/` | API snapshot files |
