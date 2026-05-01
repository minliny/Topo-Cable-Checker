# Database Integration Plan

Date: 2026-05-01

## Current Status

SQLite repository scaffold has been added but **NOT enabled**.
Default repository remains `MockRepository` (in-memory mock data).

## Architecture

```
routers → services → engine → repositories → data source
                                      │
                                      ├─ MockRepository (default)
                                      └─ SQLiteRepository (future)
```

## Repository Interface

All repositories implement `Repository` abstract class defined in `backend/repositories/interface.py`.

## Switching Repository

Set environment variable before starting the backend:

```bash
# Default (current)
export TOPOCHECKER_REPO=mock

# Future (when SQLiteRepository is fully implemented)
export TOPOCHECKER_REPO=sqlite
```

**WARNING**: Do NOT switch to `sqlite` until `SQLiteRepository` is fully implemented.

## Migration Plan

### Phase 1: Scaffold (COMPLETED)
- [x] Define `Repository` abstract interface
- [x] Implement `MockRepository` (existing behavior)
- [x] Create `SQLiteRepository` scaffold (all methods raise `NotImplementedError`)
- [x] Create `provider.py` with default `MockRepository`
- [x] Update all services to use `get_repository()` via provider

### Phase 2: Schema Design
- [ ] Design SQLite schema matching mock_data structures
- [ ] Create migration scripts
- [ ] Add `sqlalchemy` or `sqlite3` dependency

### Phase 3: Implementation
- [ ] Implement `SQLiteRepository` methods with actual SQL queries
- [ ] Add connection pooling
- [ ] Add transaction support
- [ ] Write unit tests for SQLiteRepository

### Phase 4: Migration
- [ ] Create data migration script from mock_data to SQLite
- [ ] Test full application with SQLite backend
- [ ] Update CI to test both Mock and SQLite repositories
- [ ] Switch default to SQLite when ready

## Diff Computation Policy

**Backend-only diff computation** — This is a hard requirement.

- `RecheckDiffSnapshot` is computed by the engine and returned by the backend
- `VersionDiffSnapshot` is computed by the engine and returned by the backend
- Frontend must NOT compute diffs locally
- This ensures consistent diff logic regardless of client implementation

## Constraints

- No AI/LLM dependencies in repository layer
- No external service calls in repository layer
- Repository layer is synchronous (async handled at service/engine level)
- All API responses must remain unchanged during migration
