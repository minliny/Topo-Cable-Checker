import sys

with open("docs/PROJECT_STATE_SNAPSHOT.yaml", "r") as f:
    orig = f.read()

orig = orig.replace(
    'status: "L4.0 稳定，Input Contract + Rule Engine Externalization 已合并"',
    'status: "L4 Alpha 降级，发现 W16 Draft Model / Stale UI / Debounce 为假实现"'
)
orig = orig.replace(
    'current_maturity: L4',
    'current_maturity: L4 Alpha'
)
orig = orig.replace(
    'overall: "L4.0"',
    'overall: "L4 Alpha (Downgraded due to W16 false claims)"'
)
orig = orig.replace(
    'target: "L4 (Production-like Solo Tool)"',
    'target: "重新回到 L4 Stable，修复 W16 假实现"'
)

risks = """
  - id: "RISK-009"
    severity: "Critical"
    description: "W16 Fake Implementation: Draft payload accepts only single rule_id, breaking multi-rule save semantics."
    file: "src/presentation/api/routers/rules.py, dto_models.py"
  - id: "RISK-010"
    severity: "Critical"
    description: "W16 Fake Implementation: Validate/Publish/Diff endpoints do not support rule_set, destroying full workflow."
    file: "src/presentation/api/routers/rules.py, dto_models.py"
  - id: "RISK-011"
    severity: "Critical"
    description: "W16 Fake Implementation: pageReducer.ts UPDATE_DRAFT fails to clear validationResult, causing stale UI."
    file: "frontend/src/store/pageReducer.ts"
"""

orig = orig.replace(
    'remaining_risks:\n',
    'remaining_risks:\n' + risks
)

with open("docs/PROJECT_STATE_SNAPSHOT.yaml", "w") as f:
    f.write(orig)

