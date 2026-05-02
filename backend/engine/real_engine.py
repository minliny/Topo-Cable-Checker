# backend/engine/real_engine.py
# RealEngineAdapter scaffold: implements EngineAdapter interface.
# Current implementation:
#   - Recognition: reads local Excel/CSV via LocalInputReader + DatasetRecognizer
#   - Execution: generates empty CheckResultBundle scaffold
# No real check engine integration, no database, no external AI.

import os
import uuid
from pathlib import Path
from typing import Optional

from .interface import EngineAdapter
from ..repositories.provider import get_repository
from ..input import LocalInputReader, normalize_raw_dataset
from ..recognition import DatasetRecognizer, infer_and_summarize_tables
from ..workspace.manager import WorkspaceManager
from ..models.execution import (
    CheckResultBundle,
    DataSource,
    ExecutionScope,
    IssueItem,
    RecognitionResult,
    RunHistoryEntry,
)
from ..models.diff import RecheckDiffSnapshot


class RealEngineAdapter(EngineAdapter):
    """Real engine adapter scaffold.

    Current implementation:
    - Recognition: reads local Excel/CSV via LocalInputReader + DatasetRecognizer
    - Recognition: infers device types via infer_and_summarize_tables
    - Execution: generates empty CheckResultBundle scaffold (no real rules)
    - Other methods: scaffold (NotImplementedError)

    To activate: set TOPOCHECKER_ENGINE=real
    This is NOT for production use.
    """

    def __init__(self):
        self.repo = get_repository()
        self.workspace = WorkspaceManager()
        self.reader = LocalInputReader()
        self.recognizer = DatasetRecognizer()

    # ── Recognition ──────────────────────────────────────────────

    async def get_recognition_status(self) -> str:
        """Return current recognition status.

        Returns 'not_started' to maintain API compatibility.
        Real recognition status is determined after start_recognition.
        """
        return "not_started"

    async def start_recognition(self, data_source_id: str, scope_id: str) -> str:
        """Start device recognition by reading local input file.

        Reads Excel/CSV file, normalizes data, saves to workspace.
        Returns recognition_id.
        """
        recognition_id = f"rec-{uuid.uuid4().hex[:8]}"

        # Find input file path
        # Use data_source_id as hint or default to sample file
        input_dir = self.workspace.paths.inputs
        input_file = self._find_input_file(input_dir, data_source_id)

        if input_file and input_file.exists():
            # Read and normalize
            raw = self.reader.read_file(str(input_file))
            normalized = normalize_raw_dataset(raw)

            # Recognize tables using DatasetRecognizer
            recognition_summary = self.recognizer.recognize(normalized)

            # Infer device types
            recognition_summary = infer_and_summarize_tables(recognition_summary)

            # Save recognition metadata to workspace/snapshots/
            recognition_data = {
                "recognition_id": recognition_id,
                "data_source_id": data_source_id,
                "scope_id": scope_id,
                "status": "completed",
                "source_file": str(input_file),
                "dataset_id": normalized.dataset_id,
                "normalized_at": normalized.normalized_at.isoformat(),
                "sheet_count": normalized.sheet_count,
                "total_row_count": normalized.total_row_count,
                "tables": normalized.tables,
                "recognition_summary": recognition_summary.model_dump(mode="json"),
            }

            # Save to snapshots as recognition/{recognition_id}.json
            snapshot_path = self._save_recognition_snapshot(recognition_id, recognition_data)

            return recognition_id
        else:
            # No input file found, return recognition_id with empty result
            recognition_data = {
                "recognition_id": recognition_id,
                "data_source_id": data_source_id,
                "scope_id": scope_id,
                "status": "completed",
                "source_file": None,
                "dataset_id": None,
                "normalized_at": None,
                "sheet_count": 0,
                "total_row_count": 0,
                "tables": [],
                "recognition_summary": None,
            }
            self._save_recognition_snapshot(recognition_id, recognition_data)
            return recognition_id

    async def get_recognition_result(self, recognition_id: str) -> Optional[RecognitionResult]:
        """Get recognition result from saved snapshot.

        Uses recognition_summary to generate RecognitionResult.
        """
        snapshot = self._load_recognition_snapshot(recognition_id)

        if not snapshot:
            return None

        # Get recognition summary from snapshot
        summary = snapshot.get("recognition_summary")

        if summary:
            # Use recognition summary counts
            device_count = summary.get("total_device_count", 0)
            warnings = summary.get("warnings", [])
        else:
            # Fallback to raw counts
            device_count = snapshot.get("total_row_count", 0)
            warnings = []

        return RecognitionResult(
            recognized_device_count=device_count,
            unmatched_device_count=0,
            out_of_scope_device_count=0,
            warnings=warnings,
        )

    async def confirm_recognition(self, recognition_id: str) -> bool:
        """Confirm recognition result (scaffold: always True)."""
        snapshot = self._load_recognition_snapshot(recognition_id)

        if not snapshot:
            return False

        # Mark as confirmed
        snapshot["status"] = "confirmed"
        self._save_recognition_snapshot(recognition_id, snapshot)
        return True

    # ── Execution ────────────────────────────────────────────────

    async def start_check(
        self,
        baseline_id: str,
        data_source_id: str,
        scope_id: str,
        parameter_profile_id: Optional[str] = None,
        threshold_profile_id: Optional[str] = None,
    ) -> str:
        """Start check execution (scaffold: generates empty CheckResultBundle).

        This is a scaffold implementation. It generates an empty CheckResultBundle
        without executing any real rules.

        Returns:
            run_id: The ID of the generated check run.
        """
        from datetime import datetime

        run_id = f"run-{uuid.uuid4().hex[:8]}"

        # Find recognition_id for the data source
        recognition_id = self._find_recognition_id(data_source_id)

        # Get baseline info from repository
        baseline_name = baseline_id
        scenario_id = "scenario-default"
        try:
            baseline = self.repo.get_baseline_by_id(baseline_id)
            if baseline:
                baseline_name = baseline.name if hasattr(baseline, 'name') else baseline_id
        except Exception:
            pass

        # Build workspace run data with all RunHistoryEntry required fields
        run_data = {
            "run_id": run_id,
            "baseline_id": baseline_id,
            "baseline_name": baseline_name,
            "scenario_id": scenario_id,
            "status": "scaffold_completed",
            "severity_summary": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
            },
            "device_count": 0,
            "issue_count": 0,
            "data_source_id": data_source_id,
            "scope_id": scope_id,
            "recognition_id": recognition_id,
            "parameter_profile_id": parameter_profile_id,
            "threshold_profile_id": threshold_profile_id,
            "bundle_id": f"bundle-{uuid.uuid4().hex[:8]}",
            "created_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
        }

        # Save run metadata to workspace/runs/
        self._save_run_data(run_id, run_data)

        return run_id

    async def get_run_status(self, run_id: str) -> str:
        """Get run status from workspace run data.

        Returns 'scaffold_completed' for scaffold runs.
        """
        run_data = self._load_run_data(run_id)
        if run_data:
            return run_data.get("status", "completed")
        return "completed"

    # ── Results ──────────────────────────────────────────────────

    async def get_bundle(self, run_id: str) -> Optional[CheckResultBundle]:
        """Get CheckResultBundle for a run from workspace.

        Generates an empty CheckResultBundle for scaffold runs.
        """
        from ..models.execution import SeveritySummary

        run_data = self._load_run_data(run_id)

        if run_data:
            bundle_id = run_data.get("bundle_id", f"bundle-{uuid.uuid4().hex[:8]}")
            return CheckResultBundle(
                bundle_id=bundle_id,
                run_id=run_id,
                baseline_id=run_data.get("baseline_id", "baseline-001"),
                severity_summary=SeveritySummary(),
                issue_count=0,
                issues=[],
                created_at=run_data.get("completed_at"),
            )

        return None

    async def get_issue(self, issue_id: str) -> Optional[IssueItem]:
        raise NotImplementedError(
            "RealEngineAdapter: get_issue not implemented (scaffold only)"
        )

    # ── Diff ─────────────────────────────────────────────────────

    async def get_recheck_diff(
        self, base_run_id: str, target_run_id: str
    ) -> Optional[RecheckDiffSnapshot]:
        raise NotImplementedError(
            "RealEngineAdapter: get_recheck_diff not implemented (scaffold only)"
        )

    # ── Metadata (optional, may delegate to repository) ──────────

    async def list_data_sources(self) -> list[DataSource]:
        """List available data sources."""
        return self.repo.get_all_data_sources()

    async def list_scopes(self) -> list[ExecutionScope]:
        """List available execution scopes."""
        return self.repo.get_all_execution_scopes()

    # ── Helper Methods ────────────────────────────────────────────

    def _find_input_file(self, input_dir: Path, data_source_id: str) -> Optional[Path]:
        """Find input file in workspace/inputs/."""
        if not input_dir.exists():
            return None

        # Look for file matching data_source_id or default sample file
        extensions = [".csv", ".xlsx", ".xls"]

        for ext in extensions:
            # Try data_source_id as filename
            file_path = input_dir / f"{data_source_id}{ext}"
            if file_path.exists():
                return file_path

            # Try sample file
            sample_path = input_dir / f"sample{ext}"
            if sample_path.exists():
                return sample_path

        # Return first file found
        for ext in extensions:
            files = list(input_dir.glob(f"*{ext}"))
            if files:
                return files[0]

        return None

    def _save_recognition_snapshot(
        self, recognition_id: str, data: dict
    ) -> Path:
        """Save recognition snapshot to workspace/snapshots/recognition/."""
        recognition_dir = self.workspace.paths.snapshots / "recognition"
        recognition_dir.mkdir(parents=True, exist_ok=True)

        file_path = recognition_dir / f"{recognition_id}.json"
        import json
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return file_path

    def _load_recognition_snapshot(self, recognition_id: str) -> Optional[dict]:
        """Load recognition snapshot from workspace/snapshots/recognition/."""
        file_path = self.workspace.paths.snapshots / "recognition" / f"{recognition_id}.json"
        if not file_path.exists():
            return None

        import json
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _find_recognition_id(self, data_source_id: str) -> Optional[str]:
        """Find recognition_id for a data source from recent snapshots."""
        recognition_dir = self.workspace.paths.snapshots / "recognition"
        if not recognition_dir.exists():
            return None

        # Find the most recent recognition snapshot matching data_source_id
        import json
        for snapshot_file in sorted(recognition_dir.glob("rec-*.json"), reverse=True):
            with open(snapshot_file, "r", encoding="utf-8") as f:
                snapshot = json.load(f)
                if snapshot.get("data_source_id") == data_source_id:
                    return snapshot.get("recognition_id")
        return None

    def _save_run_data(self, run_id: str, data: dict) -> Path:
        """Save run data to workspace/runs/."""
        runs_dir = self.workspace.paths.runs
        runs_dir.mkdir(parents=True, exist_ok=True)

        file_path = runs_dir / f"{run_id}.json"
        import json
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return file_path

    def _load_run_data(self, run_id: str) -> Optional[dict]:
        """Load run data from workspace/runs/."""
        file_path = self.workspace.paths.runs / f"{run_id}.json"
        if not file_path.exists():
            return None

        import json
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
