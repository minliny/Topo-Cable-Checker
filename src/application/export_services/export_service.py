from src.domain.interfaces import IResultRepository, IFileStorage
from src.domain.result_model import ExportArtifact
import json

class ExportService:
    def __init__(self, result_repo: IResultRepository, file_storage: IFileStorage):
        self.result_repo = result_repo
        self.file_storage = file_storage
        
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

        # Delegate raw file writing to infrastructure
        self.file_storage.write_artifact(f"export_{run_id}.{fmt}", data)

        return artifact
