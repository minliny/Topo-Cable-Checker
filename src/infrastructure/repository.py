import json
import os
import dataclasses
from typing import Any, Dict, List
from src.domain.task_model import CheckTask, TaskStatus
from src.domain.baseline_model import BaselineProfile
from src.domain.result_model import (
    RecognitionResultSnapshot, RunExecutionSnapshot, RunSummaryOverview,
    RunStatisticsSnapshot, IssueItem, IssueAggregateSnapshot, DeviceReviewContext, RecheckDiffSnapshot, ExportArtifact
)
from src.crosscutting.config.settings import settings
import datetime

DATA_DIR = os.path.join(settings.BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

def _read_json(file_name: str) -> Dict:
    path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def _write_json(file_name: str, data: Dict):
    path = os.path.join(DATA_DIR, file_name)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)

class BaselineRepository:
    def get_all(self) -> List[BaselineProfile]:
        data = _read_json("baselines.json")
        return [BaselineProfile(**v) for v in data.values()]
        
    def get_by_id(self, baseline_id: str) -> BaselineProfile:
        data = _read_json("baselines.json")
        if baseline_id in data:
            return BaselineProfile(**data[baseline_id])
        return None

    def save(self, profile: BaselineProfile):
        data = _read_json("baselines.json")
        data[profile.baseline_id] = profile.__dict__
        _write_json("baselines.json", data)

class TaskRepository:
    def get_by_id(self, task_id: str) -> CheckTask:
        data = _read_json("tasks.json")
        if task_id in data:
            d = data[task_id]
            d["task_status"] = TaskStatus(d["task_status"])
            d["created_at"] = datetime.datetime.fromisoformat(d["created_at"])
            return CheckTask(**d)
        return None

    def save(self, task: CheckTask):
        data = _read_json("tasks.json")
        d = task.__dict__.copy()
        d["task_status"] = d["task_status"].value
        data[task.task_id] = d
        _write_json("tasks.json", data)

class ResultRepository:
    def save_recognition(self, snap: RecognitionResultSnapshot):
        d = _read_json("recognitions.json")
        d[snap.task_id] = snap.__dict__
        _write_json("recognitions.json", d)

    def get_recognition(self, task_id: str) -> RecognitionResultSnapshot:
        d = _read_json("recognitions.json")
        return RecognitionResultSnapshot(**d[task_id]) if task_id in d else None

    def save_run_execution(self, snap: RunExecutionSnapshot):
        d = _read_json("run_executions.json")
        d[snap.run_id] = snap.__dict__
        _write_json("run_executions.json", d)

    def save_statistics(self, snap: RunStatisticsSnapshot):
        d = _read_json("run_statistics.json")
        d[snap.run_id] = snap.__dict__
        _write_json("run_statistics.json", d)

    def get_statistics(self, run_id: str) -> RunStatisticsSnapshot:
        d = _read_json("run_statistics.json")
        return RunStatisticsSnapshot(**d[run_id]) if run_id in d else None

    def save_issue_aggregate(self, snap: IssueAggregateSnapshot):
        d = _read_json("issue_aggregates.json")
        dd = snap.__dict__.copy()
        dd["issues"] = [i.__dict__ for i in dd["issues"]]
        d[snap.run_id] = dd
        _write_json("issue_aggregates.json", d)
        
    def get_issue_aggregate(self, run_id: str) -> IssueAggregateSnapshot:
        d = _read_json("issue_aggregates.json")
        if run_id in d:
            dd = d[run_id]
            dd["issues"] = [IssueItem(**i) for i in dd["issues"]]
            return IssueAggregateSnapshot(**dd)
        return None

    def save_summary(self, summary: RunSummaryOverview):
        d = _read_json("run_summaries.json")
        d[summary.run_id] = summary.__dict__
        _write_json("run_summaries.json", d)
        
    def get_summary(self, run_id: str) -> RunSummaryOverview:
        d = _read_json("run_summaries.json")
        return RunSummaryOverview(**d[run_id]) if run_id in d else None

    def save_diff(self, snap: RecheckDiffSnapshot):
        d = _read_json("run_diffs.json")
        d[f"{snap.prev_run_id}_{snap.curr_run_id}"] = snap.__dict__
        _write_json("run_diffs.json", d)

    def save_review(self, snap: DeviceReviewContext):
        d = _read_json("reviews.json")
        dd = snap.__dict__.copy()
        dd["related_issues"] = [i.__dict__ for i in dd["related_issues"]]
        d[f"{snap.run_id}_{snap.device_name}"] = dd
        _write_json("reviews.json", d)
        
    def get_diff(self, prev_run_id: str, curr_run_id: str) -> RecheckDiffSnapshot:
        d = _read_json("run_diffs.json")
        k = f"{prev_run_id}_{curr_run_id}"
        return RecheckDiffSnapshot(**d[k]) if k in d else None
        
    def get_review(self, run_id: str, device_name: str) -> DeviceReviewContext:
        d = _read_json("reviews.json")
        k = f"{run_id}_{device_name}"
        if k in d:
            dd = d[k]
            dd["related_issues"] = [IssueItem(**i) for i in dd["related_issues"]]
            return DeviceReviewContext(**dd)
        return None
