# Backend API Skeleton

## Overview

This is a minimal backend API skeleton for the TopoChecker project. It provides mock-compatible API endpoints that return static data compatible with the frontend `src/api/contracts.ts`.

**IMPORTANT**: This is NOT a production backend. It does NOT:
- Connect to a real database
- Run the actual check engine
- Compute real diffs
- Process real network topology data

## Current Status

- **Mode**: Mock/Static Data
- **Database**: Not connected
- **Check Engine**: Not connected
- **AI/LLM**: Not used

## Architecture

```
Frontend (React/TypeScript)
      ↓ (HTTP)
backend/main.py (FastAPI)
      ↓ (static mock data)
backend/data/mock_data.py
```

## API Endpoints

### Baseline Domain

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/baselines` | List all baselines |
| GET | `/api/baselines/{id}` | Get baseline detail |
| PATCH | `/api/baselines/{id}` | Update baseline |
| GET | `/api/baselines/{id}/profile-map` | Get profile mapping |
| GET | `/api/baselines/{id}/version-snapshot` | Get version snapshot |

### Rule Domain

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/rules/definitions` | List all rule definitions |
| GET | `/api/rulesets` | List all rule sets |
| PATCH | `/api/rules/{id}/override` | Update rule override |

### Version Domain

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/baselines/{id}/versions` | List versions |
| GET | `/api/versions/{id}` | Get version snapshot |
| GET | `/api/versions/diff` | Get version diff snapshot |
| POST | `/api/baselines/{id}/versions` | Create version |
| POST | `/api/versions/{id}/publish` | Publish version |

### Execution Domain

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/data-sources` | List data sources |
| GET | `/api/scopes` | List execution scopes |
| GET | `/api/recognition/status` | Get recognition status |
| POST | `/api/recognition/start` | Start recognition |
| POST | `/api/recognition/confirm` | Confirm recognition |
| POST | `/api/checks/start` | Start check |

### Run History Domain

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/runs` | List run history |
| GET | `/api/runs/{id}` | Get run detail |
| GET | `/api/bundles/{id}` | Get check result bundle |
| GET | `/api/issues/{id}` | Get issue detail |

### Diff Compare Domain

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/diff/recheck` | Get recheck diff |

### Profile Domain

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/profiles/parameters` | List parameter profiles |
| GET | `/api/profiles/thresholds` | List threshold profiles |
| GET | `/api/scopes/selectors` | List scope selectors |

## Key Design Decisions

### 1. Diff Data is Pre-computed

The backend returns pre-computed `RecheckDiffSnapshot` and `VersionDiffSnapshot` from static mock data. The frontend is NOT allowed to compute diffs.

### 2. Recognition Confirmation Flow

The execution flow preserves the recognition confirmation step:
1. `POST /api/recognition/start` - Start recognition
2. User reviews result
3. `POST /api/recognition/confirm` - Confirm recognition
4. `POST /api/checks/start` - Start check (only after confirm)

### 3. Workbench Read-Only

The Analysis Workbench only consumes `CheckResultBundle` and issue details. It cannot edit baselines, rules, or versions.

## Future Integration Points

When integrating with real backend services:

1. **Database Connection**: Replace `data/mock_data.py` with database queries
2. **Check Engine**: Replace mock check execution with real engine calls
3. **Diff Computation**: Implement real diff computation in `/api/diff/recheck`
4. **Recognition**: Replace mock recognition with real topology analysis

## Running the Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Constraints

- **NO Database**: Uses static mock data only
- **NO Check Engine**: Returns pre-computed results
- **NO AI/LLM**: No AI or LLM integration
- **NO Production URLs**: No external API calls
- **NO Real Authentication**: No real auth implementation

## Files Structure

```
backend/
├── main.py              # FastAPI app entry point
├── requirements.txt     # Python dependencies
├── models/
│   ├── __init__.py
│   ├── baseline.py      # Baseline, RuleSet, RuleDefinition models
│   ├── execution.py     # Execution, Run, Bundle, Issue models
│   ├── version.py       # Version models
│   └── diff.py          # Diff models
├── data/
│   ├── __init__.py
│   └── mock_data.py     # Static mock data
└── routers/
    ├── __init__.py
    ├── baselines.py     # Baseline endpoints
    ├── rules.py         # Rule endpoints
    ├── versions.py      # Version endpoints
    ├── execution.py     # Execution endpoints
    ├── runs.py           # Run history endpoints
    ├── diff.py          # Diff compare endpoints
    └── profiles.py      # Profile endpoints
```

## Version History

| Version | Date | Status |
|---------|------|--------|
| 0.1.0 | 2026-01-20 | Initial mock skeleton |