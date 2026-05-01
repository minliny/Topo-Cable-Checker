# Local Development Workflow

## Overview

This document describes how to set up and run the local development environment for the TopoChecker project. The project consists of:

- **Frontend**: React/TypeScript application
- **Backend**: FastAPI application with mock-compatible data

**Current Status**: This is a mock-compatible stack. It does NOT connect to:
- Real database
- Real check engine
- Real external APIs
- AI/LLM services

## Prerequisites

### Frontend

- Node.js 18+
- npm or pnpm

### Backend

- Python 3.9+
- pip

## Quick Start

### 1. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 2. Install Backend Dependencies

```bash
cd backend
pip3 install -r requirements.txt
```

### 3. Start Backend

```bash
bash scripts/dev_start_backend.sh
```

Expected output:
```
✓ 后端启动成功: http://127.0.0.1:8000
```

### 4. Verify Backend

```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{"status":"healthy","mode":"mock"}
```

### 5. Start Frontend (Development)

```bash
cd frontend
npm run dev
```

## Development Scripts

### Backend Scripts

| Script | Purpose |
|--------|---------|
| `scripts/dev_start_backend.sh` | Start backend server (MockRepository, default) |
| `scripts/dev_start_backend_file_repo.sh` | Start backend server (FileRepository mode) |
| `scripts/dev_stop_backend.sh` | Stop backend server |
| `scripts/dev_check_all.sh` | Run all checks |

### Backend API Scripts

| Script | Purpose |
|--------|---------|
| `scripts/smoke_frontend_backend_local.sh` | Smoke test backend API |
| `scripts/update_backend_api_snapshots.sh` | Update API snapshots |
| `scripts/check_backend_api_contract_snapshots.sh` | Verify API snapshots |
| `scripts/check_file_repository_runtime.sh` | Verify FileRepository runtime |

### Frontend Scripts

| Script | Purpose |
|--------|---------|
| `scripts/check_frontend_prototype_freeze.sh` | Verify prototype is frozen |
| `scripts/check_frontend_componentization_phase1.sh` | Verify componentization |
| `scripts/check_frontend_typecheck_baseline.sh` | Verify TypeScript compilation |

### Backend Skeleton Script

| Script | Purpose |
|--------|---------|
| `scripts/check_backend_api_skeleton.sh` | Verify backend skeleton |

### Workspace Scripts

| Script | Purpose |
|--------|---------|
| `scripts/export_mock_to_workspace.sh` | Export mock data to workspace fixtures |

## Running All Checks

### Full Check (Backend Required)

```bash
bash scripts/dev_check_all.sh
```

This runs:
1. Frontend checks (prototype freeze, componentization, typecheck)
2. Backend API skeleton check
3. Export workspace fixtures
4. MockRepository mode smoke test + API snapshots
5. FileRepository mode runtime verification

### Frontend Only (No Backend Required)

```bash
bash scripts/check_frontend_prototype_freeze.sh
bash scripts/check_frontend_componentization_phase1.sh
bash scripts/check_frontend_typecheck_baseline.sh
cd frontend && npm run typecheck
```

## Smoke Test

### Interactive Smoke Test

```bash
# Start backend first
bash scripts/dev_start_backend.sh

# Run smoke test
bash scripts/smoke_frontend_backend_local.sh
```

Expected output:
```
SMOKE_TEST_PASS
```

### Update API Snapshots

When backend API changes, update snapshots:

```bash
bash scripts/update_backend_api_snapshots.sh
```

### Verify API Snapshots

```bash
bash scripts/check_backend_api_contract_snapshots.sh
```

Expected output:
```
API_CONTRACT_CHECK_PASS
```

## FileRepository Mode

### What is FileRepository Mode?

FileRepository mode uses local workspace JSON files instead of in-memory mock data. It is useful for:
- Testing local file persistence
- Validating workspace fixture integrity
- Preparing for future FileRepository migration

### How to Start FileRepository Mode

```bash
# 1. Export mock data to workspace (if not already done)
bash scripts/export_mock_to_workspace.sh

# 2. Start backend in FileRepository mode
bash scripts/dev_start_backend_file_repo.sh
```

### How to Verify FileRepository Mode

```bash
bash scripts/check_file_repository_runtime.sh
```

This verifies:
- Backend is running with `TOPOCHECKER_REPO=file`
- All API endpoints respond correctly
- API responses match contract snapshots
- No database references in responses

### Switching Back to MockRepository

```bash
unset TOPOCHECKER_REPO
# or
export TOPOCHECKER_REPO=mock

bash scripts/dev_start_backend.sh
```

### Important Notes

- **Default repository is still MockRepository**. `TOPOCHECKER_REPO=file` is only for explicit verification.
- FileRepository currently falls back to MockRepository if workspace files are missing.
- Do NOT switch the default repository to FileRepository until it is fully implemented.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│                  frontend/src/api/                        │
│                 ┌────────┬────────┐                    │
│                 │ mock   │ real   │                    │
│                 │client  │client  │                    │
│                 └────┬───┴───┬────┘                    │
│                      │       │                          │
│                      ▼       ▼                          │
│                   provider.ts                           │
│                   config.ts                             │
└──────────────────────┼──────────────────────────────────┘
                       │ HTTP
                       ▼
┌─────────────────────────────────────────────────────────┐
│                 Backend (FastAPI)                        │
│              backend/main.py                             │
│              backend/routers/                           │
│              backend/repositories/                      │
│                 ┌────────┬────────┐                    │
│                 │ Mock   │ File   │                    │
│                 │Repo    │Repo    │                    │
│                 └────┬───┴───┬────┘                    │
│                      │       │                          │
│                      ▼       ▼                          │
│              backend/data/mock_data.py                   │
│              workspace/ (JSON fixtures)                  │
└─────────────────────────────────────────────────────────┘
```

## Key Constraints

### NOT Connected

- ❌ Real database
- ❌ Real check engine
- ❌ Real external APIs
- ❌ AI/LLM services
- ❌ Production URLs

### Still Working

- ✅ Mock data returns
- ✅ API contract validation
- ✅ TypeScript compilation
- ✅ Frontend-backend connectivity
- ✅ FileRepository runtime verification

## Stopping Backend

```bash
bash scripts/dev_stop_backend.sh
```

## Troubleshooting

### Backend won't start

Check Python version:
```bash
python3 --version  # Should be 3.9+
```

Install dependencies:
```bash
cd backend
pip3 install -r requirements.txt
```

### Port already in use

```bash
bash scripts/dev_stop_backend.sh
bash scripts/dev_start_backend.sh
```

### Smoke test fails

Verify backend is running:
```bash
curl http://127.0.0.1:8000/health
```

### FileRepository runtime fails

1. Check workspace fixtures exist:
```bash
ls workspace/inputs/
```

2. Re-export fixtures:
```bash
bash scripts/export_mock_to_workspace.sh
```

3. Check backend log:
```bash
cat backend/dev_server_file_repo.log
```

## Files Reference

| Directory | Purpose |
|-----------|---------|
| `frontend/` | React/TypeScript frontend |
| `backend/` | FastAPI backend |
| `scripts/` | Development and validation scripts |
| `tests/backend_api_contract/` | API snapshot files |
| `docs/api/` | API documentation |
| `docs/dev/` | Development workflow documentation |
| `workspace/` | Local workspace JSON fixtures |
