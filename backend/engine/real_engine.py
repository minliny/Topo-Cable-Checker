# backend/engine/real_engine.py
# RealEngineAdapter scaffold: implements EngineAdapter interface.
# Current implementation: recognition scaffold using LocalInputReader.
# No real check engine integration, no database, no external AI.

import os
import uuid
from pathlib import Path
from typing import Optional

from .interface import EngineAdapter
from ..repositories.provider import get_repository
from ..input import LocalInputReader, normalize_raw_dataset
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
    - Recognition: reads local Excel/CSV via LocalInputReader
    - Other methods: scaffold (NotImplementedError)

    To activate: set TOPOCHECKER_ENGINE=real
    This is NOT for production use.
    """

    def __init__(self):
        self.repo = get_repository()
        self.workspace = WorkspaceManager()
        self.reader = LocalInputReader()

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
            }
            self._save_recognition_snapshot(recognition_id, recognition_data)
            return recognition_id

    async def get_recognition_result(self, recognition_id: str) -> Optional[RecognitionResult]:
        """Get recognition result from saved snapshot."""
        snapshot = self._load_recognition_snapshot(recognition_id)

        if not snapshot:
            return None

        # Extract counts from normalized dataset
        row_count = snapshot.get("total_row_count", 0)
        tables = snapshot.get("tables", [])

        # Simple heuristic: row_count = devices, unmatched = 0, out_of_scope = 0
        return RecognitionResult(
            recognized_device_count=row_count,
            unmatched_device_count=0,
            out_of_scope_device_count=0,
            warnings=[],
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
        raise NotImplementedError(
            "RealEngineAdapter: start_check not implemented (scaffold only)"
        )

    async def get_run_status(self, run_id: str) -> str:
        raise NotImplementedError(
            "RealEngineAdapter: get_run_status not implemented (scaffold only)"
        )

    # ── Results ──────────────────────────────────────────────────

    async def get_bundle(self, run_id: str) -> Optional[CheckResultBundle]:
        raise NotImplementedError(
            "RealEngineAdapter: get_bundle not implemented (scaffold only)"
        )

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
