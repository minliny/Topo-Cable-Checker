# Project Status Snapshot

Date: 2026-05-01

## Current Phase

`file-repository-default-active`

## Repository Info

- Git remote: `git@github.com:minliny/Topo-Cable-Checker.git`
- Current main branch latest commit: `0f8f3799`

## CI Status

✅ **green** — GitHub Actions CI is passing for all jobs

## Completed Scope

- Frontend 7 pages componentization
- API contract/service/provider architecture
- Backend FastAPI mock-compatible skeleton
- Local smoke test (28 checks)
- API contract snapshot test (21 snapshots)
- GitHub Actions CI baseline
- Service/repository layer separation
- Engine adapter scaffold
- **Local workspace file persistence (default FileRepository)**
- **FileRepository runtime verification (43/43 pass)**
- **MockRepository vs FileRepository parity audit (19/19 match)**
- **CI FileRepository runtime guard**

## Current Architecture

```
backend/
├── repositories/
│   ├── interface.py         # Repository abstract interface
│   ├── mock_repository.py   # Mock implementation (legacy fallback)
│   ├── file_repository.py   # Local JSON file implementation (default)
│   └── provider.py          # Default: FileRepository
├── workspace/
│   ├── paths.py             # Workspace directory paths
│   ├── manager.py           # File read/write operations
│   └── schema.py            # JSON schema reference
└── data/mock_data.py        # Source data for workspace export
```

## Data Flow

1. `scripts/export_mock_to_workspace.sh` exports mock data to `workspace/`
2. `FileRepository` reads from `workspace/` JSON files by default
3. If workspace files are missing, `FileRepository` falls back to `MockRepository`
4. `TOPOCHECKER_REPO=mock` explicitly uses `MockRepository`

## Incomplete Scope

- ❌ Real local check engine integration
- ❌ Frontend default still mockClient
- ❌ realClient only has local localhost guard for safety

## What We Do NOT Plan

- ❌ Database integration (SQLite, PostgreSQL, etc.)
- ❌ ORM / SQL
- ❌ Server-side persistence
- ❌ Cloud APIs
- ❌ AI/LLM

## Next Stage Recommendations

1. **Check Engine Integration Phase 1**
   - Define check engine interface
   - Implement mock check engine for testing
   - Integrate with execution API

2. **Frontend Client Switch Guard**
   - Add more safety guards for realClient
   - Support environment-based client mode switching
   - Add staging mode with proper safety

3. **Remove MockRepository Fallback**
   - When FileRepository is fully stable, remove internal fallback
   - Keep `TOPOCHECKER_REPO=mock` as explicit legacy option

## Commit Log

| Hash | Message |
|------|---------|
| `0f8f3799` | ci: add file repository runtime guard |
| `1162f088` | test: audit mock and file repository response parity |
| `7b11e5cf` | feat: export mock data to local workspace fixtures |
| `745c012c` | refactor: add local workspace file persistence scaffold |
| `6f420f46` | test: verify local workspace file repository runtime |
| `d7ffc66b` | ci: add file repository runtime guard |
| `4df22afe` | fix(ci): correct backend startup path and add health-check retry loop |
| `dc214cd1` | feat: establish TopoChecker mock-compatible full-stack baseline |
