# Business Flow Status

The main execution flow is defined as:
**Rule Baseline → Check Task → Data Recognition → Recognition Confirmation → Normalization → Check Execution → Summary Overview → Issue Drill-down → Logic Review → Export → Recheck Diff**.

- `CheckTask` is implemented and governs the state transitions.
- The rule engine consumes normalized data from the domain layer.
