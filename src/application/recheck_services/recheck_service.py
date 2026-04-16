from src.domain.interfaces import IResultRepository
from src.domain.result_model import RecheckDiffSnapshot, IssueItem
from typing import Dict, Any, Tuple
import dataclasses

class RecheckService:
    def __init__(self, result_repo: IResultRepository):
        self.result_repo = result_repo
        
    def _generate_match_key(self, issue: IssueItem) -> str:
        """
        Generates a stable, repeatable match key based on structure, NOT message.
        Includes device_name, port_name (if applicable), and rule_id.
        """
        rule_id = issue.evidence.get("rule_id", "Unknown")
        item_data = issue.evidence.get("item_data", {})
        
        # Determine the primary entity name
        device_name = item_data.get("device_name") or item_data.get("src_device") or "UnknownDevice"
        port_name = item_data.get("port_name") or item_data.get("src_port") or ""
        
        key = f"R:{rule_id}|D:{device_name}|P:{port_name}"
        return key

    def generate_diff(self, task_id: str, prev_run_id: str, curr_run_id: str) -> RecheckDiffSnapshot:
        prev_agg = self.result_repo.get_issue_aggregate(prev_run_id)
        curr_agg = self.result_repo.get_issue_aggregate(curr_run_id)
        
        prev_issues = prev_agg.issues if prev_agg else []
        curr_issues = curr_agg.issues if curr_agg else []
        
        # 1. Map issues by their stable structural key
        prev_map = {self._generate_match_key(i): i for i in prev_issues}
        curr_map = {self._generate_match_key(i): i for i in curr_issues}
        
        new_issues = []
        resolved_issues = []
        persistent_issues = []
        changed_issues = []
        
        # 2. Compare prev vs curr to find resolved, persistent, changed
        for key, p_issue in prev_map.items():
            if key not in curr_map:
                resolved_issues.append(p_issue)
            else:
                c_issue = curr_map[key]
                # Compare actual values or severity to determine if changed
                if p_issue.actual != c_issue.actual or p_issue.severity != c_issue.severity:
                    changed_issues.append({
                        "key": key,
                        "previous": dataclasses.asdict(p_issue),
                        "current": dataclasses.asdict(c_issue)
                    })
                else:
                    persistent_issues.append(c_issue)
                    
        # 3. Compare curr vs prev to find new issues
        for key, c_issue in curr_map.items():
            if key not in prev_map:
                new_issues.append(c_issue)
                
        # 4. Calculate Risk Trend
        total_prev = len(prev_issues)
        total_curr = len(curr_issues)
        
        def get_sev_count(issues):
            counts = {"error": 0, "warning": 0, "info": 0, "medium": 0}
            for i in issues:
                counts[i.severity] = counts.get(i.severity, 0) + 1
            return counts
            
        prev_sev = get_sev_count(prev_issues)
        curr_sev = get_sev_count(curr_issues)
        
        severity_diff = {}
        for sev in set(list(prev_sev.keys()) + list(curr_sev.keys())):
            diff_val = curr_sev.get(sev, 0) - prev_sev.get(sev, 0)
            severity_diff[sev] = diff_val

        per_device_diff = {}
        # Calculate per device diff based on current vs prev aggregations
        if curr_agg and prev_agg:
            all_devices = set(list(curr_agg.by_device.keys()) + list(prev_agg.by_device.keys()))
            for dev in all_devices:
                diff_val = curr_agg.by_device.get(dev, 0) - prev_agg.by_device.get(dev, 0)
                per_device_diff[dev] = diff_val

        risk_trend = {
            "total_issues_diff": total_curr - total_prev,
            "severity_diff": severity_diff,
            "per_device_diff": per_device_diff
        }

        # 5. Build Snapshot
        diff_snapshot = RecheckDiffSnapshot(
            task_id=task_id,
            prev_run_id=prev_run_id,
            curr_run_id=curr_run_id,
            diff_data={
                "new": len(new_issues),
                "resolved": len(resolved_issues),
                "persistent": len(persistent_issues),
                "changed": len(changed_issues)
            },
            new_issues=new_issues,
            resolved_issues=resolved_issues,
            persistent_issues=persistent_issues,
            changed_issues=changed_issues,
            risk_trend=risk_trend
        )
        self.result_repo.save_diff(diff_snapshot)
        return diff_snapshot
