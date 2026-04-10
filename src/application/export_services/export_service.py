from src.domain.interfaces import IResultRepository
from src.domain.result_model import ExportArtifact
import json
import dataclasses
import datetime

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
        
        # Write to disk
        with open(f"data/export_{run_id}.{fmt}", "wb") as f:
            f.write(data)
            
        return artifact
