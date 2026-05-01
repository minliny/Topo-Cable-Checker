# backend/repositories/provider.py
# Repository provider — controls which repository implementation is active.
# Default: FileRepository (local JSON/workspace file persistence)
# Fallback: MockRepository (in-memory mock data, via TOPOCHECKER_REPO=mock)

import os
from typing import Optional

from .interface import Repository
from .file_repository import FileRepository
from .mock_repository import MockRepository


_DEFAULT_REPO: Optional[Repository] = None


def get_repository() -> Repository:
    """Get the active repository instance.

    Environment variable TOPOCHECKER_REPO controls the implementation:
    - "file" (default): FileRepository — local JSON/workspace file persistence
    - "mock": MockRepository — in-memory, no persistence (legacy fallback)

    FileRepository reads from workspace/ JSON files first, falls back to
    MockRepository if files are missing.
    """
    global _DEFAULT_REPO

    if _DEFAULT_REPO is not None:
        return _DEFAULT_REPO

    repo_type = os.environ.get("TOPOCHECKER_REPO", "file").lower()

    if repo_type == "mock":
        _DEFAULT_REPO = MockRepository()
    else:
        _DEFAULT_REPO = FileRepository()

    return _DEFAULT_REPO


def reset_repository() -> None:
    """Reset the cached repository instance.
    Useful for testing or switching implementations at runtime.
    """
    global _DEFAULT_REPO
    _DEFAULT_REPO = None
