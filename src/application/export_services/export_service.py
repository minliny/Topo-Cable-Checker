from src.infrastructure.repository import ResultRepository
from src.domain.result_model import ExportArtifact
import json

class ExportService:
    def __init__(self):
        self.result_repo = ResultRepository()
        
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
        # Write to disk
        with open(f"data/export_{run_id}.{fmt}", "wb") as f:
            f.write(data)
            
        return artifact
