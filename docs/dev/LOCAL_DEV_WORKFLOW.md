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
| `scripts/dev_start_backend.sh` | Start backend server |
| `scripts/dev_stop_backend.sh` | Stop backend server |
| `scripts/dev_check_all.sh` | Run all checks |

### Backend API Scripts

| Script | Purpose |
|--------|---------|
| `scripts/smoke_frontend_backend_local.sh` | Smoke test backend API |
| `scripts/update_backend_api_snapshots.sh` | Update API snapshots |
| `scripts/check_backend_api_contract_snapshots.sh` | Verify API snapshots |

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

## Running All Checks

### Full Check (Backend Required)

```bash
bash scripts/dev_start_backend.sh
bash scripts/dev_check_all.sh
bash scripts/dev_stop_backend.sh
```

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
│              backend/data/mock_data.py                   │
│                    (mock data only)                     │
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

## Files Reference

| Directory | Purpose |
|-----------|---------|
| `frontend/` | React/TypeScript frontend |
| `backend/` | FastAPI backend |
| `scripts/` | Development and validation scripts |
| `tests/backend_api_contract/` | API snapshot files |
| `docs/api/` | API documentation |
| `docs/dev/` | Development workflow documentation |
