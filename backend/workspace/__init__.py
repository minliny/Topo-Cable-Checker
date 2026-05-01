# backend/workspace/__init__.py
"""Local workspace management for TopoChecker.

This module handles local file persistence:
- Task definitions (JSON)
- Run results (JSON)
- Version snapshots (JSON)
- Reports (HTML, CSV, Excel)

No database, no ORM, no SQLite.
"""

from .paths import WorkspacePaths
from .manager import WorkspaceManager

__all__ = ["WorkspacePaths", "WorkspaceManager"]
