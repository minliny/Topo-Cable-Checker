from src.domain.rule_engine import RuleEngine
from src.domain.fact_model import NormalizedDataset, DeviceFact, PortFact, LinkFact
from src.domain.baseline_model import BaselineProfile
import dataclasses

dataset = NormalizedDataset(
    devices=[
        DeviceFact(device_name="R1", device_type="Router", status="Active", _source_sheet="Devices"),
        DeviceFact(device_name="S1", device_type="Switch", status="Active", _source_sheet="Devices"),
        DeviceFact(device_name="S2", device_type="Switch", status="Inactive", _source_sheet="Devices")
    ],
    ports=[],
    links=[]
)

baseline = BaselineProfile(
    baseline_id="b1",
    baseline_version="v1",
    recognition_profile={},
    naming_profile={},
    baseline_version_snapshot={},
    rule_set={
        "rule_1": {
            "executor": "threshold",
            "target_type": "devices",
            "metric_type": "count",
            "threshold_key": "total_devices",
        },
        "rule_2": {
            "executor": "threshold",
            "target_type": "devices",
            "metric_type": "count",
            "scope_selector": {
                "device_type": "Switch"
            },
            "threshold_key": "switch_count",
        },
        "rule_3": {
            "executor": "group_consistency",
            "target_type": "devices",
            "scope_selector": {
                "device_type": "Switch"
            },
            "parameter_key": "switch_status_check"
        }
    },
    parameter_profile={
        "switch_status_check": {
            "group_key": "device_type",
            "comparison_field": "status"
        }
    },
    threshold_profile={
        "total_devices": {
            "operator": "between",
            "min_value": 2,
            "max_value": 10
        },
        "switch_count": {
            "operator": "gte",
            "value": 3
        }
    }
)

engine = RuleEngine()
issues = engine.execute(dataset, baseline)
print(f"Total issues found: {len(issues)}")
for issue in issues:
    print(issue.message)
    print(issue.evidence)
