# Rule Language Specification

## 1. Language Version
Current Language Version: **v1.0**

All rule definitions MUST declare their language version or they will be evaluated against the latest specification by default. If an unsupported `language_version` is provided, the compiler will return an `unsupported_language_version` error.

## 2. Supported Rule Definition Forms
The rule engine supports two primary paradigms for expressing rules:
- **DSL (Domain Specific Language)**: Used for precise, single-fact assertion logic.
- **Template**: Used for complex, multi-fact patterns such as aggregations, consistencies, and topologies.

## 3. DSL Syntax Specification
### 3.1 `when` Clause (Scope Selection)
Defines the preconditions for the rule to apply.
- **Simple Equality**: `when: 'field == "value"'`
- **Multiple Conditions (`when.all`)**:
  ```yaml
  when:
    all:
      - 'device_type == "Switch"'
      - 'status exists'
  ```

### 3.2 `assert` Clause (Assertion Logic)
Defines the rule expectation.
- **Simple Equality**: `assert: 'status == "active"'`
- **Regex Match (`assert.regex`)**:
  ```yaml
  assert:
    regex:
      field: device_name
      pattern: '^SW-\d{2}$'
  ```
- **Existence Check (`assert.exists`)**:
  ```yaml
  assert:
    exists: port_status
  ```

## 4. Target Type Support Scope
Rules can be evaluated against the following target types:
- `devices`
- `ports`
- `links`

## 5. Template Registry Specification
Templates provide pre-packaged logic that is translated to underlying executors.
- `group_consistency`: Asserts that a defined `comparison_field` is uniform across items grouped by `group_key`.
- `threshold_check`: Evaluates a numeric threshold (`count` or `distinct_count`) against a dataset.
- `topology_assertion`: Validates connections between source and target entities.

## 6. Compile Error Type Manifest
The `RuleCompiler` will emit structured errors under the `RuleCompileError` exception class:
- `unsupported_language_version`: Provided version is not supported by the compiler.
- `unknown_rule_type`: Rule type is neither `dsl` nor `template`.
- `unsupported_target_type`: Target type is not one of the allowed scopes.
- `invalid_dsl_expression`: Syntax error within the DSL expression.
- `unknown_template`: Template name is not found in the registry.
- `missing_required_param`: A mandatory parameter for the template or DSL structure is missing.

## 7. Compiled Rule Standard Structure
A successfully compiled rule will always map to an underlying executor definition.
**DSL Example**:
```yaml
executor: single_fact
scope_selector:
  target_type: devices
  device_type: Switch
field: status
type: field_equals
expected: active
severity: medium
```

**Template Example**:
```yaml
executor: group_consistency
scope_selector:
  target_type: devices
group_key: device_type
comparison_field: status
severity: warning
```
