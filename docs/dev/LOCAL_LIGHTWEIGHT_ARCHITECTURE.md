# Local Lightweight Architecture

Date: 2026-05-01

## Project Positioning

Topo-Cable-Checker is a **local lightweight tool**.

It is NOT a server-side SaaS, NOT a cloud service, and does NOT require database persistence.

## What We Do NOT Use

- ❌ Database (SQLite, PostgreSQL, MySQL, MongoDB, etc.)
- ❌ ORM (SQLAlchemy, Peewee, Tortoise, etc.)
- ❌ Server-side persistence
- ❌ Cloud APIs
- ❌ AI/LLM

## What We DO Use

- ✅ Local file input (Excel, CSV, table files)
- ✅ Local parsing and processing
- ✅ Local rule checking engine
- ✅ Local result output (JSON, HTML, CSV, Excel)
- ✅ Local workspace file snapshots

## Workspace Directory Structure

```
workspace/
  inputs/           # User input files (Excel, CSV)
  tasks/            # Task definitions (JSON snapshots)
  runs/             # Run results (JSON snapshots)
  snapshots/        # Version snapshots (JSON)
  reports/          # Generated reports (HTML, CSV, Excel)
  exports/          # Exported data
```

## Data Persistence Strategy

| Data Type | Format | Location |
|-----------|--------|----------|
| Baselines | JSON | `workspace/tasks/` |
| Rulesets | JSON | `workspace/tasks/` |
| Run history | JSON | `workspace/runs/` |
| Check results | JSON | `workspace/runs/` |
| Version snapshots | JSON | `workspace/snapshots/` |
| Reports | HTML/CSV/Excel | `workspace/reports/` |

## Repository Layer Clarification

The `backend/repositories/` directory contains **data access abstractions**, NOT database repositories.

- `MockRepository`: in-memory mock data for development
- Future `FileRepository`: local JSON file persistence
- NO database connection, NO ORM, NO SQL

## FastAPI Skeleton Purpose

The current FastAPI backend is a **local development adapter layer**.

- It provides API endpoints for frontend development
- It returns mock-compatible data
- It does NOT imply the project must become a server-side system
- Future real data source will be local workspace files and local check engine

## Diff Computation Policy

**Backend-only diff computation** — hard requirement.

- `RecheckDiffSnapshot` is computed by the engine, returned by backend
- `VersionDiffSnapshot` is computed by the engine, returned by backend
- Frontend must NOT compute diffs locally

## Input / Output Flow

```
User Input (Excel/CSV)
    ↓
Local Parser
    ↓
Local Check Engine
    ↓
JSON Results (workspace/runs/)
    ↓
Report Generator (HTML/CSV/Excel)
    ↓
User Output (local files)
```

## Future Directions

1. **Local File Persistence**: Implement `FileRepository` to read/write JSON from workspace/
2. **Real Check Engine**: Implement `RealEngineAdapter` for local rule checking
3. **Report Export**: Add HTML/CSV/Excel export functionality
4. **NO database, NO cloud, NO SaaS**
