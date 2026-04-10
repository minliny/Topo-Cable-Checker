from src.domain.rule_engine import RuleEngine
from src.domain.fact_model import NormalizedDataset, DeviceFact, PortFact, LinkFact
from src.domain.baseline_model import BaselineProfile
from src.domain.rule_compiler import RuleCompiler

dataset = NormalizedDataset(
    devices=[
        DeviceFact(device_name="R1", device_type="Router", status="active", _source_sheet="Devices"),
        DeviceFact(device_name="S1", device_type="Switch", status="active", _source_sheet="Devices"),
        DeviceFact(device_name="S2", device_type="Switch", status="inactive", _source_sheet="Devices")
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
        "rule_dsl_1": {
            "rule_type": "dsl",
            "target_type": "devices",
            "expression": {
                "when": 'device_type == "Switch"',
                "assert": 'status == "active"'
            },
            "severity": "error"
        },
        "rule_template_1": {
            "rule_type": "template",
            "template": "group_consistency",
            "target_type": "devices",
            "params": {
                "group_key": "device_type",
                "comparison_field": "status"
            },
            "severity": "warning"
        }
    },
    parameter_profile={},
    threshold_profile={}
)

# Test Compilation directly
print("--- COMPILED RULES ---")
for rule_id, rule_def in baseline.rule_set.items():
    compiled = RuleCompiler.compile(rule_id, rule_def)
    print(f"{rule_id}: {compiled}")

# Test Execution
print("\n--- EXECUTION RESULTS ---")
engine = RuleEngine()
issues = engine.execute(dataset, baseline)
for issue in issues:
    print(f"[{issue.issue_id}] {issue.category} (severity: {issue.severity}): {issue.message}")
    print(f"Evidence: {issue.evidence}")

