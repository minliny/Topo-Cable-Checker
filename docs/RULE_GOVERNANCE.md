# Rule Governance

## Overview
This platform extends the Rule Engine to support structured rule governance. Rules are no longer opaque configurations; they are explicitly managed entities whose compilation and validation lifecycle can be traced, audited, and viewed via the Local Web UI.

## Baseline and Rule Definition Relationship
A `RuleDefinitionDTO` represents the raw logic configured by users or domain experts. It lives inside a specific Baseline (`BaselineProfile`).
The governance layer tracks each rule's provenance, capturing the `baseline_version` and the `language_version` it was written for.

## The Role of Compiled Rules
Not all rules run exactly as written. The system compiles abstract DSL and Template definitions into concrete `CompiledRuleDTO` models using the `RuleCompiler`. The governance layer stores these compiled rules to provide complete transparency into exactly which executor, parameters, and thresholds will be invoked at runtime.

## Managing Compile Errors
A rule that fails compilation does not crash the system silently nor is it simply ignored. The governance layer captures and persists `CompileErrorDTO` instances. This structured error capture guarantees that invalid configurations (e.g., `unsupported_language_version`, missing parameters) are explicitly flagged in the UI for operators to audit and fix.

## Language Version in Governance
Every `RuleDefinitionDTO` captures its `language_version`. The system uses this to guarantee backward compatibility and deterministic compilation. If a rule specifies a language version no longer supported by the compiler, it yields a deterministic `unsupported_language_version` compilation error.

## UI Integration
Read-only views of the Rule Governance layer are available via the Local Web UI:
- `/rules`: Lists all definitions, their enabled status, and compilation results.
- `/rules/{baseline_id}/{rule_id}`: Provides detailed traceability from raw definitions to the compiled underlying structures or exact errors.
- `/templates`: Displays the registered capabilities available for rule authors.
