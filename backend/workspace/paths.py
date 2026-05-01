# backend/workspace/paths.py
"""Workspace path definitions."""

import os
from pathlib import Path
from typing import Optional


class WorkspacePaths:
    """Manages workspace directory paths."""

    def __init__(self, root: Optional[str] = None):
        self.root = Path(root or os.environ.get("TOPOCHECKER_WORKSPACE", "workspace"))

    @property
    def inputs(self) -> Path:
        return self.root / "inputs"

    @property
    def tasks(self) -> Path:
        return self.root / "tasks"

    @property
    def runs(self) -> Path:
        return self.root / "runs"

    @property
    def snapshots(self) -> Path:
        return self.root / "snapshots"

    @property
    def reports(self) -> Path:
        return self.root / "reports"

    @property
    def exports(self) -> Path:
        return self.root / "exports"

    def ensure_all(self) -> None:
        """Create all workspace directories if they don't exist."""
        for path in [self.inputs, self.tasks, self.runs, self.snapshots, self.reports, self.exports]:
            path.mkdir(parents=True, exist_ok=True)
