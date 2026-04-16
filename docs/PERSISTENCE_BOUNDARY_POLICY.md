# Persistence Boundary Policy

*(Established in Phase C3.3 Persistence Decoupling Preparation)*  
Route C (Hybrid Transitional Route) assumes file-based persistence remains for now. This policy exists to ensure future storage evolution (DB-backed repo / service-backed storage) has a narrow and explicit change surface.

## 1. Persistence Payload vs Domain Meaning

### 1.1 BaselineProfile 的“载荷字段”
在 [baseline_model.py](file:///workspace/src/domain/baseline_model.py) 中，以下字段属于“持久化载荷”（payload），而不是稳定领域契约：
- `rule_set`
- `baseline_version_snapshot`
- `version_history_meta`
- `working_draft`

这些字段在当前实现里使用 `Dict[str, Any]`（及其 type alias）承载，仅代表“当前 file/JSON persistence 下的表示”，不保证内部结构永远稳定。

### 1.2 允许保留 Dict，但必须显式化
- 允许 payload 继续是 dict
- 但服务层/路由层不得把 dict 的内部键集合当作长期稳定契约
- 如需对 payload 内部结构做依赖，必须通过 Application 层的显式 assembler/mapper（保持轻量）

## 2. Repository Contract vs JSON Representation

### 2.1 Repository Contract（对上层）
[IBaselineRepository](file:///workspace/src/domain/interfaces.py#L10-L14) 的契约面向 `BaselineProfile`：
- `get_by_id` / `get_all` 返回 `BaselineProfile`
- `save` 接受 `BaselineProfile`

禁止上层把 `repo.save({..dict..})` 当成可用路径。该路径在 [repository.py](file:///workspace/src/infrastructure/repository.py) 已明确拒绝（TypeError）。

### 2.2 JSON Representation（对下层）
JSON schema、schema migration、revision/OCC、single-writer lock 都属于 Repository 的内部实现细节：
- Application / Presentation 层不得依赖这些细节来做业务判断
- 若需要暴露给外部（例如诊断/观测），必须通过 DTO/事件等显式边界输出

## 3. Draft / Version / Snapshot 生命周期边界

### 3.1 当前状态集合（事实）
- `working_draft`: 单条规则草稿（可保存但不保证可发布）
- `rule_set`: 当前 baseline_version 对应的已发布规则集合
- `baseline_version_snapshot`: 已发布历史版本的规则集合快照（按版本号索引）
- `baseline_version`: 当前已发布版本号

### 3.2 生命周期（文字图）
- Save Draft：
  - 写入 `working_draft`
  - 不修改 `rule_set`
  - revision +1
- Publish Draft：
  - 将发布前 `rule_set` 存入 `baseline_version_snapshot[current_version]`
  - 将草稿编译后的 rule_def 写入 `rule_set[rule_id]`
  - bump `baseline_version`
  - 清空 `working_draft`
  - revision +1
- Diff：
  - diff 的 source 可以是：
    - `baseline_version`（当前 `rule_set`）
    - `baseline_version_snapshot[vX.Y]`
    - `draft`（当前 `rule_set` + `working_draft` 投影）
- Restore / Rollback：
  - 将目标版本的规则集合覆盖回 `rule_set`
  - bump `baseline_version`（形成新版本，而不是回写老版本）
  - revision +1

### 3.3 明确：哪些是领域状态，哪些是持久化便利结构
- 领域状态（当前阶段视角）：`baseline_version`、`rule_set`、`working_draft`
- 持久化便利结构（为 UI/审计/回滚提供）：`baseline_version_snapshot`、`version_history_meta`

后续若进入 DB 化或更强状态建模阶段，应优先重新审视“快照存储策略”和“版本元数据策略”。

## 4. 新增持久化字段的规则
- 新字段必须明确标注属于：
  - Domain state
  - Persistence payload / representation detail
  - Infra artifact / observation
- 若属于 payload，必须能在不破坏 Repository Contract 的前提下演进（例如默认值、迁移策略在 repo 内部完成）

