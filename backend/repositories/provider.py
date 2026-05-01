# backend/repositories/provider.py
# Repository provider — controls which repository implementation is active.
# Default: MockRepository (in-memory mock data)
# Future: SQLiteRepository (persistent database)

import os
from typing import Optional
from .interface import Repository
from .mock_repository import MockRepository
from .sqlite_repository import SQLiteRepository


_DEFAULT_REPO: Optional[Repository] = None


def get_repository() -> Repository:
    """Get the active repository instance.

    Environment variable TOPOCHECKER_REPO controls the implementation:
    - "mock" (default): MockRepository — in-memory, no persistence
    - "sqlite": SQLiteRepository — persistent SQLite database

    WARNING: Do NOT switch to "sqlite" until SQLiteRepository is fully implemented.
    """
    global _DEFAULT_REPO

    if _DEFAULT_REPO is not None:
        return _DEFAULT_REPO

    repo_type = os.environ.get("TOPOCHECKER_REPO", "mock").lower()

    if repo_type == "sqlite":
        _DEFAULT_REPO = SQLiteRepository()
    else:
        _DEFAULT_REPO = MockRepository()

    return _DEFAULT_REPO


def reset_repository() -> None:
    """Reset the cached repository instance.
    Useful for testing or switching implementations at runtime.
    """
    global _DEFAULT_REPO
    _DEFAULT_REPO = None
