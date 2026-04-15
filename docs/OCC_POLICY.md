# OCC Policy（Revision-based Optimistic Concurrency Control）

## 1. 目的

本项目使用 `revision` 作为基线（baseline）共享状态的并发控制 token，避免多窗口/多编辑者造成静默覆盖。

本文件定义“系统级一致性规则”，用于约束后续所有写入路径的 API 设计与实现方式，防止漏加 OCC。

## 2. 范围（Scope）

### 2.1 默认规则：所有 Baseline 共享持久化写入必须 OCC protect

凡是会写入 `baselines.json` 且可能影响以下共享状态的写操作，必须满足 OCC：

- baseline 的 `rule_set`、`baseline_version`、`baseline_version_snapshot`
- baseline 的 `working_draft`
- baseline 的任何其他用户可编辑字段（如未来扩展的名称、标签等）

OCC 规范：

- 请求必须携带 `expected_revision`
- 写入前必须校验 `expected_revision == current_revision`
- 冲突时返回 HTTP `409`
- 错误码必须为 `P1009`（`CONCURRENCY_CONFLICT`）

实现锚点：

- `BaselineProfile.revision`：[baseline_model.py](file:///workspace/src/domain/baseline_model.py)
- `BaselineRepository.save(..., expected_revision=...)`：[repository.py](file:///workspace/src/infrastructure/repository.py#L435-L468)
- `ConcurrencyError` + 409 映射：[exceptions.py](file:///workspace/src/crosscutting/errors/exceptions.py)、[error_handler.py](file:///workspace/src/presentation/api/error_handler.py)

### 2.2 不在 OCC 范围内的写入（Legitimate Exceptions by Scope）

以下写入路径目前不纳入 revision OCC（无 `expected_revision` contract），但仍属于“写路径审计矩阵”的一部分：

- `tasks.json`（任务状态流转）
- 各类运行产物 JSON（recognitions/run_executions/run_statistics/issue_aggregates/run_summaries/run_diffs/reviews/exports）
- 导出文件 `data/export_{run_id}.{fmt}`（一次性产物）

理由：这些对象不是“多人共同编辑同一份 baseline 的共享状态”，且当前模型未建立 revision token；在不修改 OCC 核心模型的约束下，属于 scope 外例外。

## 3. API 设计规范（Contract）

### 3.1 expected_revision 的放置规则

- **默认**：写操作使用 request body 字段 `expected_revision`
  - 例：`POST /api/rules/draft/save`
  - 例：`POST /api/rules/publish/{baseline_id}`
- **DELETE 例外（最小改动策略）**：使用 query 参数 `?expected_revision=<int>`
  - 例：`DELETE /api/rules/draft/{baseline_id}?expected_revision=...`

### 3.2 写操作返回值建议

- 若写入会导致 `revision` 变化，建议返回 `new_revision`，便于前端更新 token，避免后续请求立刻冲突。

## 4. 允许例外的条件（Exception Policy）

允许不纳入 OCC 的 baseline 写入仅限以下情形，且必须满足“可证明”的语义约束：

- **create-if-absent 幂等初始化**
  - 若目标 baseline 已存在：不得写入、不得覆盖、不得改变 revision
  - 若目标 baseline 不存在：仅创建一次，写入确定性默认内容

当前例子：

- `POST /api/baselines/bootstrap-default`（在满足上述条件且已通过自动化测试证明的前提下，可作为例外）

## 5. 测试护栏（Required Tests）

任何新增或修改的 baseline 写 endpoint 必须包含：

- happy path：正确 token 成功
- stale/unhappy path：错误 token 返回 409 + P1009
- 若声明为 Exception：必须有“已存在不覆盖”的证据测试（至少验证关键字段与 revision 不变）

