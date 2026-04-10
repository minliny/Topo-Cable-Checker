from src.domain.interfaces import IResultRepository
from src.domain.result_model import ExportArtifact
from src.crosscutting.config.settings import settings
import json
import dataclasses
import datetime
import os

class ExportService:
    def __init__(self, result_repo: IResultRepository = None):
        if result_repo is None:
            from src.infrastructure.repository import ResultRepository
            self.result_repo = result_repo or ResultRepository()
        else:
            self.result_repo = result_repo
    def export(self, run_id: str, fmt: str) -> ExportArtifact:
        issues = self.result_repo.get_issue_aggregate(run_id)
        if not issues:
            raise ValueError("No issues found to export.")

        data = json.dumps([i.__dict__ for i in issues.issues]).encode("utf-8")

        artifact = ExportArtifact(
            run_id=run_id,
            format=fmt,
            data=data
        )
        self.result_repo.save_export(artifact)

        # Write to disk securely using configured data directory
        data_dir = os.path.join(settings.BASE_DIR, "data")
        os.makedirs(data_dir, exist_ok=True)
        export_path = os.path.join(data_dir, f"export_{run_id}.{fmt}")
        with open(export_path, "wb") as f:
            f.write(data)

        return artifact
