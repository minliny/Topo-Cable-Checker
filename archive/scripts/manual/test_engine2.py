from src.domain.rule_engine import RuleEngine
from src.domain.fact_model import NormalizedDataset, DeviceFact, PortFact, LinkFact
from src.domain.baseline_model import BaselineProfile

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
        "rule_4": {
            "executor": "threshold",
            "target_type": "devices",
            "metric_type": "distinct_count",
            "metric_field": "device_type",
            "threshold_key": "distinct_device_types"
        }
    },
    parameter_profile={},
    threshold_profile={
        "distinct_device_types": {
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
