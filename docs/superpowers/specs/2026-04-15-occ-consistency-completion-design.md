# Phase C2.5：OCC Consistency Completion — Design

## 背景

项目在 Phase C2 引入了基于 `revision` 的 optimistic concurrency control（OCC），采用：

- 写入请求携带 `expected_revision`
- 发生冲突返回 HTTP 409
- 错误码使用 `P1009`（`CONCURRENCY_CONFLICT`）

当前 OCC 仅覆盖主写路径（draft save / publish），存在“半一致性系统规则”的风险。

## 目标

在不修改 OCC 核心模型（revision 机制本身）的前提下，将 OCC 从“主路径能力”提升为“系统级一致性规则”：

1. 全量识别所有真实写操作入口，并分类 OCC 覆盖状态
2. 对所有“应受保护但未保护”的共享状态写路径补齐 OCC
3. 对所有例外路径给出严格、可审计、可持续执行的策略约束
4. 输出可持续的 OCC Policy 文档，并同步状态面/快照文档

## 非目标

- 不引入 tasks/results 的 revision 机制
- 不将 OCC 扩展为全系统通用事务/锁机制
- 不做无关架构重构或新功能

## 范围界定

### 受 OCC 保护的共享状态

OCC 的一致性规则仅覆盖 `baselines.json` 代表的共享状态（baseline/draft/publish/clear 等），因为该部分存在多窗口/多编辑者的典型并发覆盖风险，且已建立 revision contract。

### 不纳入 OCC 的写入（默认候选例外）

`tasks.json` 与各类 `results*.json` 写入被纳入“写路径审计矩阵”，但默认作为 OCC 机制的例外范围（无 revision contract）。对例外的合理性必须在 Policy 中明确：它们通常是 append/replace by run_id/task_id 的运行记录，不属于“多人共同编辑同一份 baseline 的共享状态”。

## Task 1：全写路径 OCC 审计（矩阵输出）

输出矩阵（强制字段）：

| Write Path | Mutates What | OCC Status | Why |

写路径枚举必须包含：

- FastAPI 写入路由（POST/PUT/PATCH/DELETE）
- Application service 中所有调用 `repo.save()` / `_write_json()` 的路径
- CLI/脚本写入口（若触发持久化写入）

并强制覆盖至少：

- clear draft
- rollback / restore version（若存在落盘回滚）
- bootstrap / create baseline
- clone / duplicate baseline
- delete / archive / rename / reorder（若存在）

### bootstrap-default 的特别要求（批准后的调整）

bootstrap-default 暂不得直接归类为 Legitimate Exception，必须先证明其真实语义属于：

- create-if-not-exists
- 绝不覆盖已有 baseline 状态

若实际为 upsert/overwrite，则必须纳入 OCC 或重构为显式 create-if-absent 语义。

## Task 2：补齐缺失 OCC 覆盖（推荐方案 A）

### clear draft（必须补齐）

目标：将 clear draft 与 save/publish 一致化为 OCC 保护写路径。

- API 设计：保留既有 endpoint，采用 query 参数（最小改动）
  - `DELETE /api/rules/draft/{baseline_id}?expected_revision=<int>`
- 错误语义：与 C2 保持一致
  - 发生冲突：409 + `error_code=P1009`
- Service/Repo：沿用现有 `BaselineRepository.save(..., expected_revision=...)`
- 前端：调用 clear 时必须携带 token；冲突时提示 stale/refresh required；禁止静默覆盖

### bootstrap-default（条件成立才可例外）

在完成语义证明后：

- 若为严格 create-if-absent 且不覆盖：可作为 OCC Exception（幂等初始化例外）
- 否则：纳入 OCC 或重构为显式 create-if-absent

## Task 3：OCC Policy 文档

新增/更新文档以防未来漏加 OCC：

- `docs/OCC_POLICY.md`
  - 默认规则：所有写 `baselines.json` 的共享状态入口必须 OCC protect
  - 例外条件：仅允许“幂等初始化 create-if-absent 且不覆盖”的写路径例外，并要求证据
  - API 规范：`expected_revision` 命名、放置位置（body vs query）、错误语义（409/P1009）
  - 测试要求：每个写入口必须具备 happy/stale/unhappy path 的自动化测试
- 更新状态面文档（如 `docs/PROJECT_STATE_SNAPSHOT.yaml`）反映覆盖范围

## 测试策略

必须新增/补齐：

- clear draft
  - valid token → 200
  - stale token → 409 + P1009
- bootstrap-default
  - 证明其“已存在时不写入/不覆盖”的语义（必要时增加针对 revision 不变、rule_set 不变的断言）

