# backend/workspace/manager.py
"""Workspace file manager for local persistence."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, List, Dict

from .paths import WorkspacePaths


class WorkspaceManager:
    """Manages local workspace files (JSON only, no database)."""

    def __init__(self, root: Optional[str] = None):
        self.paths = WorkspacePaths(root)
        self.paths.ensure_all()

    # ── Task Management ──────────────────────────────────────────

    def save_task(self, task: Dict[str, Any]) -> Path:
        """Save a task definition to workspace/tasks/{task_id}.json"""
        task_id = task["task_id"]
        file_path = self.paths.tasks / f"{task_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(task, f, ensure_ascii=False, indent=2)
        return file_path

    def load_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Load a task definition from workspace/tasks/{task_id}.json"""
        file_path = self.paths.tasks / f"{task_id}.json"
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_tasks(self) -> List[Dict[str, Any]]:
        """List all task definitions."""
        tasks = []
        for file_path in self.paths.tasks.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                tasks.append(json.load(f))
        return tasks

    # ── Run Management ───────────────────────────────────────────

    def save_run(self, run: Dict[str, Any]) -> Path:
        """Save a run result to workspace/runs/{run_id}.json"""
        run_id = run["run_id"]
        file_path = self.paths.runs / f"{run_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(run, f, ensure_ascii=False, indent=2)
        return file_path

    def load_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Load a run result from workspace/runs/{run_id}.json"""
        file_path = self.paths.runs / f"{run_id}.json"
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_runs(self) -> List[Dict[str, Any]]:
        """List all run results."""
        runs = []
        for file_path in self.paths.runs.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                runs.append(json.load(f))
        return runs

    # ── Snapshot Management ──────────────────────────────────────

    def save_snapshot(self, snapshot: Dict[str, Any]) -> Path:
        """Save a version snapshot to workspace/snapshots/{version_id}.json"""
        version_id = snapshot["version_id"]
        file_path = self.paths.snapshots / f"{version_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)
        return file_path

    def load_snapshot(self, version_id: str) -> Optional[Dict[str, Any]]:
        """Load a version snapshot from workspace/snapshots/{version_id}.json"""
        file_path = self.paths.snapshots / f"{version_id}.json"
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_snapshots(self) -> List[Dict[str, Any]]:
        """List all version snapshots."""
        snapshots = []
        for file_path in self.paths.snapshots.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                snapshots.append(json.load(f))
        return snapshots

    # ── Report Management ────────────────────────────────────────

    def save_report(self, report: Dict[str, Any], content: str) -> Path:
        """Save a report to workspace/reports/{report_id}.{format}"""
        report_id = report["report_id"]
        fmt = report.get("format", "html")
        file_path = self.paths.reports / f"{report_id}.{fmt}"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        # Also save metadata as JSON
        meta_path = self.paths.reports / f"{report_id}.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return file_path

    def list_reports(self) -> List[Dict[str, Any]]:
        """List all report metadata."""
        reports = []
        for file_path in self.paths.reports.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                reports.append(json.load(f))
        return reports

    # ── Export Management ────────────────────────────────────────

    def save_export(self, export_id: str, data: Dict[str, Any], fmt: str = "json") -> Path:
        """Save exported data to workspace/exports/{export_id}.{fmt}"""
        file_path = self.paths.exports / f"{export_id}.{fmt}"
        with open(file_path, "w", encoding="utf-8") as f:
            if fmt == "json":
                json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                f.write(str(data))
        return file_path

    def load_export(self, export_id: str, fmt: str = "json") -> Optional[Dict[str, Any]]:
        """Load exported data from workspace/exports/{export_id}.{fmt}"""
        file_path = self.paths.exports / f"{export_id}.{fmt}"
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            if fmt == "json":
                return json.load(f)
            return {"raw": f.read()}
