# AI Handoff Document

> 此文档供 AI 代理（或新开发者）快速接手项目时参考。
> 更新时间：2026-04-12（Phase A 完成，Usage Simulation 体系建立）

---

## 0. 开发模式：Usage-Driven Optimization

**当前项目已进入 L4 稳定期。开发模式从"建设驱动"切换为"真实使用驱动优化"。**

### 当前开发原则

1. **Pain 驱动**：所有开发工作必须来自 `USAGE_PAINLOG.md` 中的真实痛点，禁止凭预感添加功能
2. **最小变更**：每次只解决一个 Pain，不做附带重构
3. **测试守卫**：任何修改必须保证 272+ 现有测试通过，不得引入回归
4. **验证闭环**：修复后必须在 `ITERATION_REVIEW.md` 中记录验证结果

### 新功能准入标准（Feature Gate）

新功能/增强被接受的条件：

- [ ] 在 `USAGE_PAINLOG.md` 中有 Pain Score ≥ 10 的记录
- [ ] Pain 经至少 2 次真实使用触发（非一次性偶遇）
- [ ] 无 Pain Log 记录 → 不接受

### Pain 驱动迭代机制

```
1. 真实使用中发现摩擦 → 记录到 USAGE_PAINLOG.md
2. 每轮迭代审视 → ITERATION_REVIEW.md（选 Top Pain）
3. 排期到 ROADMAP.md Active 列
4. 开发 + 测试
5. 下一轮迭代验证 Pain 是否消除
```

### 禁止提前做的事项（过度工程）

- ❌ 不因"可能有用"添加 API 端点
- ❌ 不因"代码不够优雅"做无 Pain 驱动的重构
- ❌ 不提前引入 PostgreSQL / RBAC / 审批流（见 ROADMAP Future Triggers）
- ❌ 不在无 Pain 支撑时优化性能、bundle 体积
- ❌ 不新增"Nice to Have"功能到 Backlog

---

## 1. 项目一句话定位

**Topo-Cable-Checker = 规则治理工作台（Rule Governance Workbench）**
用于编辑、校验、版本化、Diff、发布和回滚拓扑线缆校验规则的个人开发者工具。

**当前成熟度：L4.0（稳固）** — 0 伪实现 + 272 测试通过 + Deep Diff 递归比较 + 完整 Rule Set Rollback + Save Draft 真实持久化 + Executor 全覆盖测试 + Usage Simulation 体系

---

## 2. 技术栈速查

| 层 | 技术 | 关键文件 |
|----|------|---------|
| 前端 | React + TypeScript + Ant Design + useReducer 状态机 | `frontend/src/` |
| API 层 | FastAPI + Pydantic DTO + 全局异常处理 + Request ID | `src/presentation/api/` |
| 应用层 | 12 个 Service 按职责拆分 | `src/application/` |
| 领域层 | RuleCompiler + 4 Executor + 规则目录系统 | `src/domain/` |
| 基础设施层 | JSON 文件持久化 + 原子写入 + Rolling Backup + 损坏检测 + **Schema Migration (v0→v1.0→v1.1→v1.2)** | `src/infrastructure/repository.py` |
| 横切层 | RotatingFileHandler 日志 / ErrorCode 异常 / config / ids / time | `src/crosscutting/` |

---

## 3. 启动方式

### 后端
```bash
# Windows PowerShell
python -m uvicorn src.presentation.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端
```bash
cd frontend
npm install
npm run dev
# 默认连接真实后端 (http://localhost:8000/api)
# 如需 Mock 模式，设置 VITE_USE_MOCK_API=true
```

### 前端构建验证
```bash
cd frontend
npx tsc --noEmit    # 类型检查 — 应 0 errors
npm run build       # vite build — 应成功生成 dist/
```

### 环境变量
- `VITE_USE_MOCK_API`：前端 Mock/Real API 切换（**默认 `false` → Real API**；设为 `true` 启用 Mock）
- `VITE_API_BASE_URL`：后端 API 地址（默认 `/api`，开发时建议 `http://localhost:8000/api`）
- `CHECKTOOL_BASE_DIR`：数据目录覆盖（默认项目根目录）

---

## 4. P0+P1.0+P1.1 修复后的新增基础设施

### 4.1 日志系统
- **位置**：`logs/app.log`
- **轮转**：单文件 ≤5MB，保留 3 个备份（总计 ~20MB）
- **格式**：`时间 - 模块名 - 级别 - 消息`
- **关键记录**：Persistence 异常、Executor 异常、API 调用（含 request_id）

### 4.2 数据备份
- **位置**：`data/backups/`
- **策略**：每次 `_write_json` 前自动备份，保留最近 5 份
- **格式**：`{filename}.bak.{timestamp}`
- **恢复**：`_read_json` 检测到 JSON 损坏时自动从最近备份恢复
- **损坏文件保留**：损坏的原始文件重命名为 `{filename}.corrupted.{timestamp}.json`

### 4.3 错误码体系
- **定义**：`src/crosscutting/errors/exceptions.py` 中的 `ErrorCode` 类
- **范围**：P1xxx（持久化）、D2xxx（领域）、I3xxx（基础设施）、A4xxx（应用）、X9000（未知）
- **新增**：P1007（Schema Migration）、P1008（Schema Incompatible）
- **异常层级**：`CheckToolBaseError` → `PersistenceError` / `DomainError` / `ConfigurationError` / `PersistenceSchemaError`
- **API 响应**：所有异常统一返回 `{error_code, message, request_id, details}`

### 4.4 Request ID 追踪
- **生成**：`RequestIdMiddleware` 自动生成 UUID4 或接受 `X-Request-ID` header
- **传播**：Response Header `X-Request-ID` + Error Body `request_id` + 日志中 `request_id=xxx`
- **用途**：任意错误可通过 request_id 在日志中全链路定位

### 4.5 Publish Validation Gate
- **机制**：publish 端点委托给 `RulePublishWorkflowService.publish_draft()`
- **流程**：Convert DTO → RuleDraftView → compile_draft_preview() → 验证通过才持久化
- **阻断保证**：编译/校验失败时 `publish_success=False`，返回 `blocked_issues`
- **Body 绑定**：`PublishRequestDTO`（rule_id, rule_type, target_type, severity, params）确保请求体正确绑定
- **数据真实性**：提交的 draft_data 与最终持久化数据一致，测试已证明

### 4.6 Diff 治理语义增强
- **DiffRuleDTO.field_changes**：per-field before/after（`[{field_name, old_value, new_value}]`）
- **DiffRuleDTO.human_summary**：人类可读一行摘要（e.g. `"severity: "warning" → "error""`）
- **DiffSourceTargetDTO.human_readable_summary**：全局变更摘要（e.g. `"1 rule(s) added, 2 rule(s) modified (severity, params)"`）
- **前端展示**：DiffPanel/RightPanel/DiffView 展示 field-level before/after 对比

### 4.7 Schema Version & Migration Safety
- **当前 schema version**：`BASELINES_SCHEMA_VERSION = "1.2"`
- **存储位置**：`baselines.json` 顶层 `__schema_version__` 字段
- **读取逻辑**：
  - 无 `__schema_version__` → 视为 v0（pre-schema），自动迁移
  - 可迁移版本 → step-by-step 迁移到当前版本
  - 数据版本 > 代码版本 → `PersistenceSchemaError`（明确拒绝）
  - 无迁移路径 → `PersistenceSchemaError`（明确拒绝）
- **迁移注册表**：`BASELINES_MIGRATIONS` dict，key = (from, to)
- **写入逻辑**：`BaselineRepository.save()` 自动 stamp `__schema_version__`
- **新增异常**：`PersistenceSchemaError`（error codes P1007/P1008）

### 4.8 Save Draft 持久化
- **服务**：`RuleDraftSaveService`（save_draft / load_draft / clear_draft）
- **存储**：`BaselineProfile.working_draft` 字段，通过 `BaselineRepository` 持久化到 `baselines.json`
- **严格语义**：`None` = 无草稿，`dict` = 有草稿，`{}` 禁止用于表示"无草稿"
- **API 端点**：
  - `POST /api/rules/draft/save` — 保存草稿（无编译门，invalid draft 可保存）
  - `GET /api/rules/draft/{baseline_id}` — 加载草稿（用于自动恢复）
  - `DELETE /api/rules/draft/{baseline_id}` — 清除草稿
- **自动清除**：Publish 成功后 `working_draft` 自动设为 `None`
- **前端改动**：
  - `handleSaveDraft` 从 setTimeout 改为真实 API 调用
  - `switchNavContext` 进入 draft 时先调用 loadDraft 自动恢复
  - 新增 `DRAFT_SAVE_SUCCESS` / `DRAFT_SAVE_FAILED` / `DRAFT_LOADED` reducer actions

### 4.9 Executor 测试体系
- `test_threshold_executor.py`：35 测试，覆盖 7 个算子 + count/distinct_count + threshold_profile vs inline
- `test_single_fact_executor.py`：20 测试，覆盖 field_equals/regex_match/missing_value
- `test_group_consistency_executor.py`：19 测试，覆盖 dominant value/parameter resolution/edge cases

### 4.10 Deep Diff 递归比较
- **函数**：`deep_diff(old_obj, new_obj, path)` — 递归比较 dict/list/scalar/type mismatch
- **返回**：`List[DeepDiffChange]`，每项含 `field_path`（dot-notation）、`old_value`、`new_value`
- **集成**：`diff_versions()` 使用 `deep_diff()` 替代浅层 key 比较，`BaselineDiffRuleChangeView.deep_changes` 存储完整递归差异
- **向后兼容**：`changed_fields` 从 `deep_changes` 提取顶层字段名

### 4.11 Rollback 完整 Rule Set
- **字段**：`RollbackCandidateDTO.rule_set` — 完整历史版本规则集
- **向后兼容**：`draft_data` 仍保留第一条规则，供单规则编辑 UX 使用
- **版本区分**：`_get_rule_set_for_version()` 返回 `None`（版本不存在）vs `{}`（0 条规则）

### 4.12 Usage Simulation & Stress Testing 体系
- **计划文档**：`docs/USAGE_SIMULATION_PLAN.md` — 5 类场景（A~E），32 个测试场景
- **数据集**：`samples/usage_simulation/` — 5 个标准化 JSON 数据集
  - `dataset_A_single_rule.json` — 单规则正确性（10 场景）
  - `dataset_B_multi_rule.json` — 多规则交互（5 场景）
  - `dataset_C_boundary.json` — 边界与极端输入（7 场景）
  - `dataset_D_workflow.json` — Draft/Publish/Version 工作流压测（5 场景）
  - `dataset_E_api_stress.json` — API 端点压力测试（5 场景）
- **测试清单**：`docs/USAGE_TEST_CHECKLIST.md` — 手动/半自动验证清单
- **与自动化测试的关系**：SIM 数据集补充自动化测试，提供手动验证的标准化输入
- **执行方式**：
  - A/B/C 类：`pytest tests/test_*_executor.py -v`（已自动化覆盖）
  - D 类：`pytest tests/test_draft_save_api.py -v`（已自动化覆盖）
  - E 类：需启动 API 服务 + ab/locust 压测工具

---

## 5. 核心数据流

```
用户进入 baseline 编辑上下文
  → GET /api/rules/draft/{baseline_id} (自动恢复)
  → 有草稿 → 填充 draftData (DRAFT_LOADED) / 无草稿 → 默认模板

用户编辑 Draft JSON
  → 前端 UPDATE_DRAFT (pageReducer)
  → 点击保存 → POST /api/rules/draft/save (真实持久化)
    → RuleDraftSaveService.save_draft() → BaselineRepository.save() → baselines.json
    → 成功 → DRAFT_SAVE_SUCCESS (dirty=false) / 失败 → DRAFT_SAVE_FAILED (dirty保持)
  → 点击校验 → POST /api/rules/draft/validate
  → RuleCompiler.compile() → CompiledRule / RuleCompileError
  → 前端 VALIDATION_SUCCESS / VALIDATION_FAILED
  → 点击发布 → POST /api/rules/publish/{baseline_id}
  → RulePublishWorkflowService.publish_draft()
    → compile_draft_preview() → 验证门
    → 验证失败 → 返回 blocked_issues → 前端 PUBLISH_BLOCKED
    → 验证通过 → snapshot old → bump version → clear working_draft → save → 前端 PUBLISH_SUCCESS
  → 查看 Diff → GET /api/baselines/{id}/diff
  → RuleBaselineHistoryService.diff_versions() → deep_diff() 递归比较
  → DiffRuleDTO with deep_changes (dot-path field_changes) + human_summary
  → 前端展示 per-field before/after + 全局变更摘要
  → 回滚 → POST /api/rules/rollback
  → 返回完整 rule_set (B2) + draft_data (向后兼容)
```

---

## 6. 已修复的致命 Bug（P0 + P1.0 + P1.1 + Phase A）

| # | Bug | 修复 | 位置 |
|---|-----|------|------|
| 1 | topology_executor `rule_def` NameError | → `compiled_rule.params.get()` | `src/domain/executors/topology_executor.py` |
| 2 | threshold_executor `rule_def` NameError | → `compiled_rule.target.get()` | `src/domain/executors/threshold_executor.py` |
| 3 | JSON 损坏静默返回 `{}` | Fail-fast + 异常 + 备份恢复 | `src/infrastructure/repository.py` |
| 4 | 无数据备份 | Rolling backup (5 copies) | `src/infrastructure/repository.py` |
| 5 | 仅 StreamHandler 日志 | + RotatingFileHandler | `src/crosscutting/logging/logger.py` |
| 6 | API 裸 traceback | 全局异常处理 + 统一 JSON | `src/presentation/api/error_handler.py` |
| 7 | 无请求追踪 | RequestIdMiddleware | `src/presentation/api/error_handler.py` |
| 8 | publish 端点 Body 未绑定 | PublishRequestDTO + RulePublishWorkflowService | `src/presentation/api/routers/rules.py` |
| 9 | 验证不阻断发布 | RuleCompiler 编译校验门 | `src/presentation/api/routers/rules.py` |
| 10 | 前端默认 Mock API | VITE_USE_MOCK_API=false 为默认 | `frontend/src/api/client.ts` |
| 11 | 前端 tsc 构建失败 | 移除无效 ignoreDeprecations + 修复 25+ TS 类型错误 | `frontend/tsconfig.json + 多个组件` |
| 12 | Diff 只显示字段名堆叠 | field_changes (before/after) + human_summary | `src/presentation/api/dto_models.py + baselines.py` |
| 13 | JSON 持久化无 schema 版本 | schema_version + migration registry | `src/infrastructure/repository.py` |
| 14 | handleSaveDraft 仅 setTimeout 模拟 | 真实 API + RuleDraftSaveService + working_draft 持久化 | `App.tsx + rules.py + rule_draft_save_service.py` |
| 15 | Diff 仅浅层 key 比较 | deep_diff() 递归比较 + DeepDiffChange dot-path | `rule_baseline_history_service.py` |
| 16 | Rollback 仅取第一条规则 | RollbackCandidateDTO 增加 rule_set 字段 + _get_rule_set_for_version 返回 None | `rules.py + rule_baseline_history_service.py` |
| 17 | 空 rule_set 回滚误报"版本不存在" | is None 替代 not 判断 | `rule_baseline_history_service.py` |
| 18 | Rollback Preview Diff 方向误导 | rollback_effect_diff 专用 API + 回滚确认页使用 rollback effect diff | `src/presentation/api/routers/baselines.py + frontend/src/components/CenterViews/RollbackConfirmView.tsx` |

---

## 7. 已知问题与风险

> 完整风险列表见 `docs/PROJECT_STATE_SNAPSHOT.yaml` → remaining_risks

| # | 问题 | 严重度 | 来源 | 状态 |
|---|------|--------|------|------|
| 1 | tasks.json 无 schema 版本迁移 | P2 | RISK-003 | Backlog |
| 2 | 根目录残留一次性脚本 | P2 | RISK-004 | Parking Lot |
| 3 | 前端 bundle >500KB | P2 | RISK-007 | Parking Lot |
| 4 | GroupConsistencyExecutor 缺配置静默 false negative | P3 | RISK-008 | Closed |
| 5 | RuleEditor JSON 手工编辑易出错 | High | PAIN-001 | Active |
| 6 | 回滚确认只展示第一条规则 | Critical | PAIN-002 | Active |

---

## 8. 预存失败测试

**`tests/test_run_core.py::test_cli_run_without_optional`** — 失败

- **原因**：CLI 子进程测试，task create 成功但 task 状态非 "ready"，导致 run 命令返回错误码 1
- **错误信息**：`Task {id} is not ready to check`
- **是否 P0/P1.0/P1.1 引入**：否
- **建议**：P1 阶段修复 task lifecycle 状态机或更新测试 fixture

---

## 9. 架构约束（勿违反）

1. **DIP 原则**：`src/domain/interfaces.py` 定义接口，基础设施层实现。**领域层不得 import 基础设施层**。
2. **原子写入**：所有 JSON 持久化必须通过 `_write_json()`（备份 → temp → os.replace）。
3. **Fail-Fast**：`_read_json()` 不允许静默吞掉损坏数据，必须抛出 `PersistenceCorruptionError`。
4. **状态机守卫**：前端 `pageReducer` 每个 case 都有状态守卫，新加 Action 必须同步。
5. **DTO 隔离**：API 入参出参必须经过 Pydantic DTO 验证，不得直接暴露领域模型。
6. **错误码**：新增异常必须分配 `ErrorCode`，不得使用裸 `Exception`。
7. **Validation Gate**：publish 必须经过 RuleCompiler 编译校验，不得绕过。
8. **Schema Version**：修改 baselines.json 数据结构时，必须 bump `BASELINES_SCHEMA_VERSION` 并添加迁移函数。
9. **Diff DTO 统一**：前端 Diff 展示必须使用 `rules[]` + `change_type` 过滤，不得假设 `added_rules/removed_rules/modified_rules` 属性存在。
10. **Draft 语义严格**：`working_draft` 字段使用 `None` 表示无草稿，禁止使用 `{}` 空字典表示"无草稿"。
11. **Draft Save 无编译门**：保存草稿不做 compile 验证，允许保存 invalid draft；但 publish 验证门仍阻断 invalid draft 发布。
12. **Pain Gate**：新增功能/增强必须有 `USAGE_PAINLOG.md` 中 Pain Score ≥ 10 的记录，否则不接受（Usage-Driven 约束）。
13. **版本不存在 vs 空数据**：`_get_rule_set_for_version()` 返回 `None` 表示版本不存在，`{}` 表示 0 条规则，不得混淆（B2 约束）。

---

## 10. 测试方式

```bash
# 运行所有测试（排除已知的 pre-existing 失败）
python -m pytest tests/ --ignore=tests/test_run_core.py -v

# Phase B 新增：Deep Diff 递归比较测试
python -m pytest tests/test_deep_diff.py -v

# Phase B 新增：Rollback 完整性测试
python -m pytest tests/test_rollback_completeness.py -v

# Phase A 新增：Draft Save API 测试
python -m pytest tests/test_draft_save_api.py -v

# Phase A 新增：Executor 独立测试
python -m pytest tests/test_threshold_executor.py tests/test_single_fact_executor.py tests/test_group_consistency_executor.py -v

# P1.0 新增：publish 验证门测试
python -m pytest tests/test_publish_validation_gate.py -v

# P1.1 新增：Diff 治理语义 + Schema Migration 测试
python -m pytest tests/test_diff_governance.py tests/test_schema_migration.py -v

# API 集成测试
python -m pytest tests/test_api_integration.py -v

# 前端构建验证
cd frontend && npx tsc --noEmit && npm run build
```

---

## 11. 文档索引

| 文档 | 用途 |
|------|------|
| `docs/USAGE_PAINLOG.md` | **Pain Log** — 真实使用痛点记录，驱动所有迭代优先级 |
| `docs/ITERATION_REVIEW.md` | **迭代审视** — 每轮迭代的审视记录与验证结果 |
| `docs/ROADMAP.md` | **路线图** — Usage-Driven 结构（Active / Backlog / Parking Lot / Future Triggers） |
| `docs/USAGE_SIMULATION_PLAN.md` | **仿真测试计划** — 5 类场景（A~E），32 个测试场景定义 |
| `docs/USAGE_TEST_CHECKLIST.md` | **仿真测试清单** — 手动/半自动验证检查表 |
| `docs/PROJECT_STATE_SNAPSHOT.yaml` | 项目状态快照（机器可读） |
| `docs/AI_HANDOFF.md` | 本文档 — AI/新开发者接手指南 |
| `docs/CAPABILITY_AUDIT.md` | 能力真实性审计报告 |
| `docs/RULE_LANGUAGE_SPEC.md` | 规则语言规范 |
| `docs/PROJECT_POSITIONING.md` | 产品定位与演进决策 |

**数据集索引**：

| 数据集 | 位置 | 用途 |
|--------|------|------|
| `samples/usage_simulation/dataset_A_single_rule.json` | 单规则正确性验证 | 10 场景 |
| `samples/usage_simulation/dataset_B_multi_rule.json` | 多规则交互验证 | 5 场景 |
| `samples/usage_simulation/dataset_C_boundary.json` | 边界与极端输入 | 7 场景 |
| `samples/usage_simulation/dataset_D_workflow.json` | Draft/Publish 工作流压测 | 5 场景 |
| `samples/usage_simulation/dataset_E_api_stress.json` | API 端点压力测试 | 5 场景 |
