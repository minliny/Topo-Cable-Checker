#!/usr/bin/env python3
"""
Export mock data to workspace/ JSON fixtures.

Usage:
    cd /path/to/project
    bash scripts/export_mock_to_workspace.sh

This script reads backend/data/mock_data.py and exports all mock data
as JSON files to workspace/ directories. No DB, no SQLite, no ORM.
"""

import json
import os
import sys
from pathlib import Path
import types


def pydantic_to_dict(obj):
    """Convert Pydantic model or list/dict of models to plain dict (deep)."""
    # Handle Pydantic v2 models
    if hasattr(obj, "model_dump"):
        return pydantic_to_dict(obj.model_dump())
    # Handle Pydantic v1 models
    if hasattr(obj, "dict"):
        return pydantic_to_dict(obj.dict())
    if isinstance(obj, list):
        return [pydantic_to_dict(item) for item in obj]
    if isinstance(obj, dict):
        return {k: pydantic_to_dict(v) for k, v in obj.items()}
    return obj


def _load_mock_data_module(backend_dir: Path):
    """Load mock_data.py directly, bypassing data/__init__.py relative import issues."""
    import importlib.util

    # Build fake package hierarchy so relative imports work:
    # backend -> backend.data -> backend.data.mock_data
    # ..models from backend.data.mock_data resolves to backend.models
    backend_pkg = types.ModuleType("backend")
    backend_pkg.__path__ = [str(backend_dir)]
    sys.modules["backend"] = backend_pkg

    data_pkg = types.ModuleType("backend.data")
    data_pkg.__path__ = [str(backend_dir / "data")]
    sys.modules["backend.data"] = data_pkg

    # Pre-load all models submodules under backend.models
    models_dir = backend_dir / "models"
    models_pkg = types.ModuleType("backend.models")
    models_pkg.__path__ = [str(models_dir)]
    sys.modules["backend.models"] = models_pkg

    for model_file in sorted(models_dir.glob("*.py")):
        if model_file.name == "__init__.py":
            continue
        module_name = f"backend.models.{model_file.stem}"
        spec = importlib.util.spec_from_file_location(module_name, str(model_file))
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

    # Now load mock_data.py with package = "backend.data"
    mock_data_path = backend_dir / "data" / "mock_data.py"
    spec = importlib.util.spec_from_file_location("backend.data.mock_data", str(mock_data_path))
    mock_data = importlib.util.module_from_spec(spec)
    sys.modules["backend.data.mock_data"] = mock_data
    mock_data.__package__ = "backend.data"
    spec.loader.exec_module(mock_data)
    return mock_data


def export_mock_to_workspace():
    """Export all mock data to workspace JSON files."""
    # Determine backend and project root
    backend_dir = Path(__file__).parent.parent.resolve()
    project_root = backend_dir.parent

    mock_data = _load_mock_data_module(backend_dir)

    # Ensure backend is in path for workspace import
    sys.path.insert(0, str(backend_dir))
    from workspace.manager import WorkspaceManager

    workspace = WorkspaceManager(str(project_root / "workspace"))
    exported = {}

    # ── Baselines ───────────────────────────────────────────────
    baselines = pydantic_to_dict(mock_data.MOCK_BASELINES)
    for bl in baselines:
        bl_id = bl["id"]
        path = workspace.paths.inputs / f"baseline_{bl_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(bl, f, ensure_ascii=False, indent=2)
    exported["baselines"] = len(baselines)

    # ── Rulesets ────────────────────────────────────────────────
    rulesets = pydantic_to_dict(mock_data.MOCK_RULESETS)
    path = workspace.paths.inputs / "rulesets.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rulesets, f, ensure_ascii=False, indent=2)
    exported["rulesets"] = len(rulesets)

    # ── Rules ───────────────────────────────────────────────────
    rules = pydantic_to_dict(mock_data.MOCK_RULES)
    path = workspace.paths.inputs / "rules.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)
    exported["rules"] = len(rules)

    # ── Parameter Profiles ──────────────────────────────────────
    profiles = pydantic_to_dict(mock_data.MOCK_PARAMETER_PROFILES)
    path = workspace.paths.inputs / "parameter_profiles.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=2)
    exported["parameter_profiles"] = len(profiles)

    # ── Threshold Profiles ──────────────────────────────────────
    profiles = pydantic_to_dict(mock_data.MOCK_THRESHOLD_PROFILES)
    path = workspace.paths.inputs / "threshold_profiles.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=2)
    exported["threshold_profiles"] = len(profiles)

    # ── Scope Selectors ─────────────────────────────────────────
    selectors = pydantic_to_dict(mock_data.MOCK_SCOPE_SELECTORS)
    path = workspace.paths.inputs / "scope_selectors.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(selectors, f, ensure_ascii=False, indent=2)
    exported["scope_selectors"] = len(selectors)

    # ── Data Sources ────────────────────────────────────────────
    sources = pydantic_to_dict(mock_data.MOCK_DATA_SOURCES)
    path = workspace.paths.inputs / "data_sources.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sources, f, ensure_ascii=False, indent=2)
    exported["data_sources"] = len(sources)

    # ── Execution Scopes ────────────────────────────────────────
    scopes = pydantic_to_dict(mock_data.MOCK_EXECUTION_SCOPES)
    path = workspace.paths.inputs / "execution_scopes.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(scopes, f, ensure_ascii=False, indent=2)
    exported["execution_scopes"] = len(scopes)

    # ── Baseline Profile Map ────────────────────────────────────
    path = workspace.paths.inputs / "baseline_profile_map.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(mock_data.BASELINE_PROFILE_MAP, f, ensure_ascii=False, indent=2)
    exported["baseline_profile_map"] = len(mock_data.BASELINE_PROFILE_MAP)

    # ── Baseline Version Snapshots ──────────────────────────────
    path = workspace.paths.inputs / "baseline_version_snapshots.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(mock_data.BASELINE_VERSION_SNAPSHOTS, f, ensure_ascii=False, indent=2)
    exported["baseline_version_snapshots"] = len(mock_data.BASELINE_VERSION_SNAPSHOTS)

    # ── Tasks (derived from runs) ───────────────────────────────
    tasks = []
    for run in pydantic_to_dict(mock_data.MOCK_RUNS):
        task = {
            "task_id": f"task-{run['run_id']}",
            "baseline_id": run["baseline_id"],
            "data_source_id": run["data_source_id"],
            "scope_id": run["scope_id"],
            "parameter_profile_id": "pp-001",
            "threshold_profile_id": "tp-001",
            "created_at": "2024-01-15T09:00:00Z",
            "updated_at": "2024-01-15T09:00:00Z",
        }
        tasks.append(task)
        workspace.save_task(task)
    exported["tasks"] = len(tasks)

    # ── Runs ────────────────────────────────────────────────────
    runs = pydantic_to_dict(mock_data.MOCK_RUNS)
    for run in runs:
        workspace.save_run(run)
    exported["runs"] = len(runs)

    # ── Bundles ─────────────────────────────────────────────────
    bundles = pydantic_to_dict(mock_data.MOCK_BUNDLES)
    path = workspace.paths.inputs / "bundles.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(bundles, f, ensure_ascii=False, indent=2)
    exported["bundles"] = len(bundles)

    # ── Version Snapshots ───────────────────────────────────────
    snapshots = pydantic_to_dict(mock_data.MOCK_VERSION_SNAPSHOTS)
    for snap in snapshots.values():
        workspace.save_snapshot(snap)
    exported["version_snapshots"] = len(snapshots)

    # ── Version Diff Snapshots ──────────────────────────────────
    diffs = pydantic_to_dict(mock_data.MOCK_VERSION_DIFF_SNAPSHOTS)
    path = workspace.paths.inputs / "version_diffs.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(diffs, f, ensure_ascii=False, indent=2)
    exported["version_diffs"] = len(diffs)

    # ── Recheck Diff Snapshots ──────────────────────────────────
    rechecks = pydantic_to_dict(mock_data.MOCK_RECHECK_DIFF_SNAPSHOTS)
    path = workspace.paths.inputs / "recheck_diffs.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rechecks, f, ensure_ascii=False, indent=2)
    exported["recheck_diffs"] = len(rechecks)

    # ── Reports (placeholder) ───────────────────────────────────
    reports = []
    for run in runs:
        report = {
            "report_id": f"report-{run['run_id']}",
            "run_id": run["run_id"],
            "format": "html",
            "file_path": f"workspace/reports/report-{run['run_id']}.html",
            "generated_at": "2024-01-15T09:06:00Z",
        }
        reports.append(report)
        workspace.save_report(report, f"<html><body>Report for {run['run_id']}</body></html>")
    exported["reports"] = len(reports)

    # ── Exports (placeholder) ───────────────────────────────────
    exports = []
    for run in runs:
        export_data = {
            "export_id": f"export-{run['run_id']}",
            "run_id": run["run_id"],
            "format": "json",
            "data": {"issues": run.get("issue_count", 0)},
        }
        exports.append(export_data)
        workspace.save_export(export_data["export_id"], export_data)
    exported["exports"] = len(exports)

    return exported


def main():
    print("=" * 60)
    print("  TopoChecker Mock Data -> Workspace Fixture Export")
    print("=" * 60)
    print()

    exported = export_mock_to_workspace()

    print("Export summary:")
    for key, count in exported.items():
        print(f"  {key}: {count} items")
    print()

    total = sum(exported.values())
    print(f"Total exported: {total} items")
    print()
    print("MOCK_EXPORT_TO_WORKSPACE_COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
